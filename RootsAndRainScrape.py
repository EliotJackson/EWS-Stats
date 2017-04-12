import pandas as pd
import bs4
from urllib.request import urlopen
import re
import os
from unidecode import unidecode
import glob
import numpy as np

ews_url = 'https://www.rootsandrain.com/organiser137/ews'
root_ews_dir = r'C:\EWSData'


def getlinks(original_url=ews_url, series='ews'):
    """
    Visit the roots and rain site and get all of the links to the races
    :param original_url: URL of race organier
    :param series: i.e. ews, dh

    :return: A list of links to each race
    """

    links = []
    original_url = urlopen(original_url)
    soup = bs4.BeautifulSoup(original_url, 'lxml')

    event_list = soup.find_all('tr')

    # Loop through each item of the organizers race table. Make sure the race had participants ( > 6 )
    # And wasn't canceled or otherwise ( < 16 ) Then add each of the links to the links list
    for item_idx in range(1, len(event_list)):

        print('Getting link {0} of {1}'.format(item_idx, len(event_list)))

        # Get the 5th item in the row ( Date, Race, Venue, Competitors, Men's Time, Women's Time )
        competitors_len = len(str(event_list[item_idx]).split('<td>')[4])

        if 6 < competitors_len < 16:
            links.append(event_list[item_idx].a['href'])

    if series == 'ews':
        return links[:-1]
    else:
        return links


