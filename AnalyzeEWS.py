from selenium import webdriver
import pandas as pd
import bs4
from urllib.request import urlopen
import re
import os
from itertools import chain
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import scipy as sci
import matplotlib.pyplot as plt
from unidecode import unidecode
from collections import Counter

csv = r'C:\EWSData\Master.csv'

df = pd.read_csv(csv)
#df = df.loc[:, 'year':]

rider_list = df.groupby('name').sum().index.tolist()
year_list = ['2013', '2014', '2015', '2016', '2017']
round_list = ['1', '2', '3', '4', '5', '6', '7', '8']
stage_list = ['1', '2', '3', '4', '5', '6', '7', '8']
'''
df.loc[df['finish_position'].isnull(), ['finish_position', 'finish_time']] = ['DNF', '']

for stage_num in stage_list:

    current_stage = 'stage' + stage_num + '_position'
    if int(stage_num) < 8:
        next_stage = 'stage' + str(int(stage_num) + 1) + '_position'

    if df[current_stage].isnull().any():
        if stage_num == 1:
            df.loc[df[current_stage].isnull(), next_stage:'stage8_position':2] = 'DNS'
        df.loc[df[current_stage].isnull(), next_stage:'stage8_position':2] = 'DNS'

print(df.loc[:, 'stage1_position':'stage8_position':2])
os.exit()
'''
def to_seconds(race_time):
    # Convert stagetime to seconds
    race_time = str(race_time)

    # Check for nan
    if len(race_time) == 3:
        time_in_seconds = 9999
    else:
        if 'h' in race_time.split(':')[0]:
            mins = int(race_time.split(':')[0].split('h')[1])
            hours = int(race_time.split(':')[0].split('h')[0])
        else:
            mins = int(race_time.split(':')[0])
            hours = 0

        seconds = int(race_time.split(':')[1].split('.')[0])
        ms = float('.' + race_time.split('.')[1])

        time_in_seconds = hours * 3600 + mins * 60 + seconds + ms

    return time_in_seconds


def fill_missing_and_clean(df_to_fill):
    def clean_df():
        # Convert the stagetime to seconds, use 9999 as dnf
        for stage_num in range(1, 9):
            df_to_fill['stage' + str(stage_num) + '_seconds'] = \
                df_to_fill['stage' + str(stage_num) + '_time'].apply(lambda x: to_seconds(x))

        df_to_fill['finish_position'] = pd.to_numeric(df['finish_position'], errors='coerce')

        # Get rid of unicode characters
        df_to_fill['city'] = df_to_fill.loc[df['city'].notnull(), 'city'].apply(lambda x: unidecode(x))
        df_to_fill['round_loc'] = df_to_fill['round_loc'].apply(lambda x: unidecode(x))

        # fill dnfs



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

                print(rider, year)

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
                        'GBR': 'United Kingdom', 'FRA': 'France', 'CRC': 'Costa Rica', 'BRA': 'Brazil', 'GE': 'Georgia',
                        'CHI': 'Chile', 'COL': 'Colombia', 'SW': 'Swaziland', 'ESP': 'Spain', 'FIN': 'Finland',
                        'AUT': 'Austria', 'CAN': 'Canada', 'BEL': 'Belgium', 'AND': 'Andorra', 'NZL': 'New Zealand',
                        'SUI': 'Switzerland', 'GER': 'Germany', 'SWE': 'Sweden', 'AUS': 'Australia', 'POR': 'Portugal',
                        'CHE': 'Switzerland', 'MON': 'Mongolia', 'DEN': 'Denmark', 'IRL': 'Ireland',
                        'SLO': 'Slovenia', 'ISR': 'Israel', 'CZE': 'Czech Republic', 'ZAF': 'South Africa',
                        'SWI': 'Switzerland', 'SVN': 'Slovenia', 'DEU': 'Germany', 'PRT': 'Portugal',
                        'SM': 'San Marino', 'RU': 'Russia', 'DNK': 'Denmark', 'CHL': 'Chile', 'NOR': 'Norway',
                        'tAUS': 'Australia', 'oUSA': 'United States', 'wCAN': 'Canada', 'Austraia': 'Australia',
                        'Czechia': 'Czech Republic'}

        for rider in rider_list:

            print(rider)

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
                          'Snowmass Village, CO': 'United States', 'Valberg, Guillaumes': 'France', 'Rotorua': 'New Zealand'}

        def fill_country(x):
            d = round_loc_dict.get(x, x)
            new_loc = x
            if x != d:
                new_loc = x + ', ' + d
            return new_loc
        missing_df['round_loc'] = missing_df.loc[:, 'round_loc'].apply(fill_country)

        return missing_df

    new_df = fill_missing_hometown(df_to_fill)
    new_df = fill_missing_sponsors(new_df)
    clean_df()
    new_df = fill_missing_round_country(new_df)

    return new_df


