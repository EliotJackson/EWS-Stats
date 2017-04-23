import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os
from unidecode import unidecode
import pickle
from glob import glob

def make_master_rider_list():
    """
    Make sure we only get names from roots and rain.

    If riderlist.txt doesn't exit that means its the first run so we create a new list from
    roots and rain csv files
    
    If it does exit that means we got a dump from MakeMasterCSV that includes all EWSSite results as well.
    
    :return: A list of all the riders who have ranced an EWS
    """
    all_files = glob(os.path.join(r'C:\EWSData', '**', 'Results.csv'))

    df_from_files = [pd.read_csv(file) for file in all_files]

    roots_df = pd.DataFrame(pd.concat(df_from_files))
    roots_df.drop(roots_df.columns[0], axis=1, inplace=True)

    roots_df.sort_values(['year', 'round_num'], inplace=True)
    roots_df.reset_index(inplace=True)
    roots_df.drop(roots_df.columns[0], axis=1, inplace=True)

    name_list = roots_df.groupby('name').sum().index.tolist()

    # Get all the names from our current master
    if os.path.isfile(r'C:\EWSData\Source\riderlist.txt'):
        with open(r'C:\EWSData\Source\riderlist.txt', 'rb') as fp:
            name_list = pickle.load(fp)

    return name_list

master_rider_list = make_master_rider_list()
print(master_rider_list)

with open(r'C:\EWSData\Source\Rotorua2015Riders.txt', 'rb') as fp:
    rotorua_riders = pickle.load(fp)

with open(r'C:\EWSData\Source\Whistler2016Riders.txt', 'rb') as fp:
    whistler_riders = pickle.load(fp)

rider_list = whistler_riders.split('\n')[1:-1]
whistler_list = []
for rider in rider_list:
    m = rider.split()
    m[1] = m[1].upper()
    m[0:2] = [' '.join(m[0:2])]
    if any(c.isalpha() for c in m[1]):
        m[1] = m[1].upper()
        m[0:2] = [' '.join(m[0:2])]
    m[0] = unidecode(m[0])

    m[2:13:2] = [x.translate(str.maketrans('', '', '()')) for x in m[2:13:2]]

    whistler_list.append(m)

rider_list2 = rotorua_riders.split('\n')[1:-1]
rotorua_list = []
for rider_idx, rider in enumerate(
        rider_list2):  # 140 David SHEPHARD GBR 15:52.94119. 5:30.62119. 7:26.16117. 7:31.09118. 6:11.25116. 6:15.01113. 11:47.47111. 1:00:34.54112. +25:14.08
    m = rider.split()

    # Get rid of the first placing
    if re.findall(r'(\.)', m[0]):
        del m[0]
    # Last name to uppercase
    m[2] = m[2].upper()

    # Join first and last name
    m[1:3] = [' '.join(m[1:3])]

    # Check if its a second last name or the country code
    if any(c.isalpha() for c in m[2]) and len(m[2]) != 3:
        m[2] = m[2].upper()
        m[1:3] = [' '.join(m[1:3])]
    m[1] = unidecode(m[1])

    # Get first split
    if m[3][-1] == '.':
        m.insert(4, m[3][-4:])
        m[3] = m[3][:-4]

    # Get second split
    if m[5][-1] == '.':
        m.insert(6, m[5][-4:])
        m[5] = m[5][:-4]

    # Get third split
    if m[7][-1] == '.':
        m.insert(8, m[7][-4:])
        m[7] = m[7][:-4]

    # Get fourth split
    if m[9][-1] == '.':
        m.insert(10, m[9][-4:])
        m[9] = m[9][:-4]

    if len(m) > 11:
        # Get fifth split
        if m[11][-1] == '.':
            m.insert(12, m[11][-4:])
            m[11] = m[11][:-4]

    if len(m) > 13:
        # Get sixth split
        if m[13][-1] == '.':
            m.insert(14, m[13][-4:])
            m[13] = m[13][:-4]

    if len(m) > 15:
        # Get seventh split
        if m[15][-1] == '.':
            m.insert(16, m[15][-4:])
            m[15] = m[15][:-4]
    if len(m) > 17:
        # Get seventh split
        if m[17][-1] == '.':
            m.insert(18, m[17][-4:])
            m[17] = m[17][:-4]

    # Get rid of the . after split position
    m[4:19:2] = [x.replace('.', '') for x in m[4:19:2]]

    if len(m[-5]) > 3 and m[-5] != '6969':
        m[-5] = m[-5][1:]

    rotorua_list.append(m)

