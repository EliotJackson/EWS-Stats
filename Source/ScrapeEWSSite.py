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

def make_master_rider_list(sex='m'):
    """
    Make sure we only get names from roots and rain.
    If riderlist.txt doesn't exit that means its the first run so we create a new list from
    roots and rain csv files
    If it does exit that means we got a dump from MakeMasterCSV that includes all EWSSite results.
    
    :return: A list of all the riders who have raced an EWS
    """
    if sex == 'm':
        all_files = glob(os.path.join(r'C:\EWSData', '**', 'Results.csv'))
    else:
        all_files = glob(os.path.join(r'C:\EWSData\Womens', '**', 'Results.csv'))


    df_from_files = [pd.read_csv(file) for file in all_files]

    roots_df = pd.DataFrame(pd.concat(df_from_files))
    roots_df.drop(roots_df.columns[0], axis=1, inplace=True)

    roots_df.sort_values(['year', 'round_num'], inplace=True)
    roots_df.reset_index(inplace=True)
    roots_df.drop(roots_df.columns[0], axis=1, inplace=True)

    name_list = roots_df.groupby('name').sum().index.tolist()

    if sex == 'm':
        if os.path.isfile(r'C:\EWSData\Source\riderlist.txt'):
            with open(r'C:\EWSData\Source\riderlist.txt', 'rb') as fp:
                name_list = pickle.load(fp)
    else:
        if os.path.isfile(r'C:\EWSData\Source\riderlistwomen.txt'):
            with open(r'C:\EWSData\Source\riderlistwomen.txt', 'rb') as fp:
                name_list = pickle.load(fp)

    return name_list