def get_stats(df):
    def get_gap():
        # Get the gap for all of the stages


        # Get the average of the top 10 fastest stage times and add a new gap item for each rider based on
        # The average time - their time
        for year in year_list:
            for round in round_list:
                for stage in stage_list:
                    current_stage_seconds = 'stage' + stage + '_seconds'

                    current_top10 = df.query('year == ' + year + ' and round_num == ' + round) \
                        [current_stage_seconds].nsmallest(10).index
                    current_round = df.query('year == ' + year + ' and round_num == ' + round).index

                    if not all(np.isnan(df.loc[current_round, current_stage_seconds])):
                        # Time behind avg of top 10
                        df.loc[current_round, 'stage' + stage + '_gap'] = (df.loc[current_round, current_stage_seconds] \
                                                                           - df.loc[
                                                                               current_top10, current_stage_seconds].mean())

                        # Avg time of top 10
                        df.loc[current_round, 'stage' + stage + '_top10avg'] \
                            = df.loc[current_top10, current_stage_seconds].mean()

    def plot_rider_gap(rider):
        # Make a list (event) of lists (stage) and then flatten it out ignoring DNF's (9999 second stage)
        # and ignoring stages where the rider was moe than two mins back

        x_seconds = [df.loc[df['name'] == rider, 'stage' + str(x) + '_seconds'] for x in range(1, 9)]
        x_seconds = [item for list1 in x_seconds for item in list1 if item != 9999]
        y_gap = [df.loc[df['name'] == rider, 'stage' + str(x) + '_gap'] for x in range(1, 9)]
        y_gap = [item for list1 in y_gap for item in list1 if item != 0]

        for idx, item in enumerate(y_gap):
            if item > 120:
                x_seconds[idx] = 6969
                y_gap[idx] = 6969

        x_seconds = [item for item in x_seconds if item != 6969]
        y_gap = [item for item in y_gap if item != 6969]

        print(len(x_seconds), len(y_gap))

        '''
        # Get the AVG for each stage
        avg_stage_time = [df.loc[df['name'] == rider, 'stage' + str(x) + '_top10avg'] for x in range(1, 9)]
        avg_stage_time = [item for list1 in avg_stage_time for item in list1 if item != 9999]
        print(len(avg_stage_time), len(y_gap))
        zeroto2min = [y_gap[avg_stage_time.index(item)] for item in avg_stage_time if item < 120]
        twoto4min = [y_gap[avg_stage_time.index(item)] for item in avg_stage_time if item >= 120 and item < 240]
        fourto6min = [y_gap[avg_stage_time.index(item)] for item in avg_stage_time if item >= 240 and item < 360]
        sixto8min = [y_gap[avg_stage_time.index(item)] for item in avg_stage_time if item >= 260 and item < 480]
        eightto10min = [y_gap[avg_stage_time.index(item)] for item in avg_stage_time if item >= 480 and item < 600]
        tento15min = [y_gap[avg_stage_time.index(item)] for item in avg_stage_time if item >= 600 and item < 900]
        fifteento30min = [y_gap[avg_stage_time.index(item)] for item in avg_stage_time if item >= 900 and item < 1800]
        thirtyplus = [y_gap[avg_stage_time.index(item)] for item in avg_stage_time if item >= 1800]

        time_gap_basket = []

        #print(twoto4min)
        time_gap_basket.append(np.mean(zeroto2min))
        time_gap_basket.append(np.mean(twoto4min))
        time_gap_basket.append(np.mean(fourto6min))
        time_gap_basket.append(np.mean(sixto8min))
        time_gap_basket.append(np.mean(eightto10min))
        time_gap_basket.append(np.mean(tento15min))
        time_gap_basket.append(np.mean(fifteento30min))
        time_gap_basket.append(np.mean(thirtyplus))

        for idx, item in enumerate(time_gap_basket):
            if np.isnan(time_gap_basket[idx]):
                time_gap_basket[idx] = 0

        plt.plot(list(range(8)), time_gap_basket)
        '''

        slope, intercept, r_value, p_value, std_err = sci.stats.linregress(x_seconds, y_gap)
        print(' Slope: {0} R2: {1} P_Value: {2} Time Lost per Minute: {3} Average: {4} Standard Error: {5}'
              .format(slope, r_value ** 2, p_value, slope * 60, np.mean(y_gap), std_err))

        plt.figure(figsize=(10.7, 7))
        plt.hlines(0, 0, max(x_seconds) + 20)
        plt.scatter(x_seconds, y_gap)
        plt.xlim(0)
        plt.plot(np.unique(x_seconds), np.poly1d(np.polyfit(x_seconds, y_gap, 2))(np.unique(x_seconds)))
        # plt.show()

        return slope

    # for rider in rider_list:
    #    plot_rider_gap(rider)
    # get_gap()

    def main_statistics():
        # Get descriptive stats about overall EWS environment
        stats = {}

        stats['RacesPerRider'] = df.groupby(['name']).size().sort_values(ascending=False)
        average_finish = df.groupby('name')['finish_position'].apply(sum) / df.groupby('name').size()
        average_finish = average_finish.sort_values()

        '''
        avg_finish_list = []
        slope_list = []

        for rider in rider_list[10:]:
            avg_finish_list.append(average_finish[rider])
            slope_list.append(plot_rider_gap(rider))

        x = slope_list
        y = avg_finish_list

        print(len(rider_list), len(avg_finish_list), len(slope_list))

        slope, intercept, r_value, p_value, std_err = sci.stats.linregress(x, y)
        print(' Slope: {0} R2: {1} P_Value: {2} Time Lost per Minute: {3} Average: {4} Standard Error: {5}'
              .format(slope, r_value ** 2, p_value, slope * 60, np.mean(y), std_err))

        plt.figure(figsize=(10.7, 7))
        plt.hlines(0, 0, max(x) + 20)
        plt.scatter(x, y)
        plt.xlim(0)
        plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 2))(np.unique(x)))
        plt.show()

        print(average_finish['Mckay VEZINA'])
        '''

        # df.to_csv(os.path.join('C:\EWSData', 'Master2.csv'), encoding='utf-8')


        # get_stats(df)


