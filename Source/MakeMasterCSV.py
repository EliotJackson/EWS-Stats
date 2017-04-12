import pandas as pd
import re
import os
import glob
import numpy as np
import RootsAndRainScrape

root_ews_dir = r'C:\EWSData'


def make_master_ews(root_dir=root_ews_dir):
    """
    Make a master list off all EWS results
    :param root_dir: Directory to walk and export master list to
    :return: Export CSV
    """
    columns = ["year", "round_num", "round_loc", "finish_position", "overall_position", "name", "city", "country",
               "sponsor", "factory", "stage1_time", "stage1_position", "stage2_time", "stage2_position", "stage3_time",
               "stage3_position", "stage4_time", "stage4_position", "stage5_time", "stage5_position", "stage6_time",
               "stage6_position", "stage7_time", "stage7_position", "stage8_time", "stage8_position", "finish_time",
               "time_behind", "penalties", "dnf", "dns", "dsq", "out_at_stage"]

    all_files = glob.glob(os.path.join(root_ews_dir, '**', '*.csv'))

    df_from_files = [pd.read_csv(file) for file in all_files]

    master_df = pd.DataFrame(pd.concat(df_from_files))
    master_df.drop(master_df.columns[0], axis=1, inplace=True)

    master_df.sort_values(['year', 'round_num'], inplace=True)
    master_df.reset_index(inplace=True)
    master_df.drop(master_df.columns[0], axis=1, inplace=True)


    def fill_missing_and_clean(df_to_fill):

        rider_list = df_to_fill.groupby('name').sum().index.tolist()
        year_list = ['2013', '2014', '2015', '2016', '2017']
        round_list = ['1', '2', '3', '4', '5', '6', '7', '8']
        stage_list = ['1', '2', '3', '4', '5', '6', '7', '8']

        def to_seconds(race_time):
            # Convert stagetime to seconds
            race_time = str(race_time)

            # Check for nan
            if not any(c.isalpha() for c in race_time):
                if race_time.count(':') > 1:
                    mins = int(race_time.split(':')[1])
                    hours = int(race_time.split(':')[0])
                else:
                    mins = int(race_time.split(':')[0])
                    hours = 0

                seconds = int(race_time.split(':')[-1].split('.')[0])
                ms = float('.' + race_time.split('.')[1])

                time_in_seconds = hours * 3600 + mins * 60 + seconds + ms
            else:
                time_in_seconds = np.nan
            return float(time_in_seconds)

        def add_columns():
            # Convert the stagetime to seconds
            for stage_num in stage_list:
                df_to_fill.loc[:, 'stage' + stage_num + '_seconds'] = \
                    df_to_fill['stage' + stage_num + '_time'].apply(lambda x: to_seconds(x))

            # Get the average of the top 10 fastest stage times and add a new gap item for each rider based on
            # The average time - their time

            for year in year_list:
                for rnd in round_list:
                    for stage in stage_list:
                        current_stage_seconds = 'stage' + stage + '_seconds'
                        print( year, rnd, stage)
                        current_top10 = df_to_fill.query('year == ' + year + ' and round_num == ' + rnd)[current_stage_seconds].nsmallest(10).index.tolist()

                        current_round = df_to_fill.query('year == ' + year + ' and round_num == ' + rnd).index

                        if not all(np.isnan(df_to_fill.loc[current_round, current_stage_seconds])):
                            # Time behind avg of top 10
                            df_to_fill.loc[current_round, 'stage' + stage + '_gap'] = (
                                df_to_fill.loc[current_round, current_stage_seconds]
                                - df_to_fill.loc[
                                    current_top10, current_stage_seconds].mean())

                            # Avg time of top 10
                            df_to_fill.loc[current_round, 'stage' + stage + '_top10avg'] \
                                = df_to_fill.loc[current_top10, current_stage_seconds].mean()

        def fill_missing_sponsors(missing_df):
            """
            Sometime the sponsors aren't recorded for a race. We assume a rider is under a year contract and
            replace un-recorded races with the sponsor that has ocurred most of the year.


            with sponsor NaN's replaced and factory column added
            :param missing_df: Dataframe to replace
            :return: Dataframe with sponsor NaN's replaced and
            """

            print('Filling Missing Sponsors...')

            for rider in rider_list:

                # Make sure the rider has done at least one race where sponsors were recorded/the rider was sponsored
                years_raced_with_sponsors = missing_df.loc[(missing_df['name'] == rider) &
                                                           (missing_df['sponsor'].notnull()),
                                                           'year'].drop_duplicates().tolist()

                for year in years_raced_with_sponsors:

                    full_sponsor_list = missing_df.loc[(missing_df['year'] == year) & (missing_df['name'] == rider),
                                                       'sponsor']
                    sponsor_list_mode = full_sponsor_list[missing_df['sponsor'].notnull()].value_counts().index[0]

                    # Replace NaN's with the mode
                    filled_sponsor_list = missing_df.loc[(missing_df['year'] == year) & (missing_df['name'] == rider),
                                                         'sponsor'].fillna(sponsor_list_mode)

                    # Check to see if rider was on a factory team that season
                    missing_df.loc[(missing_df['year'] == year) & (missing_df['name'] == rider), 'factory'] \
                        = any(['factor' in x.lower() for x in filled_sponsor_list])

                    # Replace all values with the mode and format text
                    missing_df.loc[(missing_df['year'] == year) & (missing_df['name'] == rider), 'sponsor'] \
                        = filled_sponsor_list.apply(lambda x: x.replace(x, sponsor_list_mode.title()))
            missing_df['sponsor'].fillna('No Sponsor', inplace=True)
            missing_df['factory'].fillna(False, inplace=True)

            return missing_df

        def fill_missing_hometown(missing_df):
            """
            Sometime the hometows aren't recorded for a race. We assume a rider is always from the same hometown
            replace un-recorded races with the a city and country or just country if thats all thats available

            :param missing_df: Dataframe to replace
            :return: Dataframe w
            """

            print('Filling Missing Hometown...')

            country_code_dict = {'ITA': 'Italy', 'USA': 'United States', 'UK': 'United Kingdom', 'GB': 'United Kingdom',
                                 'GBR': 'United Kingdom', 'FRA': 'France', 'CRC': 'Costa Rica', 'BRA': 'Brazil',
                                 'GE': 'Georgia',
                                 'CHI': 'Chile', 'COL': 'Colombia', 'SW': 'Swaziland', 'ESP': 'Spain', 'FIN': 'Finland',
                                 'AUT': 'Austria', 'CAN': 'Canada', 'BEL': 'Belgium', 'AND': 'Andorra',
                                 'NZL': 'New Zealand',
                                 'SUI': 'Switzerland', 'GER': 'Germany', 'SWE': 'Sweden', 'AUS': 'Australia',
                                 'POR': 'Portugal',
                                 'CHE': 'Switzerland', 'MON': 'Mongolia', 'DEN': 'Denmark', 'IRL': 'Ireland',
                                 'SLO': 'Slovenia', 'ISR': 'Israel', 'CZE': 'Czech Republic', 'ZAF': 'South Africa',
                                 'SWI': 'Switzerland', 'SVN': 'Slovenia', 'DEU': 'Germany', 'PRT': 'Portugal',
                                 'SM': 'San Marino', 'RU': 'Russia', 'DNK': 'Denmark', 'CHL': 'Chile', 'NOR': 'Norway',
                                 'tAUS': 'Australia', 'oUSA': 'United States', 'wCAN': 'Canada',
                                 'Austraia': 'Australia',
                                 'Czechia': 'Czech Republic'}

            for rider in rider_list:


                country = ''
                city = ''

                # Make sure the rider has done at least one race where sponsors were recorded/the rider was sponsored
                rider_hometown = missing_df.loc[(missing_df['name'] == rider) &
                                                (missing_df['country'].notnull()),
                                                'country'].drop_duplicates().tolist()
                for location in rider_hometown:
                    if ',' in location:
                        # City, Country
                        city = location.split(',')[0]
                        country = location.split(', ')[1]

                    if not location.isupper() and not location.islower() and ',' not in location:
                        # Country
                        country = location

                    if location.isupper() and country == '':
                        # Country Code or UCI Code i.e. SWE SWE.NEEA.1980
                        country_code = re.findall('([A-Z]+)', location)[0]
                        country = country_code

                country = country_code_dict.get(country, country)

                missing_df.loc[missing_df['name'] == rider, 'country'] = country
                missing_df.loc[missing_df['name'] == rider, 'city'] = city

            return missing_df

        def fill_missing_round_country(missing_df):

            # Add the country to the round location

            round_loc_dict = {"Val d'Allos": 'France', 'Les Deux Alpes': 'France', 'Winter Park, CO': 'United States',
                              'Whistler, BC': 'Canada', "Val d'Isere": 'France', 'Finale Ligure': 'Italy',
                              'Nevados de Chillan Bike Park': 'Chile', 'Glentress': 'Scotland', 'Valloire': 'France',
                              'La Thuille': 'Italy', 'Carrick, Co. Wicklow': 'Ireland', 'Samoens': 'France',
                              'Zona Zero Ainsa-Sobrarbe': 'Spain', 'Corral, Valdiva': 'Chile',
                              'Cerro Catedral': 'Argentina',
                              'Snowmass Village, CO': 'United States', 'Valberg, Guillaumes': 'France',
                              'Rotorua': 'New Zealand'}

            def fill_country(x):
                d = round_loc_dict.get(x, x)
                new_loc = x
                if x != d:
                    new_loc = x + ', ' + d
                return new_loc

            missing_df['round_loc'] = missing_df.loc[:, 'round_loc'].apply(fill_country)

            return missing_df


        df_to_fill = fill_missing_hometown(df_to_fill)
        df_to_fill = fill_missing_sponsors(df_to_fill)
        df_to_fill = fill_missing_round_country(df_to_fill)
        df_to_fill = df_to_fill[columns]
        add_columns()

        return df_to_fill

    master_df = fill_missing_and_clean(master_df)
    master_df.to_csv(os.path.join(root_dir, 'Master.csv'), encoding='utf-8')



make_master_ews()