wem ='''
1. 2 Anne Caroline CHAUSSON FRA 11:12.66 2. 3:56.37 1. 4:00.76 1. 6:06.27 2. 3:58.49 1. 4:13.62 1. 7:52.77 1. 41:20.94 1. 0 False False False 0
2. 1 Tracy MOSELEY GBR 11:11.06 1. 3:57.88 2. 4:06.20 2. 5:59.82 1. 4:10.76 2. 4:14.60 2. 7:54.91 2. 41:35.23 2. +14.29 False False False 0
3. 3 Cecile RAVANEL FRA 11:22.66 3. 4:07.85 4. 4:16.90 3. 6:10.57 3. 4:10.88 3. 4:23.32 3. 8:07.60 3. 42:39.78 3. +1:18.84 False False False 0
4. 4 Anneke BEERTEN NED 11:59.51 6. 4:05.03 3. 4:18.33 4. 6:20.19 4. 5:00.62 16. 4:37.64 4. 8:24.36 4. 44:45.68 4. +3:24.74 False False False 0
5. 56 Meggie BICHARD GBR 12:10.69 7. 4:29.71 13. 4:30.85 6. 6:37.01 11. 4:33.95 6. 4:39.88 5. 8:28.34 5. 45:30.43 5. +4:09.49  False False False 0
6. 5 Ines THOMA GER 11:44.96 4. 4:21.57 9. 4:34.66 8. 6:34.48 8. 4:38.30 8. 4:48.57 9. 9:07.70 9. 45:50.24 6. +4:29.30 False False False 0
7. 7 Rosara JOSEPH NZL 11:51.12 5. 4:22.76 10. 5:33.56 30. 6:29.05 5. 4:24.45 4. 4:46.48 7. 8:54.60 8. 46:22.02 7. +5:01.08 False False False 0
8. 55 Lorraine TRUONG SUI 12:33.17 10. 4:16.77 5. 4:28.96 5. 6:36.77 10. 4:49.06 12. 4:47.46 8. 8:51.46 7. 46:23.65 8. +5:02.71 False False False 0
9. 10 Katy WINTON GBR 12:12.37 8. 4:19.34 8. 4:31.24 7. 6:31.18 6. 4:33.45 5. 5:04.02 16. 9:21.61 17. 46:33.21 9. +5:12.27 False False False 0
10. 76 Sasha SMITH NZL 12:40.31 11. 4:38.89 20. 4:40.12 9. 6:35.59 9. 4:36.67 7. 4:44.78 6. 9:11.31 12. 47:07.67 10. +5:46.73 False False False 0
11. 61 Raewyn MORRISON NZL 12:28.81 9. 4:27.15 11. 4:44.28 11. 6:32.74 7. 4:49.86 14. 4:51.39 11. 9:16.30 16. 47:10.53 11. +5:49.59 False False False 0
12. 9 Isabeau COURDURIER FRA 13:12.50 16. 4:31.56 15. 4:41.67 10. 6:54.05 21. 4:43.58 10. 4:51.32 10. 8:49.90 6. 47:44.58 12. +6:23.64 False False False 0
13. 52 Anka MARTIN NZL 12:50.91 13. 4:29.55 12. 4:46.52 13. 6:46.88 14. 4:49.69 13. 4:56.11 13. 9:21.82 18. 48:01.48 13. +6:40.54 False False False 0
14. 54 Pauline DIEFFENTHALER FRA 12:59.66 14. 4:39.38 21. 4:48.97 14. 6:49.29 17. 4:42.67 9. 5:13.91 19. 9:13.73 14. 48:27.61 14. +7:06.67 False False False 0
15. 6 Anita GEHRIG SUI 14:17.58 26. 4:18.90 6. 4:45.25 12. 6:42.21 13. 4:44.22 11. 5:00.92 15. 9:08.15 10. 48:57.23 15. +7:36.29 False False False 0
16. 8 Kelli EMMETT USA 12:43.53 12. 4:33.19 18. 5:19.59 26. 6:48.68 16. 4:51.74 15. 5:23.19 24. 9:26.08 19. 49:06.00 16. +7:45.06 False False False 0
17. 68 Vanessa QUIN NZL 13:48.95 19. 4:31.17 14. 4:53.93 15. 7:04.01 22. 5:34.67 29. 4:52.63 12. 9:14.94 15. 50:00.30 17. +8:39.36 False False False 0
18. 78 Anja MCDONALD NZL 13:06.89 15. 4:58.59 26. 4:54.96 16. 6:49.75 18. 5:10.30 20. 5:17.86 21. 9:44.98 22. 50:03.33 18. +8:42.39 False False False 0
19. 53 Valentina MACHEDA ITA 13:31.23 17. 4:33.59 19. 4:58.14 18. 7:04.66 23. 5:06.91 19. 5:19.57 22. 9:29.28 20. 50:03.38 19. +8:42.44 False False False 0
20. 79 Natalie JAKOBS NZL 13:54.91 20. 4:49.54 24. 5:07.33 21. 6:52.30 19. 5:11.41 21. 5:11.11 18. 9:13.24 13. 50:19.84 20. +8:58.90 False False False 0
21. 51 Carolin GEHRIG SUI 14:14.37 23. 4:32.34 16. 5:13.80 22. 6:52.69 20. 5:28.18 28. 4:59.04 14. 9:10.64 11. 50:31.06 21. +9:10.12 False False False 0
22. 57 Katrina STRAND CAN 13:57.72 22. 4:48.50 23. 5:19.01 24. 7:05.61 24. 5:24.26 25. 5:04.41 17. 9:50.97 25. 51:30.48 22. +10:09.54 False False False 0
23. 80 Alba WUNDERLIN SUI 13:56.57 21. 4:54.56 25. 5:04.20 19. 7:12.49 27. 5:22.83 24. 5:23.53 25. 9:48.54 24. 51:42.72 23. +10:21.78 False False False 0
24. 77 Annika SMAIL NZL 14:19.50 27. 4:32.87 17. 5:18.99 23. 6:47.39 15. 5:41.71 31. 5:16.37 20. 9:46.12 23. 51:42.95 24. +10:22.01 False False False 0
25. 59 Mary MONCORGE FRA 14:17.40 25. 4:41.46 22. 4:56.88 17. 7:12.67 28. 5:05.35 18. 5:35.10 30. 9:54.95 26. 51:43.81 25. +10:22.87 False False False 0
26. 81 Megan ROSE AUS 14:28.33 28. 5:03.87 30. 5:40.97 31. 7:24.01 32. 5:12.03 22. 5:28.22 28. 9:35.69 21. 52:53.12 26. +11:32.18 False False False 0
27. 72 Julia HOBSON GBR 14:17.34 24. 5:02.04 29. 5:28.30 27. 7:21.32 31. 5:26.44 26. 5:44.44 32. 10:44.96 31. 54:04.84 27. +12:43.90 False False False 0
28. 58 Hannah BARNES GBR 14:39.99 31. 5:00.54 27. 5:50.98 35. 7:09.57 26. 5:27.51 27. 5:38.54 31. 10:27.18 28. 54:14.31 28. +12:53.37 False False False 0
29. 86 Adrienne HOOPER NZL 15:23.46 34. 5:01.74 28. 5:19.21 25. 7:17.83 30. 5:21.41 23. 5:28.77 29. 10:53.70 32. 54:46.12 29. +13:25.18 False False False 0
30. 82 Katherine ONEILL NZL 14:59.79 32. 5:06.35 32. 5:46.71 34. 7:06.08 25. 5:52.15 32. 5:26.77 27. 11:22.13 35. 55:39.98 30. +14:19.04 False False False 0
31. 74 Fiona BEATTIE GBR 14:39.74 30. 5:08.78 33. 6:50.84 41. 7:36.06 34. 6:07.97 33. 5:24.68 26. 11:04.07 33. 56:52.14 31. +15:31.20 False False False 0
32. 83 Genevieve MCKEW AUS 17:31.82 41. 5:04.50 31. 5:30.96 28. 7:17.54 29. 5:35.73 30. 5:23.08 23. 10:36.41 29. 57:00.04 32. +15:39.10 False False False 0
33. 73 Rachael GURNEY GBR 15:05.74 33. 5:11.91 34. 5:43.33 32. 7:40.66 36. 6:13.63 35. 5:52.10 35. 11:13.63 34. 57:01.00 33. +15:40.06 False False False 0
34. 87 Erin GREENE NZL 15:53.17 35. 5:49.80 40. 5:32.26 29. 7:28.49 33. 6:11.13 34. 5:49.38 34. 10:22.73 27. 57:06.96 34. +15:46.02 False False False 0
35. 91 Rosemary BARNES AUS 16:51.69 38. 5:19.29 35. 6:40.78 38. 7:38.88 35. 6:49.67 40. 5:52.65 36. 10:42.87 30. 59:55.83 35. +18:34.89 False False False 0
36. 71 Hanna JONSSON SWE 16:39.16 37. 5:40.86 39. 5:45.10 33. 7:58.97 38. 6:36.93 38. 5:46.14 33. 12:15.12 37. 1:00:42.28 36. +19:21.34 False False False 0
37. 90 Jill BEHLEN USA 17:08.80 39. 5:20.21 37. 6:46.58 40. 7:54.38 37. 6:27.83 37. 6:30.20 39. 11:50.95 36. 1:01:58.95 37. +20:38.01 False False False 0
38. 66 Rach THROOP USA 16:17.35 36. 5:37.93 38. 6:39.43 37. 8:15.53 39. 6:41.33 39. 6:23.59 38. 12:17.60 38. 1:02:12.76 38. +20:51.82 False False False 0
39. 67 Syd SCHULZ USA 18:25.86 42. 5:20.09 36. 5:56.40 36. 8:17.61 40. 6:24.41 36. 5:54.60 37. 16:05.00 39. 1:06:23.97 39. +25:03.03 False False False 0
60 Sarah LEISHMAN CAN 13:37.25 18. 4:18.95 7. 5:04.28 20. 6:42.19 12. 5:03.31 17. 6969 6969 6969 6969 6969 6969 6969 True False False 6
63 Casey BROWN CAN 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 False True False 1
69 Amy PRYSE-PHILLIPS CAN 19:17.51 43. 6:22.21 41. 6:45.32 39. 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 4
70 Kylie MADUNA AUS 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 False True False 1
75 Genevieve BARIL-GUERARD CAN 17:17.70 40. 6:57.56 42. 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 3
84 Janine KAVANAGH NZL 14:33.26 29. 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 2
85 Sarsha HUNTINGTON AUS 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 True False False 1
89 Cait DOOLEY USA 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 6969 False True False 1
'''
with open(r'C:\EWSData\Womens\Rotorua2015WomenRiders.txt', 'wb') as fp:
    pickle.dump(wem, fp)
