import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os
from unidecode import unidecode
import pickle
from glob import glob

'''
Sometime results don't show up on the Roots and Rain site, but they are on the EWS Site.
We have to lean them all separately because they are in different formats
We also have to match the names to the Roots and Rain text so that we have consistent people
As more results are omitted from Roots and Rain they will be added here in the same format
'''

def make_master_rider_list():
    """
    Make sure we only get names from roots and rain.
    If riderlist.txt doesn't exit that means its the first run so we create a new list from
    roots and rain csv files
    If it does exit that means we got a dump from MakeMasterCSV that includes all EWSSite results.
    
    :return: A list of all the riders who have raced an EWS
    """

    all_files = glob(os.path.join(r'C:\EWSData', '**', 'Results.csv'))

    df_from_files = [pd.read_csv(file) for file in all_files]

    roots_df = pd.DataFrame(pd.concat(df_from_files))
    roots_df.drop(roots_df.columns[0], axis=1, inplace=True)

    roots_df.sort_values(['year', 'round_num'], inplace=True)
    roots_df.reset_index(inplace=True)
    roots_df.drop(roots_df.columns[0], axis=1, inplace=True)

    name_list = roots_df.groupby('name').sum().index.tolist()

    if os.path.isfile(r'C:\EWSData\Source\riderlist.txt'):
        with open(r'C:\EWSData\Source\riderlist.txt', 'rb') as fp:
            name_list = pickle.load(fp)

    return name_list



def clean_ews_results():
    with open(r'C:\EWSData\Source\Rotorua2015Riders.txt', 'rb') as fp:
        rotorua_riders = pickle.load(fp)

    with open(r'C:\EWSData\Source\Whistler2016Riders.txt', 'rb') as fp:
        whistler_riders = pickle.load(fp)

    print('Cleaning Whistler Text...')
    whistler_list = []

    for rider in whistler_riders.split('\n')[1:-1]:

        # Richie Rude	13:01.870	(3)	06:30.790	(42)	04:07.200	(1)	03:24.990	(1)	21:30.800	(1)	48:35.650	(1)
        rider_details = rider.split()

        # Last name to uppercase and join first and last name
        rider_details[1] = rider_details[1].upper()
        rider_details[0:2] = [' '.join(rider_details[0:2])]

        # Check for a 3 word name i.e. Bas Van Steenbergen
        if any(character.isalpha() for character in rider_details[1]):
            rider_details[1] = rider_details[1].upper()
            rider_details[0:2] = [' '.join(rider_details[0:2])]
        rider_details[0] = unidecode(rider_details[0])

        rider_details[2:13:2] = [x.translate(str.maketrans('', '', '()')) for x in rider_details[2:13:2]]

        whistler_list.append(rider_details)

    print('Cleaning Rotorua Text')
    rotorua_list = []

    for rider_idx, rider in enumerate(rotorua_riders.split('\n')[1:-1]):

        # 140 David SHEPHARD GBR 15:52.94119. 5:30.62119. 7:26.16117. 7:31.09118.
        #  6:11.25116. 6:15.01113. 11:47.47111. 1:00:34.54112. +25:14.08
        rider_details = rider.split()

        # Get rid of the first placing
        if re.findall(r'(\.)', rider_details[0]):
            del rider_details[0]

        # Last name to uppercase and join first and last name
        rider_details[2] = rider_details[2].upper()
        rider_details[1:3] = [' '.join(rider_details[1:3])]

        # Check if its a second last name or the country code
        if any(character.isalpha() for character in rider_details[2]) and len(rider_details[2]) != 3:
            rider_details[2] = rider_details[2].upper()
            rider_details[1:3] = [' '.join(rider_details[1:3])]
        rider_details[1] = unidecode(rider_details[1])

        # Get first split
        if rider_details[3][-1] == '.':
            rider_details.insert(4, rider_details[3][-4:])
            rider_details[3] = rider_details[3][:-4]

        # Get second split
        if rider_details[5][-1] == '.':
            rider_details.insert(6, rider_details[5][-4:])
            rider_details[5] = rider_details[5][:-4]

        # Get third split
        if rider_details[7][-1] == '.':
            rider_details.insert(8, rider_details[7][-4:])
            rider_details[7] = rider_details[7][:-4]

        # Get fourth split
        if rider_details[9][-1] == '.':
            rider_details.insert(10, rider_details[9][-4:])
            rider_details[9] = rider_details[9][:-4]

        if len(rider_details) > 11:
            # Get fifth split
            if rider_details[11][-1] == '.':
                rider_details.insert(12, rider_details[11][-4:])
                rider_details[11] = rider_details[11][:-4]

        if len(rider_details) > 13:
            # Get sixth split
            if rider_details[13][-1] == '.':
                rider_details.insert(14, rider_details[13][-4:])
                rider_details[13] = rider_details[13][:-4]

        if len(rider_details) > 15:
            # Get seventh split
            if rider_details[15][-1] == '.':
                rider_details.insert(16, rider_details[15][-4:])
                rider_details[15] = rider_details[15][:-4]

        if len(rider_details) > 17:
            # Get seventh split
            if rider_details[17][-1] == '.':
                rider_details.insert(18, rider_details[17][-4:])
                rider_details[17] = rider_details[17][:-4]

        # Get rid of the . after split position
        rider_details[4:19:2] = [x.replace('.', '') for x in rider_details[4:19:2]]

        # Remove the + from Time behind: +12.73
        # 6969 indicates a NaN that I added manually
        if len(rider_details[-5]) > 3 and rider_details[-5] != '6969':
            rider_details[-5] = rider_details[-5][1:]

        rotorua_list.append(rider_details)

        return whistler_list, rotorua_list