def country_stats():
    '''
    Country Stats
        Total Races per Country
        Average Finish per Country
        Most wins per Country
        Total Hometown wins
        % Chance to win a hometown race
        Country with most races
        Average racers per venue in hometown or not
    '''
    # Total Races per Country
    total_races_per_country = df.groupby('country')['finish_position'].size().sort_values()

    #A Average Finish per Country
    average_country_finish = df.groupby('country')['finish_position'].mean().sort_values()

    # Country with most wins
    country_with_most_wins = df.loc[df['finish_position'] == 1].groupby('country')\
        ['finish_position'].value_counts().sort_values(ascending=False)


    # % prob to win in home country
    winners_df = df.loc[df['finish_position'] == 1, ['country', 'round_loc', 'name']]
    hometown_win = winners_df.apply(lambda x: x['country'] in x['round_loc'], axis=1)
    pct_hometown_win = hometown_win.value_counts()[True] /  hometown_win.size

    #print(winners_df['round_loc'].apply(lambda x: x.split(', ')[-1]).value_counts())
    #print(winners_df['country'].value_counts())
    # Get a list of countries that have a EWS round and have riders who have won.
    a = '|'.join(winners_df['country'].unique().tolist())
    winning_countries = winners_df['round_loc'].str.contains(a)
    winning_countries = winners_df.loc[winning_countries, 'round_loc'].apply(lambda x: x.split(', ')[-1]).unique()

    for country in winning_countries:
        #print(country)
        # France 50% chance to win
        winners_france = df.loc[df['finish_position'] == 1, ['country', 'round_loc']]
        print(winners_france.shape[0])
        winners_france['round_loc'] = winners_france['round_loc'].apply(lambda x: x.split(', ')[-1])
        winners_france = winners_france.loc[winners_france['round_loc'] == country, :]


        c = Counter(winners_france['country'])

        #print(c[country])

        winners_france = df.loc[df['finish_position'] == 1, ['country', 'round_loc']]
        winners_france['round_loc'] = winners_france['round_loc'].apply(lambda x: x.split(', ')[-1])
        winners_france = winners_france.loc[winners_france['round_loc'] != country, :]
        #print(winners_france.shape)





    # round_loc_count = df.groupby('round_loc').sum().index.tolist().split(', ')[1]

    # print(round_loc_count)

    def norm_score(p, q, Q):
        score = p * (np.e**(-q / Q))

        return score

    normalized_country_finish = norm_score(average_country_finish, total_races_per_country, 1500).sort_values()




print( np.e, np.e ** -5, np.e ** -2.5, np.e ** -1, np.e ** -.5, np.e ** -.1)
'''
print(norm_score(4, 100, 30))
print(norm_score(7, 4, 30))
print(norm_score(7, 10, 30))
print(norm_score(10, 4, 30))
print(norm_score(10, 100, 30))
'''
print(df.groupby('name').sum().index.tolist())
#country_stats()
fill_missing_and_clean(df)
df.to_csv(r'C:\EWSData\Master2.csv', encoding='utf-8')
