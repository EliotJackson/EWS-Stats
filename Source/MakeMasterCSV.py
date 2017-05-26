import pandas as pd
import re
import os
import glob
import numpy as np
import pickle
import datetime as datetime

#pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_rows', -1)

root_ews_dir = r'C:\EWSData'

# ToDo: Compare cumulative stage time to finish time

def make_master_ews(root_dir=root_ews_dir):
    """
    Make a master list off all EWS results
    :param root_dir: Directory to walk and export master list to
    :return: Export CSV
    """

    two_day_races = [[2013, 1], [2013, 2], [2013, 3], [2013, 4], [2013, 5], [2013, 6],
                     [2014, 1], [2014, 2], [2014, 3], [2014, 4], [2014, 5], [2014, 6], [2014, 7],
                     [2015, 3], [2015, 4], [2015, 5], [2015, 7], [2015, 8],
                     [2016, 1], [2016, 2], [2016, 4], [2016, 5], [2016, 7], [2016, 8],
                     [2017, 3], [2017, 5], [2017, 6], [2017, 8]]


    columns = ["year", "round_num", "round_loc", "finish_position", "overall_position", "name", "city", "country",
               "sponsor", "factory", "stage1_time", "stage1_position", "stage2_time", "stage2_position", "stage3_time",
               "stage3_position", "stage4_time", "stage4_position", "stage5_time", "stage5_position", "stage6_time",
               "stage6_position", "stage7_time", "stage7_position", "stage8_time", "stage8_position", "finish_time",
               "time_behind", "penalties", "dnf", "dns", "dsq", "out_at_stage", "num_stages"]

    all_files = glob.glob(os.path.join(root_ews_dir, '**', '*.csv'))

    df_from_files = [pd.read_csv(file) for file in all_files]

    master_df = pd.DataFrame(pd.concat(df_from_files))
    master_df.drop(master_df.columns[0], axis=1, inplace=True)

    master_df.sort_values(['year', 'round_num'], inplace=True)
    master_df.reset_index(inplace=True)
    master_df.drop(master_df.columns[0], axis=1, inplace=True)
    master_df.drop_duplicates(inplace=True)


    def fill_missing_and_clean(df_to_fill):

        # Account for first race where it was Saturday ad Sunday. Fix this eventually.
        df_to_fill['num_stages'].replace(0, 2, inplace=True)
        print(df_to_fill['stages_raced'])
        p = df_to_fill.apply(lambda x: print(max(x['stages_raced'].split(', ')), x['round_loc'], x['year']), axis=1)
        #ToDo: Get EWS Site Stages raced working

        rider_list = df_to_fill.groupby('name').sum().index.tolist()
        year_list = ['2013', '2014', '2015', '2016', '2017']
        round_list = ['1', '2', '3', '4', '5', '6', '7', '8']
        stage_list = ['1', '2', '3', '4', '5', '6', '7', '8']
        def to_delta1(race_time):
            """
            Convert any time we have in out dataframe to timedelta format

            :param race_time: Time to convert
            :return: Timedelta
            """

            race_time = str(race_time)

            if race_time == 'nan':
                race_time = '99999'

            # Check for 'Not Raced', if we get it set timedelta to 1 day to for easy identification
            # NaN values are set to 0 timedelta for identification
            if not any(character.isalpha() for character in race_time):
                if race_time.count(':') > 1:
                    # '2:43:20.334'
                    mins = int(race_time.split(':')[1])
                    hrs = int(race_time.split(':')[0])
                    secs = int(race_time.split(':')[-1].split('.')[0])
                    ms = float(race_time.split('.')[1])
                else:
                    if race_time.count(':') == 1:
                        # '43:20.334'
                        hrs = 0
                        mins = int(race_time.split(':')[0])
                        secs = int(race_time.split(':')[-1].split('.')[0])
                        ms = float(race_time.split('.')[1])
                    elif (race_time.count(':') == 0) & (race_time.count('.') == 1):
                        # '20.334'
                        hrs = 0
                        mins = 0
                        secs = int(race_time.split('.')[0])
                        ms = float(race_time.split('.')[1])
                    else:
                        # '0' or penalty
                        hrs = 0
                        mins = 0
                        secs = int(race_time)
                        ms = 0

                delta = datetime.timedelta(hours=hrs, minutes=mins, seconds=secs, milliseconds=ms)
                print(delta)
            else:

                delta = datetime.timedelta(1)

            return delta

        def to_delta(race_time):
            """
            Convert any time we have in out dataframe to timedelta format

            :param race_time: Time to convert
            :return: Timedelta
            """

            race_time = str(race_time)

            # Check for 'Not Raced', if we get it set timedelta to 1 day to for easy identification
            # NaN values are set to 0 timedelta for identification
            if not any(character.isalpha() for character in race_time):
                if race_time.count(':') > 1:
                    # '2:43:20.334'
                    mins = int(race_time.split(':')[1])
                    hrs = int(race_time.split(':')[0])
                    secs = int(race_time.split(':')[-1].split('.')[0])
                    ms = race_time.split('.')[1]

                    # Incase we have a 2:04.1 situation
                    if len(ms) == 1:
                        ms = int(ms + '00')
                    elif len(ms) == 2:
                        ms = int(ms + '0')
                    else:
                        ms = int(ms)

                elif race_time.count(':') == 1:
                    # '43:20.334'
                    hrs = 0
                    mins = int(race_time.split(':')[0])
                    secs = int(race_time.split(':')[-1].split('.')[0])
                    ms = race_time.split('.')[1]

                    # In case we have a 2:04.1 situation
                    if len(ms) == 1:
                        ms = int(ms + '00')
                    elif len(ms) == 2:
                        ms = int(ms + '0')
                    else:
                        ms = int(ms)

                elif (race_time.count(':') == 0) & (race_time.count('.') == 1):
                    # '20.334'
                    hrs = 0
                    mins = 0
                    secs = int(race_time.split('.')[0])
                    ms = race_time.split('.')[1]

                    # In case we have a 2:04.1 situation
                    if len(ms) == 1:
                        ms = int(ms + '00')
                    elif len(ms) == 2:
                        ms = int(ms + '0')
                    else:
                        ms = int(ms)

                elif race_time == 'nan':
                    # Penalty or DNF
                    hrs = 0
                    mins = 0
                    secs = 0
                    ms = 0

                else:
                    # '0'
                    hrs = 0
                    mins = 0
                    secs = int(race_time)
                    ms = 0

                delta = datetime.timedelta(hours=hrs, minutes=mins, seconds=secs, milliseconds=ms)

            else:

                delta = datetime.timedelta(1)

            return delta


        def add_columns():
            """
            Add any extra features we need for analysis
            """
            df_to_fill.loc[:, 'overall_points'] = 0
            df_to_fill.loc[:, 'overall_time'] = datetime.timedelta(0)

            print('Converting to Timedelta...')
            # Convert any times we have to timedelta
            for stage_num in stage_list:
                df_to_fill.loc[:, 'stage' + stage_num + '_time'] = \
                    df_to_fill.loc[:, 'stage' + stage_num + '_time'].apply(lambda x: to_delta(x))
            df_to_fill.loc[:, 'finish_time'] = df_to_fill.loc[:, 'finish_time'].apply(lambda x: to_delta(x))
            df_to_fill.loc[:, 'time_behind'] = df_to_fill.loc[:, 'time_behind'].apply(lambda x: to_delta(x))
            df_to_fill.loc[:, 'penalties'] = df_to_fill.loc[:, 'penalties'].apply(lambda x: to_delta(x))


            print('Adding Gap and Average Time of Top 10 Columns...')
            '''
            Get the average of the top 10 fastest stage times and compute the time gap from that for each rider
            '''
            for stage in stage_list:
                current_stage = 'stage' + stage + '_time'
                top_10 = 'stage' + stage + '_top10avg'
                gap = 'stage' + stage + '_gap'

                top_10_times = df_to_fill.loc[df_to_fill[current_stage] != '00:00:00']\
                    .groupby(['year', 'round_num'])[current_stage].nsmallest(10).reset_index()

                df_to_fill.loc[:, top_10] = top_10_times.groupby(['year', 'round_num'])[current_stage]\
                    .transform(lambda x: np.mean(x))

                df_to_fill[top_10].fillna(datetime.timedelta(0), inplace=True)

                df_to_fill.loc[:, gap] = df_to_fill[current_stage] - df_to_fill[top_10]

            print('Rounds Raced')
            '''
            Rounds Raced
            '''
            # Add the two columns together with a space in the middle. Year is a number so we have to turn it into
            # a string (words) before we can add it. lambda is a funciton, its read like "for each item in name, add a
            # a space and add it to the corresponding item in year on axis 1 ( across)
            df_to_fill.loc[:, 'name_year'] = df_to_fill.apply(lambda x: x['name'] + ' ' + str(x['year']), axis=1)

            # Make our pivot table
            new_pivot = df_to_fill.pivot('name_year', 'round_num', 'round_num')

            '''
            round_num                      1    2    3    4    5    6    7    8
            name_year
            ??? DI PIERDOMENICO 2013     NaN  NaN  NaN  NaN  NaN  NaN  7.0  NaN
            Aaron BRADFORD 2013          NaN  NaN  NaN  4.0  5.0  NaN  7.0  NaN
            Aaron BRADFORD 2014          1.0  2.0  3.0  4.0  5.0  6.0  7.0  NaN
            Aaron BRADFORD 2015          NaN  NaN  NaN  NaN  NaN  6.0  NaN  NaN
            Aaron BRADFORD 2016          NaN  NaN  NaN  NaN  5.0  6.0  NaN  NaN
            '''

            # Apply applies whatever is in the ( ) to every row in the dataset
            # ','.join() joins items using a comma
            # x.dropna() drops all of the NaN values
            # astype(str) converts the numbers to "letters" so they can be joined to the commas
            # values gets the values in the cells
            # replace gets ride of the '.0'. This means it a float, or decimal type, we trned it into a string
            # which means we can replace letters with other letters (hacky :P)
            new_pivot = new_pivot.apply(lambda x: ','.join(x.dropna().astype(str).values).replace('.0', ''), axis=1)

            '''
            name_year
            ??? DI PIERDOMENICO 2013                   7
            Aaron BRADFORD 2013                    4,5,7
            Aaron BRADFORD 2014            1,2,3,4,5,6,7
            Aaron BRADFORD 2015                        6
            Aaron BRADFORD 2016                      5,6
            '''

            # The one line that took me forever to figure out :P
            # Map does the same thing as apply not sure the difference. Apply doesnt work here though.
            # Were saying wherever the original column has Aaron BRADFORD 2013, get the value for that in the new_pivot
            # Dataset
            df_to_fill.loc[:, 'rounds_raced'] = df_to_fill['name_year'].map(new_pivot)
            df_to_fill.drop('name_year', axis=1, inplace=True)

            print('Rounds Missed')
            '''
            Rounds Missed
            '''
            for year in year_list:
                year = int(year)
                rnd_list = df_to_fill.loc[df_to_fill['year'] == year, 'round_num'].unique()

                def get_not_raced(raced, rounds):
                    rounds_done = []
                    for done in rounds:
                        if len(raced) > 1:
                            if str(done) not in raced.split(','):
                                rounds_done.append(str(done))
                        else:
                            if str(done) not in raced:
                                rounds_done.append(str(done))

                    return ','.join(rounds_done)

                df_to_fill.loc[df_to_fill['year'] == year, 'not_raced'] = \
                    df_to_fill.loc[df_to_fill['year'] == year, 'rounds_raced'].apply(get_not_raced, rounds=rnd_list)

            print('Add Overall Points')
            '''
            Add Overall Points Per Race
            '''
            def get_round_points(x, series_year):
                if series_year == 2013:
                    if x == 1:
                        points = 600
                    elif x == 2:
                        points = 500
                    elif x == 3:
                        points = 420
                    elif x == 4:
                        points = 360
                    elif x == 5:
                        points = 300
                    elif x == 6:
                        points = 260
                    elif 6 < x <= 9:
                        points = 380 - x * 20
                    elif 9 < x <= 16:
                        points = 290 - x * 10
                    elif 16 < x <= 31:
                        points = 162 - x * 2
                    elif 31 < x <= 131:
                        points = 131 - x
                    else:
                        points = 0

                else:
                    if x == 1:
                        points = 500
                    elif x == 2:
                        points = 450
                    elif x == 3:
                        points = 420
                    elif x == 4:
                        points = 400
                    elif 4 < x <= 29:
                        points = 440 - x * 10
                    elif 29 < x <= 49:
                        points = 295 - x * 5
                    elif 49 < x < 100:
                        points = 99 - x
                    else:
                        points = 0

                return points

            # Get the year and finish position so we can use the correct points scale
            df_to_fill.loc[:, 'points'] = df_to_fill.loc[:, ['finish_position', 'year']].apply\
                (lambda x: get_round_points(x['finish_position'], x['year']), axis=1)

            '''
            # Non loop overall
            new_pivot2 = (df_to_fill.pivot('name_year', 'round_num', 'points')
                                    #.fillna(0)
                                    .apply(lambda x: x.cumsum(), axis=1))
            df_to_fill.drop('name_year', axis=1, inplace=True)

            #new_pivot2.apply(lambda x: x.cumsum(), axis=1)
            #new_pivot2 = new_pivot2.unstack().reset_index()

            #df_to_fill['over'] = df_to_fill['name_year_rnd'].map(new_pivot2[0])

            #print(new_pivot2)
            '''
            # No loop overall points
            #p = df_to_fill.groupby(['year', 'name'])['points'].apply(lambda x: x.cumsum())
            # print(p)


            print('Add Two-Day Race Info...')
            df_to_fill.loc[:, 'two_day_race'] = False

            def stages_per_day(x, day):
                # Get the number of stages per day by the number of total stages

                if x == 5:
                    day1 = 3
                elif x == 3:
                    day1 = 2
                elif x < 2:
                    day1 = 1
                else:
                    day1 = np.floor(x / 2)

                day2 = x - day1

                if day == 1:
                    return int(day1)
                else:
                    return int(day2)

            for race in two_day_races:
                yr = race[0]
                rnd = race[1]

                race_df = (df_to_fill['year'] == yr) & (df_to_fill['round_num'] == rnd)
                df_to_fill.loc[race_df, 'two_day_race'] = True

                df_to_fill.loc[race_df, 'day1'] = df_to_fill.loc[race_df, 'num_stages'].apply(
                        lambda x: stages_per_day(x, 1))
                df_to_fill.loc[race_df, 'day2'] = df_to_fill.loc[race_df, 'num_stages'].apply(
                        lambda x: stages_per_day(x, 2))

            print('Add Current Race Position Throughout Day...')
            # Add current position columns
            total_time = datetime.timedelta(0)

            def stage_not_raced(x):
                if x >= datetime.timedelta(1):
                    return datetime.timedelta(0)
                else:
                    return x

            # Add running total time for each rider throughout the day
            for stage_num in stage_list:
                total_time += df_to_fill['stage' + stage_num + '_time']
                df_to_fill.loc[:, 'time_after_' + stage_num] = total_time.apply(lambda x: stage_not_raced(x))

            # Add position columns after the time column
            for stage in stage_list:
                df_to_fill.insert(df_to_fill.columns.get_loc('time_after_' + stage) + 1,
                                  'position_after_' + stage, df_to_fill.index)

            for year in year_list:
                print('For', year)

                overall_time_df = pd.DataFrame(datetime.timedelta(0), rider_list, ['overall_time'])
                overall_points_df = pd.DataFrame(0, rider_list, ['overall_points'])

                for rnd in round_list:
                    print('Round',rnd)

                    '''
                    Get series points and series overall time.
                    '''
                    def overall_info(overall_type_df, overall_type, column):
                        overall = df_to_fill.loc[(df_to_fill['year'] == int(year)) & (df_to_fill['round_num'] == int(rnd)),
                                                 ['name', overall_type]].set_index('name')

                        raced_list = df_to_fill.loc[(df_to_fill['year'] == int(year)), 'round_num'].unique()

                        if int(rnd) in raced_list:
                            overall_type_df.fillna(0, inplace=True)
                            overall_type_df[column] += overall[overall_type]
                            overall_type_df.fillna(0, inplace=True)

                            original_index = df_to_fill.index
                            names = df_to_fill['name']

                            df_to_fill.set_index('name', inplace=True)
                            df_to_fill.loc[(df_to_fill['year'] == int(year)) & (df_to_fill['round_num'] == int(rnd)),
                                           column] += overall_type_df[column]
                            df_to_fill.set_index(original_index, inplace=True)
                            df_to_fill.loc[:, 'name'] = names

                    overall_info(overall_points_df, 'points', 'overall_points')
                    overall_info(overall_time_df, 'finish_time', 'overall_time')

                    for stage in stage_list:

                        '''
                        Position throughout the day
                        '''
                        def check_stage_finish(x):
                            # If the timedelta is 0 that means the rider didn't finish the race or stage.
                            if x == datetime.timedelta(0):
                                return datetime.timedelta(2)
                            else:
                                return x

                        stage_overall = df_to_fill.loc[(df_to_fill['year'] == int(year))
                                                       & (df_to_fill['round_num'] == int(rnd)), 'time_after_' + stage]

                        # Clean non-finishes
                        stage_overall = stage_overall.apply(lambda x: check_stage_finish(x))

                        # Sort by best overall time
                        stage_overall = stage_overall.sort_values(ascending=True).reset_index()

                        if len(stage_overall.iloc[:, -1]) > 0:
                            # Round was raced
                            if stage_overall.iloc[1, -1] != datetime.timedelta(2):
                                # Stage was raced
                                df_to_fill.loc[stage_overall['index'], 'position_after_' + stage] = stage_overall.index + 1
                            else:
                                df_to_fill.loc[stage_overall['index'], 'position_after_' + stage] = 0


            '''
            Overall Position Throughout the Year
            '''
            df_to_fill.loc[:, 'overall_position1'] = df_to_fill\
                .sort_values(['year', 'round_num', 'overall_points'], ascending=[1, 1, 0])\
                .groupby(['year', 'round_num']).cumcount() + 1

            df_to_fill.loc[:, 'dif'] = df_to_fill.apply(lambda x: x['finish_time'] - x['time_after_' + str(max(x['stages_raced']))], axis=1)
            df_to_fill.loc[:, 'last'] = df_to_fill.apply(lambda x: x['time_after_' + str(x['num_stages'])], axis=1)
            #pop = df_to_fill.apply(lambda x: x['time_after_' + str(x['num_stages'])], axis=1)
            print(df_to_fill.loc[(df_to_fill['dif'] != datetime.timedelta(0)) & (df_to_fill['dif'] != datetime.timedelta(1)), ['dif', 'last', 'finish_time']])

        add_columns()
        def fill_missing_sponsors(missing_df):
            """
            Sometime the sponsors aren't recorded for a race. We assume a rider is under a year contract and
            replace un-recorded races with the sponsor that has ocurred most of the year.


            with sponsor NaN's replaced and factory column added
            :param missing_df: Dataframe to replace
            :return: Dataframe with sponsor NaN's replaced and
            """
            '''
            No Loop Fill
            def de_dup(items):
                #print(items)
                lst = list(items)
                new_list = set(lst)
                new_list = [x for x in new_list if not pd.isnull(x)]
                return new_list
            p = missing_df.groupby('name')['sponsor'].apply(de_dup)
            '''
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
            :return: Dataframe
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

                # Make sure the rider has done at least one race
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

                # If the country is still empty, it was probably a one off race for the rider
                # so use the location of the race
                missing_df.loc[(missing_df['name'] == rider) & (missing_df['country'] == ''), 'country'] \
                    = missing_df.loc[(missing_df['name'] == rider) & (missing_df['country'] == ''), 'round_loc']\
                        .apply(lambda x: x.split(', ')[-1])


            return missing_df

        def fill_missing_round_country(missing_df):

            print('Filling Missing Round Country Location...')

            # Add the country to the round location

            round_loc_dict = {"Val d'Allos": 'France', 'Les Deux Alpes': 'France', 'Winter Park, CO': 'United States',
                              'Whistler, BC': 'Canada', "Val d'Isere": 'France', 'Finale Ligure': 'Italy',
                              'Nevados de Chillan Bike Park': 'Chile', 'Glentress': 'Scotland', 'Valloire': 'France',
                              'La Thuille': 'Italy', 'Carrick, Co. Wicklow': 'Ireland', 'Samoens': 'France',
                              'Zona Zero Ainsa-Sobrarbe': 'Spain', 'Corral, Valdiva': 'Chile',
                              'Cerro Catedral': 'Argentina',
                              'Snowmass Village, CO': 'United States', 'Valberg, Guillaumes': 'France',
                              'Rotorua': 'New Zealand', 'Tasmania': 'Australia'}

            def fill_country(x):
                d = round_loc_dict.get(x, x)
                new_loc = x
                if x != d:
                    new_loc = x + ', ' + d
                return new_loc

            missing_df.loc[:, 'round_loc'] = missing_df['round_loc'].apply(fill_country)

            return missing_df



        df_to_fill = fill_missing_sponsors(df_to_fill)
        df_to_fill = fill_missing_round_country(df_to_fill)
        df_to_fill = fill_missing_hometown(df_to_fill)
        df_to_fill = df_to_fill[columns].copy(deep=True)
        add_columns()

        return df_to_fill

    master_df = fill_missing_and_clean(master_df)

    # Make a master rider list just incase we need to scrape the EWS site and match names
    rider_list_txt = master_df.groupby('name').sum().index.tolist()
    with open(r'C:\EWSData\Source\riderlist.txt', 'wb') as fp:
        pickle.dump(rider_list_txt, fp)

    master_df.to_csv(os.path.join(root_dir, 'Master.csv'), encoding='utf-8')



make_master_ews()