def whistler_name_match(whistler_list, master_rider_list):
    print('Matching Whistler Names...')

    names = [info[1] for info in whistler_list]

    # Make sure all the names were adding are the same as in the Roots and Rain results sheet.
    # Our names arent that different so we can just use the name from the first algorithm
    # and average out the predictions to get out new name i.e. Richie Rude turns into Richie Rude Jr.
    for name_idx, name in enumerate(names):
        matched_name, score1 = process.extractOne(name, master_rider_list, scorer=fuzz.ratio)
        _, score2 = process.extractOne(name, master_rider_list, scorer=fuzz.partial_ratio)
        _, score3 = process.extractOne(name, master_rider_list, scorer=fuzz.token_set_ratio)
        _, score4 = process.extractOne(name, master_rider_list, scorer=fuzz.token_sort_ratio)
        avg_score = (score1 + score2 + score3 + score4) / 4


        if avg_score > 80:
            whistler_list[name_idx][0] = matched_name

    columns = ["name", "stage1_time", "stage1_position", "stage2_time",
               "stage2_position", "stage3_time", "stage3_position",
               "stage4_time", "stage4_position", "stage5_time", "stage5_position", "finish_time",
               "finish_position"]

    # Add static variables
    whistler_df = pd.DataFrame(whistler_list, columns=columns)
    whistler_df['year'] = 2016
    whistler_df['round_num'] = 6
    whistler_df['round_loc'] = 'Whistler, BC, Canada'
    whistler_df["stage8_time"] = 'Not Raced'
    whistler_df["stage8_position"] = 'Not Raced'
    whistler_df["overall_position"] = ''
    whistler_df["country"] = ''
    whistler_df["stage6_time"] = 'Not Raced'
    whistler_df["stage6_position"] = 'Not Raced'
    whistler_df["stage7_time"] = 'Not Raced'
    whistler_df["stage7_position"] = 'Not Raced'
    whistler_df["time_behind"] = ''
    whistler_df["dnf"] = False
    whistler_df["dns"] = False
    whistler_df["dsq"] = False
    whistler_df["out_at_stage"] = 0
    whistler_df["num_stages"] = 5

    # Put finish_time in H:M:S:m format
    whistler_df['finish_time'] = whistler_df['finish_time'].apply(lambda x: '0:' + x if x.count(':') < 2 else x)

    whistler_df['time_behind'] = pd.to_datetime(whistler_df['finish_time'])
    whistler_df['time_behind'] = whistler_df['time_behind'] \
        .apply(lambda x: pd.Timedelta(x - whistler_df.loc[0, 'time_behind']))

    # Remove days and hours and milliseconds i.e. 0 days 00:00:07.130000
    whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: str(x)[10:])
    whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: x[:-4]
            if x[-4:] == '0000' and len(x) > 1 else x + '.00')

    # If there are no minutes just get the seconds
    whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: x[3:] if x[:3] == '00:' else x)

    # Remove 0 from 01:23.42 but dont remove 0 from the first place dude
    whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: x[1:]
        if x[:1] == '0' and len(x) > 1 else x)

    os.makedirs(r'C:\EWSData\Whistler, BC 2016', exist_ok=True)
    whistler_df.to_csv(r'C:\EWSData\Whistler, BC 2016\EWSResults.csv', encoding='utf-8')


def rotorua_name_match(rotorua_list, master_rider_list):
    print('Matching Rotorua Names...')

    names = [info[1] for info in rotorua_list]

    # Make sure all the names were adding are the same as in the Roots and Rain results sheet.
    # Our names arent that different so we can just use the name from the first algorithm
    # and average out the predictions to get out new name i.e. Richie Rude turns into Richie Rude Jr.
    for name_idx, name in enumerate(names):
        matched_name, score1 = process.extractOne(name, master_rider_list, scorer=fuzz.ratio)
        _, score2 = process.extractOne(name, master_rider_list, scorer=fuzz.partial_ratio)
        _, score3 = process.extractOne(name, master_rider_list, scorer=fuzz.token_set_ratio)
        _, score4 = process.extractOne(name, master_rider_list, scorer=fuzz.token_sort_ratio)
        avg_score = (score1 + score2 + score3 + score4) / 4

        # James PRITCHARD is really close to another name so we just omit that
        if avg_score > 80 and name != 'James PRITCHARD':
            rotorua_list[name_idx][1] = matched_name

    columns = ["overall_position", "name", "country", "stage1_time", "stage1_position", "stage2_time",
               "stage2_position", "stage3_time", "stage3_position",
               "stage4_time", "stage4_position", "stage5_time", "stage5_position", "stage6_time", "stage6_position",
               "stage7_time", "stage7_position", "finish_time", 'finish_position', "time_behind", "dnf", "dns",
               "dsq", "out_at_stage"]

    # Add static variables
    rotorua_df = pd.DataFrame(rotorua_list, columns=columns)
    rotorua_df['round_num'] = 1
    rotorua_df['year'] = 2015
    rotorua_df['round_loc'] = 'Rotorua, New Zealand'
    rotorua_df["stage8_time"] = 'Not Raced'
    rotorua_df["stage8_position"] = 'Not Raced'
    rotorua_df["penalties"] = ''
    rotorua_df["num_stages"] = 7

    # 6969 is manually inputed NaN
    rotorua_df.replace('6969', '', inplace=True)

    os.makedirs(r'C:\EWSData\Rotorua 2015', exist_ok=True)
    rotorua_df.to_csv(r'C:\EWSData\Rotorua 2015\EWSResults.csv', encoding='utf-8')


master_rider_list = make_master_rider_list()
whistler_list, rotorua_list = clean_ews_results()
whistler_name_match(whistler_list, master_rider_list)
rotorua_name_match(rotorua_list, master_rider_list)