def clean_ews_results(sex='m'):
    if sex == 'm':
        with open(r'C:\EWSData\Source\Rotorua2015Riders.txt', 'rb') as fp:
            rotorua_riders = pickle.load(fp)
        with open(r'C:\EWSData\Source\Whistler2016Riders.txt', 'rb') as fp:
            whistler_riders = pickle.load(fp)
    else:
        with open(r'C:\EWSData\Womens\Rotorua2015WomenRiders.txt', 'rb') as fp:
            rotorua_riders = pickle.load(fp)
            print(rotorua_riders)
        with open(r'C:\EWSData\Womens\Whistler2016WomenRiders.txt', 'rb') as fp:
            whistler_riders = pickle.load(fp)


    print('Cleaning Whistler Text...')
    whistler_list = []

    for rider in whistler_riders.split('\n')[1:-1]:

        # Richie Rude	13:01.870	(3)	06:30.790	(42)	04:07.200	(1)	03:24.990	(1)	21:30.800	(1)	48:35.650	(1)
        whistler_rider_details = rider.split()

        # Last name to uppercase and join first and last name
        whistler_rider_details[1] = whistler_rider_details[1].upper()
        whistler_rider_details[0:2] = [' '.join(whistler_rider_details[0:2])]

        # Check for a 3 word name i.e. Bas Van Steenbergen
        if any(character.isalpha() for character in whistler_rider_details[1]):
            whistler_rider_details[1] = whistler_rider_details[1].upper()
            whistler_rider_details[0:2] = [' '.join(whistler_rider_details[0:2])]
        whistler_rider_details[0] = unidecode(whistler_rider_details[0])

        # Remove parentheses around finish position
        whistler_rider_details[2:13:2] = [x.translate(str.maketrans('', '', '()')) for x in whistler_rider_details[2:13:2]]

        whistler_list.append(whistler_rider_details)

    print('Cleaning Rotorua Text...')
    rotorua_list = []

    for rider_idx, rider in enumerate(rotorua_riders.split('\n')[1:-1]):

        # 140 David SHEPHARD GBR 15:52.94119. 5:30.62119. 7:26.16117. 7:31.09118.
        #  6:11.25116. 6:15.01113. 11:47.47111. 1:00:34.54112. +25:14.08
        rotorua_rider_details = rider.split()

        # Get rid of the first placing
        if re.findall(r'(\.)', rotorua_rider_details[0]):
            del rotorua_rider_details[0]

        # Last name to uppercase and join first and last name
        rotorua_rider_details[2] = rotorua_rider_details[2].upper()
        rotorua_rider_details[1:3] = [' '.join(rotorua_rider_details[1:3])]

        # Check if its a second last name or the country code
        if any(character.isalpha() for character in rotorua_rider_details[2]) and len(rotorua_rider_details[2]) != 3:
            rotorua_rider_details[2] = rotorua_rider_details[2].upper()
            rotorua_rider_details[1:3] = [' '.join(rotorua_rider_details[1:3])]
        rotorua_rider_details[1] = unidecode(rotorua_rider_details[1])

        # Get first split
        if rotorua_rider_details[3][-1] == '.':
            rotorua_rider_details.insert(4, rotorua_rider_details[3][-4:])
            rotorua_rider_details[3] = rotorua_rider_details[3][:-4]

        # Get second split
        if rotorua_rider_details[5][-1] == '.':
            rotorua_rider_details.insert(6, rotorua_rider_details[5][-4:])
            rotorua_rider_details[5] = rotorua_rider_details[5][:-4]

        # Get third split
        if rotorua_rider_details[7][-1] == '.':
            rotorua_rider_details.insert(8, rotorua_rider_details[7][-4:])
            rotorua_rider_details[7] = rotorua_rider_details[7][:-4]

        # Get fourth split
        if rotorua_rider_details[9][-1] == '.':
            rotorua_rider_details.insert(10, rotorua_rider_details[9][-4:])
            rotorua_rider_details[9] = rotorua_rider_details[9][:-4]

        if len(rotorua_rider_details) > 11:
            # Get fifth split
            if rotorua_rider_details[11][-1] == '.':
                rotorua_rider_details.insert(12, rotorua_rider_details[11][-4:])
                rotorua_rider_details[11] = rotorua_rider_details[11][:-4]

        if len(rotorua_rider_details) > 13:
            # Get sixth split
            if rotorua_rider_details[13][-1] == '.':
                rotorua_rider_details.insert(14, rotorua_rider_details[13][-4:])
                rotorua_rider_details[13] = rotorua_rider_details[13][:-4]

        if len(rotorua_rider_details) > 15:
            # Get seventh split
            if rotorua_rider_details[15][-1] == '.':
                rotorua_rider_details.insert(16, rotorua_rider_details[15][-4:])
                rotorua_rider_details[15] = rotorua_rider_details[15][:-4]

        if len(rotorua_rider_details) > 17:
            # Get seventh split
            if rotorua_rider_details[17][-1] == '.':
                rotorua_rider_details.insert(18, rotorua_rider_details[17][-4:])
                rotorua_rider_details[17] = rotorua_rider_details[17][:-4]

        # Get rid of the . after split position
        rotorua_rider_details[4:19:2] = [x.replace('.', '') for x in rotorua_rider_details[4:19:2]]

        # Remove the + from Time behind: +12.73
        # 6969 indicates a NaN that I added manually
        if len(rotorua_rider_details[-5]) > 3 and rotorua_rider_details[-5] != '6969':
            rotorua_rider_details[-5] = rotorua_rider_details[-5][1:]

        rotorua_list.append(rotorua_rider_details)

    return whistler_list, rotorua_list

