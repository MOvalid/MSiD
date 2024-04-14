import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join


COLUMN_NAMES_TO_DROP = ['Nation', 'Starts', 'G+A', 'G-PK', 'PK', 'PKatt', 'npxG', 'xAG', 'npxG+xAG',
                        'PrgC', 'PrgP', 'PrgR', 'G+A.1', 'xAG.1', 'G-PK.1', 'G+A-PK', 'xG+xAG', 'npxG.1', 'npxG+xAG.1', 'Matches']

COLUMN_NAMES_TO_DROP_MIS = ['Nation', 'Pos', 'Age', 'CrdY',
                            'CrdR', 'PKwon', 'PKcon', 'OG', 'Won', 'Lost', 'Matches']

POSITION_MAPPING = {'GK' : 1, 'DF': 2, 'MF': 3, 'FW': 4, 'DF,MF': 5 , 'DF,FW' : 6, 'FW,MF': 7}


def get_from_csv(csv_file_name, column_names):
    # reading data from csv file and loading to DataFrame
    league_stats = pd.read_csv(csv_file_name) 

    # dropping useless columnsin DataFrame
    for name in column_names:
        league_stats.drop(name, axis=1, inplace=True)

    # renaming duplicate columns
    league_stats.rename(columns={
                        'Gls.1': 'Gls/90', 'Ast.1': 'Ast/90', 'xG.1': 'xG/90'}, inplace=True)

    # filtering the players who played minimum 3 full matches
    league_stats = league_stats[league_stats['90s']
                                >= 3.0].reset_index(drop=True)

    # returning processed data
    return league_stats

def process_all_players_data(my_paths, csv_result_file_name):
    # filtering the files in my directory, which have my main data
    only_files = [f for f in listdir(my_paths[0]) if isfile(join(my_paths[0], f))]

    all_players = pd.DataFrame()

    # loading players data into one DateFrame "all_players"
    for csv in only_files:
        all_players = pd.concat(
            [all_players,  get_from_csv(f'{my_paths[0]}\{csv}', COLUMN_NAMES_TO_DROP)], ignore_index=True)


    # filtering the files in my directory, which have miscellaneous data stats
    only_mis_files = [f for f in listdir(my_paths[1]) if isfile(join(my_paths[1], f))]

    all_players_mis = pd.DataFrame()

    # loading miscellaneous data into one DateFrame "all_player_miss"
    for csv in only_mis_files:
        all_players_mis = pd.concat(
            [all_players_mis,  get_from_csv(f'{my_paths[1]}\{csv}', COLUMN_NAMES_TO_DROP_MIS)], ignore_index=True)

    # Dropping column '90s'
    all_players_mis.pop('90s')
    #'left join' merging my 2 DataFrames into one, based on 'Player' and 'club' columns. 
    result = pd.merge(all_players, all_players_mis,
                      how='left', on=['Player', 'club'])
    # processing "club" column
    clubs = result.pop('club')
    result.insert(len(result.columns), 'club', clubs)
    # print(result.columns)

    # processing "Pos" column
    result['Pos'] = [' '.join(sorted(pos.split(','))).replace(' ', ',') for pos in result['Pos']]


    result['Pos'] = result['Pos'].astype(str)
    result['Pos'] = result['Pos'].replace(POSITION_MAPPING)
    result['Pos'] = result['Pos'].fillna(-1)

    # dropping rows with uncorrect value of "Pos" attribute
    result = result[result['Pos'].isin(set(POSITION_MAPPING.values()))]

    # dropping defective rows
    result = result.dropna()

    # saving my result DataFrame to csv file
    result.to_csv(csv_result_file_name, index=False)


    



def process_result_data(my_paths, csv_result_file_name):

    # loading and light processing data
    all_players = get_from_csv(my_paths[0], COLUMN_NAMES_TO_DROP)
    all_players_mis = get_from_csv(my_paths[1], COLUMN_NAMES_TO_DROP_MIS)

    # dropping '90s' column
    all_players_mis.pop('90s')

    #'left join' merging my 2 DataFrames into one, based on 'Player' and 'club' columns.     #
    result = pd.merge(all_players, all_players_mis,
                      how='left', on=['Player', 'club'])
    # processing 'club' column
    clubs = result.pop('club')
    result.insert(len(result.columns), 'club', clubs)
    # print(result.columns)

    # processing 'Pos' column
    result['Pos'] = [' '.join(sorted(pos.split(','))).replace(' ', ',') for pos in result['Pos']]

    result['Pos'] = result['Pos'].astype(str)
    result['Pos'] = result['Pos'].replace(POSITION_MAPPING)
    result['Pos'] = result['Pos'].fillna(-1)

    # dropping rows with uncorrect value of "Pos" attribute
    result = result[result['Pos'].isin(set(POSITION_MAPPING.values()))]

    # dropping defective rows
    result = result.dropna()

    # saving my result DataFrame to csv file
    result.to_csv(csv_result_file_name, index=False)


    





def main():
    process_all_players_data((r'csv_2021_2022', r'csv_2021_2022_miscellaneous'), 'all_players_2021_2022.csv')
    process_all_players_data((r'csv_2022_2023', r'csv_2022_2023_miscellaneous'), 'test_2022_2023.csv')


    



if __name__ == "__main__":
    main()