def get_ews_results(url):
    """

    :param url: URL of race
    :return: Write a CSV of structured results
    """

    num_stages = 0
    finish_position = []
    overall_position = []
    name = []
    country = []
    sponsor = []
    ews_year_list = []
    ews_round_num_list = []
    ews_round_loc_list = []
    stage1_time = []
    stage1_position = []
    stage2_time = []
    stage2_position = []
    stage3_time = []
    stage3_position = []
    stage4_time = []
    stage4_position = []
    stage5_time = []
    stage5_position = []
    stage6_time = []
    stage6_position = []
    stage7_time = []
    stage7_position = []
    stage8_time = []
    stage8_position = []
    finish_time = []
    time_behind = []
    penalties = []
    dnf = []
    dns = []
    dsq = []
    out_at_stage = []

    columns = ["year", "round_num", "round_loc", "finish_position", "overall_position", "name", "country", "sponsor",
               "stage1_time", "stage1_position", "stage2_time", "stage2_position", "stage3_time", "stage3_position",
               "stage4_time", "stage4_position", "stage5_time", "stage5_position", "stage6_time", "stage6_position",
               "stage7_time", "stage7_position", "stage8_time", "stage8_position", "finish_time",
               "time_behind", "penalties", "dnf", "dns", "dsq", "out_at_stage"]

    url = 'https://www.rootsandrain.com' + url
    url = urlopen(url)
    soup = bs4.BeautifulSoup(url, 'lxml')

    # Get the info from the race --- i.e. 2013 Enduro World Series round 7 at Finale Ligure
    page_title = soup.find('h1', attrs={'id': 'h1-title'}).text
    ews_year = int(page_title[:4])
    ews_round_num = int(page_title.split(' at ')[0][-1:])
    ews_round_loc = unidecode(page_title.split(' at ')[1])
    print('Getting results for {0} round number {1} in {2}'.format(ews_round_loc, ews_round_num, ews_year))

    # Split the Men's table by member
    results_table = str(soup.find_all('tbody')[0]).split('<tr')

    # Make sure we don't have the wrong results list
    if len(results_table) < 60:
        results_table = str(soup.find_all('tbody')[1]).split('<tr')

    # Omit the columns element
    results_table = results_table[1:]
    rider_result_list = [re.findall('>(.*?)</td>', rider) for rider in results_table]
    print(str(len(results_table)) + ' Riders')

    # Get the text of all of the columns in the table header.
    # They are sorting links so we can just find the by link
    table_columns = [res.string for res in soup.find('thead').find_all('a')]

    # Go through each column. If it has a number (i.e. Stage 6) add it to the list.
    # On it's way in, separate the number and take the max of the whole list ---num.split(' ')[1]
    stage_number_list = [re.search('(\d+)', num).group(1) for num in table_columns
                         if len(re.findall('(\d+)', num)) > 0]
    if len(stage_number_list) > 0:
        num_stages = int(len(stage_number_list))

    for rider_idx, rider in enumerate(rider_result_list):

        'Getting rider {0} of {1}'.format(rider_idx, len(rider_result_list))

        '''
        Go through each rider and extract relevant information

        ['<td>6', '6', '<a href="/race2023/2013-oct-20-enduro-world-series-7-finale-ligure/?country=3"><span class="flag
        f-fr"></span></a><a class="rn" href="/rider32388/nicolas-lau/results/" title="View mountain biking race results
        and photos of Nicolas LAU">Nicolas LAU</a>', ' ', 'FRA', '', '3:49.8 <i>(3)</i>',
        '<strong>6:46.8 <i>(1)</i></strong>', '4:10.6 <i>(3)</i>', '6:50.4 <i>(2)</i>',
        '<strong>6:46.6 <i>(1)</i></strong>', '1:00.0', '<strong class="ftw">26:24.0</strong>', '43.5s']

        '''
        stage_count = 0  # Reset stage count
        out_at = 0 # what stage the rider went out at. 0 means finished

        # Check if the rider got disqualified
        disqualified = [any('dsq' in s.lower() for s in rider)][0]

        if 'Area' and 'Licence' not in table_columns:
            rider.insert(4, '')

        # If we have two identifying columns, remove one.
        if 'License' and 'Area' in table_columns:
            rider.remove(rider[3])

        # If there is no text then the rider DNF'd
        if len(rider[0].split('<td>')[1]) < 1:
            if disqualified:
                finish_position.append(rider[0].split('<td>')[1].replace('', 'DSQ'))
            else:
                finish_position.append(rider[0].split('<td>')[1].replace('', 'DNF'))
        else:
            finish_position.append(int(rider[0].split('<td>')[1]))
        overall_position.append(rider[1])

        if 'Unknown' in rider[2]:
            name.append('Unknown RIDER')
        else:
            # Decode any unicode chars -- Rémy ABSALON Remy ABSALON
            name.append(unidecode(rider[2].split('">')[3].split('</a>')[0]))

        country.append(unidecode(rider[4]))

        # If sponsor column isnt empty
        if len(rider[5]) > 5:
            sponsor.append(rider[5].split('>')[1].split('<')[0])
        else:
            sponsor.append('')

        if 'dummy' in rider[len(rider) - 2]:
            finish_time.append('')
        else:
            finish_time.append(rider[len(rider) - 2].split('">')[1].split('</')[0].replace('h', ':'))

        time_behind.append(rider[len(rider) - 1].replace('-', '0').replace('s', ''))

        # 1:00.0 vs <span class="dummy"></span>
        if len(rider[6 + num_stages]) < 8:
            penalty = rider[6 + num_stages].replace('s', '')

            if len(penalty) == 1:
                penalty = '0:0' + penalty + '.00'
            if len(penalty) == 2:
                penalty = '0:' + penalty + '.00'

            penalties.append(penalty)
        else:
            penalties.append('')

        # In case of missing columns ( i.e. Stage 1, Stage 3, Stage 6 ) Use the stage count variable to
        # See how many columns we have so far. By checking if the stage is in the list we can see exactly
        # What stages we have data for and add those. The columns will still be sequential in the html
        # We look for 'dummy' to indicate DNF on that stage. <strong> indicates stage win which we don't need
        if '1' in stage_number_list or 'Saturday' in table_columns:
            # Stage was raced
            if 'dummy' not in rider[6]:
                # Rider finished stage
                stage1_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6]).group(1).replace('<strong>', '').replace('h', ':'))
                stage1_position.append(int(re.search('\((\d+)\)', rider[6]).group(1)))
            else:
                # Rider didn't finish stage. See if he started
                error_string = re.search('>(.*?)<', rider[6]).group(1)
                stage1_time.append(None)
                stage1_position.append(None)

                out_at = 1
                out_at_stage.append(out_at)

                # Since its the first stage
                if disqualified == False and (error_string.lower() == 'dns' or error_string.lower() == ''):
                    finish_position[rider_idx] = 'DNS'

            stage_count += 1
        else:
            # Stage wasn't raced
            stage1_time.append('Not Raced')
            stage1_position.append('Not Raced')

        if '2' in stage_number_list or 'Sunday' in table_columns:
            if 'dummy' not in rider[6 + stage_count]:
                stage2_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6 + stage_count]).group(1).replace('<strong>', '').replace('h', ':'))
                stage2_position.append(int(re.search('\((\d+)\)', rider[6 + stage_count]).group(1)))
            else:
                stage2_time.append(None)
                stage2_position.append(None)


                if out_at == 0:

                    out_at = 2
                    out_at_stage.append(out_at)
            stage_count += 1
        else:
            stage2_time.append('Not Raced')
            stage2_position.append('Not Raced')

        if '3' in stage_number_list:
            if 'dummy' not in rider[6 + stage_count]:
                stage3_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6 + stage_count]).group(1).replace('<strong>', '').replace('h', ':'))
                stage3_position.append(int(re.search('\((\d+)\)', rider[6 + stage_count]).group(1)))
            else:
                stage3_time.append(None)
                stage3_position.append(None)

                if out_at == 0:
                    out_at = 3
                    out_at_stage.append(out_at)

            stage_count += 1
        else:
            stage3_time.append('Not Raced')
            stage3_position.append('Not Raced')

        if '4' in stage_number_list:
            if 'dummy' not in rider[6 + stage_count]:
                stage4_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6 + stage_count]).group(1).replace('<strong>', '').replace('h', ':'))
                stage4_position.append(int(re.search('\((\d+)\)', rider[6 + stage_count]).group(1)))
            else:
                stage4_time.append(None)
                stage4_position.append(None)

                if out_at == 0:
                    out_at = 4
                    out_at_stage.append(out_at)
            stage_count += 1
        else:
            stage4_time.append('Not Raced')
            stage4_position.append('Not Raced')

        if '5' in stage_number_list:
            if 'dummy' not in rider[6 + stage_count]:
                stage5_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6 + stage_count]).group(1).replace('<strong>', '').replace('h', ':'))
                stage5_position.append(int(re.search('\((\d+)\)', rider[6 + stage_count]).group(1)))
            else:
                stage5_time.append(None)
                stage5_position.append(None)

                if out_at == 0:
                    out_at = 5
                    out_at_stage.append(out_at)
            stage_count += 1
        else:
            stage5_time.append('Not Raced')
            stage5_position.append('Not Raced')

        if '6' in stage_number_list:
            if 'dummy' not in rider[6 + stage_count]:
                stage6_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6 + stage_count]).group(1).replace('<strong>', '').replace('h', ':'))
                stage6_position.append(int(re.search('\((\d+)\)', rider[6 + stage_count]).group(1)))
            else:
                stage6_time.append(None)
                stage6_position.append(None)

                if out_at == 0:
                    out_at = 6
                    out_at_stage.append(out_at)

            stage_count += 1
        else:
            stage6_time.append('Not Raced')
            stage6_position.append('Not Raced')

        if '7' in stage_number_list:
            if 'dummy' not in rider[6 + stage_count]:
                stage7_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6 + stage_count]).group(1).replace('<strong>', '').replace('h', ':'))
                stage7_position.append(int(re.search('\((\d+)\)', rider[6 + stage_count]).group(1)))
            else:
                stage7_time.append(None)
                stage7_position.append(None)

                if out_at == 0:
                    out_at = 7
                    out_at_stage.append(out_at)

            stage_count += 1
        else:
            stage7_time.append('Not Raced')
            stage7_position.append('Not Raced')

        if '8' in stage_number_list:
            if 'dummy' not in rider[6 + stage_count]:
                stage8_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6 + stage_count]).group(1).replace('<strong>', '').replace('h', ':'))
                stage8_position.append(int(re.search('\((\d+)\)', rider[6 + stage_count]).group(1)))
            else: #re.search('>(.*?)<', rider[6 + stage_count]).group(1)
                stage8_time.append(None)
                stage8_position.append(None)

                if out_at == 0:
                    out_at = 8
                    out_at_stage.append(out_at)
            stage_count += 1
        else:
            stage8_time.append('Not Raced')
            stage8_position.append('Not Raced')

        if out_at == 0:

            out_at_stage.append(out_at)

        if isinstance(finish_position[rider_idx], str):
            # Check if the rider got disqualified
            dsq.append('dsq' in finish_position[rider_idx].lower())
            # Check if the rider DNS'd
            dns.append(('dns' in finish_position[rider_idx].lower()))
            # Check if the rider DNF'd
            dnf.append(('dnf' in finish_position[rider_idx].lower()))

            finish_position[rider_idx] = ''
        else:
            dsq.append(False)
            dns.append(False)
            dnf.append(False)


    # Since the EWS info doesnt change per rider, create a list the
    # Same length as our results list with each constant
    for i in range(len(name)):
        ews_round_loc_list.append(ews_round_loc)
        ews_round_num_list.append(ews_round_num)
        ews_year_list.append(ews_year)

    # Make a dataframe and export it to a csv
    stats_list = [ews_year_list, ews_round_num_list, ews_round_loc_list, finish_position,
                  overall_position, name, country, sponsor, stage1_time, stage1_position,
                  stage2_time, stage2_position, stage3_time, stage3_position, stage4_time, stage4_position,
                  stage5_time, stage5_position, stage6_time, stage6_position, stage7_time, stage7_position,
                  stage8_time, stage8_position, finish_time, time_behind, penalties, dnf, dns, dsq, out_at_stage]

    # Transpose Dataframe
    rider_df = pd.DataFrame(stats_list).T
    rider_df.columns = columns

    os.makedirs(os.path.join(r'C:\EWSData', ews_round_loc + ' ' + str(ews_year)), exist_ok=True)
    rider_df.to_csv(os.path.join(r'C:\EWSData', ews_round_loc + ' ' + str(ews_year), 'Results.csv'), encoding='utf-8')


def all_results():
    for link_idx, link in enumerate(getlinks()):
        if link_idx >= 0:
            get_ews_results(link)


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


#all_results()
#get_ews_results('/race3927/2016-sep-18-enduro-world-series-7-valberg-guillaumes/results/')
make_master_ews()