def whistler_name_match(whistler_list, master_rider_list, sex='m'):
    print('Matching Whistler Names...')

    names = [info[0] for info in whistler_list]

    # Make sure all the names were adding are the same as in the Roots and Rain results sheet.
    # Our names arent that different so we can just use the name from the first algorithm
    # and average out the predictions to get out new name i.e. Richie Rude turns into Richie Rude Jr.
    for name_idx, name in enumerate(names):
        matched_name, score1 = process.extractOne(name, master_rider_list, scorer=fuzz.ratio)
        _, score2 = process.extractOne(name, master_rider_list, scorer=fuzz.partial_ratio)
        _, score3 = process.extractOne(name, master_rider_list, scorer=fuzz.token_set_ratio)
        _, score4 = process.extractOne(name, master_rider_list, scorer=fuzz.token_sort_ratio)
        avg_score = (score1 + score2 + score3 + score4) / 4

        if sex == 'm':
            thresh = 80
        else:
            thresh = 75

        if avg_score > thresh:
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
    whistler_df["stages_raced"] = '1, 2, 3, 4, 5'

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

    if sex =='m':
        os.makedirs(r'C:\EWSData\Whistler, BC 2016', exist_ok=True)
        whistler_df.to_csv(r'C:\EWSData\Whistler, BC 2016\EWSResults.csv', encoding='utf-8')
    else:
        os.makedirs(r'C:\EWSData\Womens\Whistler 2016', exist_ok=True)
        whistler_df.to_csv(r'C:\EWSData\Womens\Whistler 2016\EWSResults.csv', encoding='utf-8')


