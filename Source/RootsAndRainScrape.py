import pandas as pd
import bs4
from urllib.request import urlopen
import re
import os
from unidecode import unidecode

'''
The base of our analysis. We scrape all of the EWS results from the Roots and Rain website, clean them and save them
to CSV's to be aggregated to a master.csv or analyzed individually.
'''


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
        competitors_len = len(str(event_list[item_idx]).split('<td>')[3])

        if 6 < competitors_len < 16:
            links.append(event_list[item_idx].a['href'])

    if series == 'ews':
        # First race is split by age category and is useless.
        return links[:-1]
    else:
        return links


def get_ews_results(url, sex='m'):
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
    stage9_time = []
    stage9_position = []
    finish_time = []
    time_behind = []
    penalties = []
    dnf = []
    dns = []
    dsq = []
    out_at_stage = []
    num_stages_list = []
    stages_raced = []

    columns = ["year", "round_num", "round_loc", "finish_position", "overall_position", "name", "country", "sponsor",
               "stage1_time", "stage1_position", "stage2_time", "stage2_position", "stage3_time", "stage3_position",
               "stage4_time", "stage4_position", "stage5_time", "stage5_position", "stage6_time", "stage6_position",
               "stage7_time", "stage7_position", "stage8_time", "stage8_position", "stage9_time", "stage9_position",
               "finish_time", "time_behind", "penalties", "dnf", "dns", "dsq", "out_at_stage",
               "num_stages", "stages_raced"]

    if sex == 'm':
        url = 'https://www.rootsandrain.com' + url
    else:
        url = 'https://www.rootsandrain.com' + url + 'results/filters/f/'

    url = urlopen(url)
    soup = bs4.BeautifulSoup(url, 'lxml')

    # Get the info from the race --- i.e. 2013 Enduro World Series round 7 at Finale Ligure
    page_title = soup.find('h1', attrs={'id': 'h1-title'}).text
    ews_year = int(page_title[:4])
    ews_round_num = int(page_title.split(' at ')[0][-1:])
    ews_round_loc = unidecode(page_title.split(' at ')[1])
    print('Getting results for {0} round number {1} in {2}'.format(ews_round_loc, ews_round_num, ews_year))

    # Split the table by member
    results_table = str(soup.find_all('tbody')[0]).split('<tr')

    # Make sure we don't have the wrong results list
    if sex == 'm':
        if len(results_table) < 60:
            results_table = str(soup.find_all('tbody')[1]).split('<tr')
    else:
        for table in range(10):
            results_table = str(soup.find_all('tbody')[table]).split('<tr')
            if len(results_table) > 11:
                break


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
        out_at = 0  # What stage the rider went out at. 0 means finished

        # Check if the rider got disqualified
        disqualified = [any('dsq' in s.lower() for s in rider)][0]

        if 'Area' and 'Licence' not in table_columns:
            rider.insert(4, '')

        # If we have two identifying columns, remove License.
        if 'License' and 'Area' in table_columns:
            rider.remove(rider[3])

        # If there is no text then the rider DNF'd, DNS'd or DSQ
        if len(rider[0].split('>')[-1]) < 1:
            if disqualified:
                finish_position.append(rider[0].split('>')[-1].replace('', 'DSQ'))
            else:
                finish_position.append(rider[0].split('>')[-1].replace('', 'DNF'))
        else:
            finish_position.append(int(rider[0].split('>')[-1]))
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
            if 'Saturday' in table_columns and len(stage_number_list) == 0:
                stage_number_list.append('1')
                num_stages += 1

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
                if disqualified is False and (error_string.lower() == 'dns' or error_string.lower() == ''):
                    finish_position[rider_idx] = 'DNS'

            stage_count += 1
        else:
            # Stage wasn't raced
            stage1_time.append('Not Raced')
            stage1_position.append('Not Raced')

        if '2' in stage_number_list or 'Sunday' in table_columns:
            if 'Sunday' in table_columns and len(stage_number_list) == 1:
                stage_number_list.append('2')
                num_stages += 1

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

        if '9' in stage_number_list:
            if 'dummy' not in rider[6 + stage_count]:
                stage9_time.append(re.search('(^\d.*?|<strong>.*?) <',
                                             rider[6 + stage_count]).group(1).replace('<strong>', '').replace('h', ':'))
                stage9_position.append(int(re.search('\((\d+)\)', rider[6 + stage_count]).group(1)))
            else: #re.search('>(.*?)<', rider[6 + stage_count]).group(1)
                stage9_time.append(None)
                stage9_position.append(None)

                if out_at == 0:
                    out_at = 9
                    out_at_stage.append(out_at)

            stage_count += 1
        else:
            stage9_time.append('Not Raced')
            stage9_position.append('Not Raced')

        # If the rider never went out add a 0
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

    # Turn the ['1', '2'] into 1, 2
    stage_number_list = str(stage_number_list).translate(str.maketrans('', '', '[]\''))

    # Since the EWS info doesnt change per rider, create a list the
    # Same length as our results list with each constant
    for i in range(len(name)):
        ews_round_loc_list.append(ews_round_loc)
        ews_round_num_list.append(ews_round_num)
        ews_year_list.append(ews_year)
        num_stages_list.append(num_stages)
        stages_raced.append(stage_number_list)

    # Make a dataframe and export it to a csv
    stats_list = [ews_year_list, ews_round_num_list, ews_round_loc_list, finish_position,
                  overall_position, name, country, sponsor, stage1_time, stage1_position,
                  stage2_time, stage2_position, stage3_time, stage3_position, stage4_time, stage4_position,
                  stage5_time, stage5_position, stage6_time, stage6_position, stage7_time, stage7_position,
                  stage8_time, stage8_position, stage9_time, stage9_position,
                  finish_time, time_behind, penalties, dnf, dns, dsq, out_at_stage, num_stages_list, stages_raced]

    # Transpose Dataframe
    rider_df = pd.DataFrame(stats_list).T
    rider_df.columns = columns

    if sex == 'm':
        os.makedirs(os.path.join(r'C:\EWSData', ews_round_loc + ' ' + str(ews_year)), exist_ok=True)
        rider_df.to_csv(os.path.join(r'C:\EWSData', ews_round_loc + ' ' + str(ews_year), 'Results.csv'), encoding='utf-8')
    else:
        os.makedirs(os.path.join(r'C:\EWSData\Womens', ews_round_loc + ' ' + str(ews_year)), exist_ok=True)
        rider_df.to_csv(os.path.join(r'C:\EWSData\Womens', ews_round_loc + ' ' + str(ews_year), 'Results.csv'),
                        encoding='utf-8')


def all_results(sex='m'):
    for link_idx, link in enumerate(getlinks()):
        if link_idx >= 0:
            get_ews_results(link, sex)


all_results()
#get_ews_results('/race3927/2016-sep-18-enduro-world-series-7-valberg-guillaumes/results/')

