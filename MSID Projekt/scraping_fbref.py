import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
import re

BASIC_LINK = 'https://fbref.com'

# links to all leagues from which I scrapped the data used in my project
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

# names of csv files to which players' statistics were saved

# CSV_NAMES = [
#     'premier_league_2021_2022.csv',
#     'serie_A_2021_2022.csv',
#     'la_liga_2021_2022.csv',
#     'bundesliga_2021_2022.csv',
#     'ligue_1_2021_2022.csv',
#     'championship_2021_2022.csv',
#     'eredivisie_2021_2022.csv',
#     'primeira_liga_2021_2022.csv'
# ]


# MIS_CSV_NAMES = [
#     'premier_league_2021_2022_miscellaneous.csv',
#     'serie_A_2021_2022_miscellaneous.csv',
#     'la_liga_2021_2022_miscellaneous.csv',
#     'bundesliga_2021_2022_miscellaneous.csv',
#     'ligue_1_2021_2022_miscellaneous.csv'
#     'championship_2021_2022_miscellaneous.csv',
#     'eredivisie_2021_2022_miscellaneous.csv',
#     'primeira_liga_2021_2022_miscellaneous.csv'
#     'train_2022_2023_miscellaneous.csv',

# ]

CSV_NAMES = [
    'premier_league_2022_2023.csv',
    'serie_A_2022_2023.csv'
]

MIS_CSV_NAMES = [
    'premier_league_2022_2023_miscellaneous.csv',
    'serie_A_2022_2023_miscellaneous.csv'
]


def get_all_players_data(leagues_urls, csv_file_names, pattern):
    """This function for each link (one link = one league) calls other scraping functions and saves data files in the indicated places"""
    team_links = []
    for league_url, league_csv_name in zip(leagues_urls, csv_file_names):
        sleep(1)

        # retrieving all team links from the league table
        team_links = get_team_links(league_url)

        # gathering all player statistics and saving them to the appropriate file
        get_league_stats(team_links, pattern).to_csv(
            league_csv_name, index=False)


def get_team_stats(link, pattern):
    """This function fetches the team page for each link, reads the player stats tables and returns a DataFrame"""
    # downloading the web page
    current_data = requests.get(link)

    # finding and reading the appropriate table
    players_list = pd.read_html(
        current_data.text, match=pattern)

    # Extraction and truncation of the list of players
    players = players_list[0][:-2]
    players = players.iloc[1:len(players)-1]

    # change of column headers (the table turned out to have "two-dimensional" column headers)
    players.columns = [tuple[1] for tuple in players.columns[0:]]

    # Adding the name of their club to the player data
    players['club'] = [get_team_name(link)]*len(players)
    return players


def get_league_stats(team_links, pattern):
    """This function for each link of a given team calls a function that retrieves statistics of the team's players from the link. It accumulates data and returns it as a DataFrame"""
    all_league_players = pd.DataFrame()
    for link in team_links:
        sleep(3)
        all_league_players = pd.concat(
            [all_league_players, get_team_stats(link, pattern)], ignore_index=True)
    return all_league_players


def get_team_links(league_url):
    """This function, for each link of a given league from a given season, searches the page for links to the statistics of a given team and returns links to pages with statistics of players of a given team."""
    # downloading the web page
    data = requests.get(league_url)

    # processing our html page using the BeautifulSoup class and selecting the appropriate table
    soup = BeautifulSoup(data.text, features='html.parser')
    teams_table = soup.select('table.stats_table')[0]

    # collecting all links to the statistics of specific teams
    links = teams_table.find_all('a')
    team_links = [link.get('href') for link in links]

    # adding the main link member to the team's sublink
    return [BASIC_LINK+link for link in team_links if re.match(r".*Stats$", link)]


def get_team_name(link):
    """This function searches for the name of the club in the link and returns its name."""
    match = re.search(r"\/([A-Za-z0-9-]+)-Stats$", link)
    if match:
        club_name = match.group(1).lower().strip().replace('-', ' ')
        print(club_name)
        return club_name
    raise AttributeError("Not found club name!")


def main():
    get_all_players_data(TOP_LEAGUES_URLS, CSV_NAMES, r"^Standard Stats.*")
    # get_all_players_data(TOP_LEAGUES_URLS, MIS_CSV_NAMES,
    #                      r"^Miscellaneous Stats.*")


if __name__ == '__main__':
    main()
