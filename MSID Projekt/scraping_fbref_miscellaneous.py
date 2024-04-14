import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
import re

BASIC_LINK = 'https://fbref.com'

TOP_LEAGUES_URLS = [
    # 'https://fbref.com/en/comps/9/2021-2022/2021-2022-Premier-League-Stats',
    # 'https://fbref.com/en/comps/11/2021-2022/2021-2022-Serie-A-Stats',
    # 'https://fbref.com/en/comps/12/2021-2022/2021-2022-La-Liga-Stats',
    # 'https://fbref.com/en/comps/20/2021-2022/2021-2022-Bundesliga-Stats',
    # 'https://fbref.com/en/comps/13/2021-2022/2021-2022-Ligue-1-Stats',
    # 'https://fbref.com/en/comps/10/2021-2022/2021-2022-Championship-Stats',
    # 'https://fbref.com/en/comps/23/2021-2022/2021-2022-Eredivisie-Stats',
    # 'https://fbref.com/en/comps/32/2021-2022/2021-2022-Primeira-Liga-Stats'
    'https://fbref.com/en/comps/9/Premier-League-Stats',
    'https://fbref.com/en/comps/11/Serie-A-Stats'
]


CSV_NAMES = [
    # 'premier_league_2021_2022_miscellaneous.csv',
    # 'serie_A_2021_2022_miscellaneous.csv',
    # 'la_liga_2021_2022_miscellaneous.csv',
    # 'bundesliga_2021_2022_miscellaneous.csv',
    # 'ligue_1_2021_2022_miscellaneous.csv'
    # 'championship_2021_2022_miscellaneous.csv',
    # 'eredivisie_2021_2022_miscellaneous.csv',
    # 'primeira_liga_2021_2022_miscellaneous.csv'
    'train_2022_2023_miscellaneous.csv',
    'train_2022_2023_miscellaneous.csv'
]


def get_all_players_season_21_22():
    team_links = []
    for league_url, league_csv_name in zip(TOP_LEAGUES_URLS, CSV_NAMES):
        sleep(1)
        team_links.extend(get_team_links(league_url))
        team_links = get_team_links(league_url)
        get_league_stats(team_links).to_csv(league_csv_name, index=False)
    # get_league_stats(team_links).to_csv(CSV_NAMES[0], index=False)
        
    # return all_leagues_players

def get_team_stats(l):
    current_data = requests.get(l)
    players = pd.read_html(
        current_data.text, match=r"^Miscellaneous Stats.*")
    players[0] = players[0][:-2]
    players[0] = players[0].iloc[1:len(players[0])-1]
    players[0].columns = [tuple[1] for tuple in players[0].columns[0:]]
    players[0]['club'] = [get_team_name(l)]*len(players[0])
    return players[0]

def get_league_stats(team_links):
    all_league_players = pd.DataFrame()
    for l in team_links:
        sleep(3)
        all_league_players = pd.concat([all_league_players, get_team_stats(l)], ignore_index=True)
    return all_league_players

def get_team_links(league_url):
    data = requests.get(league_url)
    soup = BeautifulSoup(data.text, features='html.parser')
    teams_table = soup.select('table.stats_table')[0]
    links = teams_table.find_all('a')
    team_links = [link.get('href') for link in links]
    return [BASIC_LINK+link for link in team_links if re.match(r".*Stats$", link)]

def get_team_name(l):
    match = re.search(r"\/([A-Za-z0-9-]+)-Stats$", l)
    if match:
        club_name = match.group(1).lower().strip().replace('-', ' ')
        print(club_name)
        return club_name
    raise AttributeError("Not found club name!")

def main():
    get_all_players_season_21_22()

if __name__ == '__main__':
    main()