def whistler_name_match():
    names = [x[0] for x in whistler_list]
    for name_idx, name in enumerate(names):
        a, b = process.extractOne(name, master_rider_list, scorer=fuzz.ratio)
        _, b2 = process.extractOne(name, master_rider_list, scorer=fuzz.partial_ratio)
        _, b3 = process.extractOne(name, master_rider_list, scorer=fuzz.token_set_ratio)
        _, b4 = process.extractOne(name, master_rider_list, scorer=fuzz.token_sort_ratio)
        c = (b + b2 + b3 + b4) / 4

        #print(name, a, c)
        if c > 80:
            whistler_list[name_idx][0] = a

    columns = ["name", "stage1_time", "stage1_position", "stage2_time",
               "stage2_position", "stage3_time", "stage3_position",
               "stage4_time", "stage4_position", "stage5_time", "stage5_position", "finish_time",
               "finish_position"]

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

    whistler_df['finish_time'] = whistler_df['finish_time'].apply(lambda x: '0:' + x if x.count(':') < 2 else x)

    whistler_df['time_behind'] = pd.to_datetime(whistler_df['finish_time'])
    whistler_df['time_behind'] = whistler_df['time_behind'] \
        .apply(lambda x: pd.Timedelta(x - whistler_df.loc[0, 'time_behind']))
    whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: str(x)[10:-4])
    whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: x[3:] if x[:3] == '00:' else x)
    whistler_df['time_behind'] = whistler_df['time_behind'].apply(lambda x: x[1:] \
        if x[:1] == '0' and len(x) > 1 else x)

    os.makedirs(r'C:\EWSData\Whistler, BC 2016', exist_ok=True)
    whistler_df.to_csv(r'C:\EWSData\Whistler, BC 2016\EWSResults.csv', encoding='utf-8')

    return whistler_list


def rotorua_name_match():
    names = [x[1] for x in rotorua_list]
    for name_idx, name in enumerate(names):
        a, b = process.extractOne(name, master_rider_list, scorer=fuzz.ratio)
        _, b2 = process.extractOne(name, master_rider_list, scorer=fuzz.partial_ratio)
        _, b3 = process.extractOne(name, master_rider_list, scorer=fuzz.token_set_ratio)
        _, b4 = process.extractOne(name, master_rider_list, scorer=fuzz.token_sort_ratio)
        c = (b + b2 + b3 + b4) / 4

        if c > 80 and name != 'James PRITCHARD':
            rotorua_list[name_idx][1] = a

    columns = ["overall_position", "name", "country", "stage1_time", "stage1_position", "stage2_time",
               "stage2_position", "stage3_time", "stage3_position",
               "stage4_time", "stage4_position", "stage5_time", "stage5_position", "stage6_time", "stage6_position",
               "stage7_time", "stage7_position", "finish_time", 'finish_position', "time_behind", "dnf", "dns",
               "dsq", "out_at_stage"]

    rotorua_df = pd.DataFrame(rotorua_list, columns=columns)
    rotorua_df['round_num'] = 1
    rotorua_df['year'] = 2015
    rotorua_df['round_loc'] = 'Rotorua, New Zealand'
    rotorua_df["stage8_time"] = 'Not Raced'
    rotorua_df["stage8_position"] = 'Not Raced'
    rotorua_df["penalties"] = ''
    rotorua_df.replace('6969', '', inplace=True)

    os.makedirs(r'C:\EWSData\Rotorua 2015', exist_ok=True)
    rotorua_df.to_csv(r'C:\EWSData\Rotorua 2015\EWSResults.csv', encoding='utf-8')
    return rotorua_list



a = process.extract('Dick Rude', master_rider_list, scorer=fuzz.ratio)
print(a)

whistler_name_match()
rotorua_name_match()