def rotorua_name_match(rotorua_list, master_rider_list, sex='m'):
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
    rotorua_df["stages_raced"] = '1, 2, 3, 4, 5, 6, 7'

    # 6969 is manually inputed NaN
    rotorua_df.replace('6969', '', inplace=True)

    if sex == 'm':
        os.makedirs(r'C:\EWSData\Rotorua 2015', exist_ok=True)
        rotorua_df.to_csv(r'C:\EWSData\Rotorua 2015\EWSResults.csv', encoding='utf-8')
    else:
        os.makedirs(r'C:\EWSData\Womens\Rotorua 2015', exist_ok=True)
        rotorua_df.to_csv(r'C:\EWSData\Womens\Rotorua 2015\EWSResults.csv', encoding='utf-8')


def execute(sex='m'):
    if sex == 'm':
        master_rider_list = make_master_rider_list()
        whistler_list, rotorua_list = clean_ews_results()
        whistler_name_match(whistler_list, master_rider_list)
        rotorua_name_match(rotorua_list, master_rider_list)
    else:
        master_rider_list = make_master_rider_list(sex='f')
        whistler_list, rotorua_list = clean_ews_results(sex='f')
        whistler_name_match(whistler_list, master_rider_list, sex='f')
        rotorua_name_match(rotorua_list, master_rider_list, sex='f')


execute()
