import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from time import sleep

NEW_COLUMNS = ['name', 'position', 'played_minutes', "appearances", "first_squad", "substitute_in",
               "substitute_out", "goals", 'avg_goals', 'yellow_cards', 'yellow_red_cards', 'red_cards', 'club']

TOP_LEAGUES_URLS = [
    'https://www.soccerstats247.com/competitions/england/premier-league/',
    'https://www.soccerstats247.com/competitions/germany/bundesliga/',
    'https://www.soccerstats247.com/competitions/spain/la-liga/',
    'https://www.soccerstats247.com/competitions/italy/serie-a/',
    'https://www.soccerstats247.com/competitions/france/ligue-1/',
    'https://www.soccerstats247.com/competitions/netherlands/eredivisie/',
    'https://www.soccerstats247.com/competitions/portugal/primeira-liga/'
]

CSV_NAMES = [
    'premier_league_2022_2023.csv',
    'bundesliga_2022_2023.csv',
    'la_liga_2022_2023.csv',
    'serie_A_2022_2023.csv',
    'ligue_1_2022_2023.csv',
    'eredivisie_2022_2023.csv'
    'primeira_liga_2022_2023.csv'
]


def get_all_players_season_22_23(leagues_urls, csv_file_names):
    for league_url, league_csv_name in zip(league_csv_name, csv_file_names):
        sleep(1)
        # retrieving all team links from the league table
        team_links = get_team_links(league_url)

        # gathering all player statistics and saving them to the appropriate file
        get_league_stats(team_links).to_csv(league_csv_name, index=False)


def get_team_links(league_url):
    """This function, for each link of a given league from a given season, searches the page for links to the statistics of a given team and returns links to pages with statistics of players of a given team."""
    # downloading the web page
    data = requests.get(league_url)
    
    # processing our html page using the BeautifulSoup class and selecting the appropriate table
    soup = BeautifulSoup(data.text, features='html.parser')
    teams_table = soup.select('table.gridAlternate')[0]

    # collecting all links to the statistics of specific teams
    links = teams_table.find_all('a')
    return [link.get('href') for link in links]


def get_league_stats(team_links):
    """This function for each link of a given team calls a function that retrieves statistics of the team's players from the link. It accumulates data and returns it as a DataFrame"""
    all_league_players = pd.DataFrame()
    for link in team_links:
        sleep(3)
        # downloading relevant statistics from each team and adding them to the accumulating DataFrame
        all_league_players = pd.concat(
            [all_league_players, get_team_stats(link)], ignore_index=True)

    # removal of empty spaces from the DataFrame (it's not about the lack of statistics, but the error of the page etc.)
    all_league_players = all_league_players.replace(
        '\n', '', regex=True).drop(b'\xc2\xa0'.decode(), axis=1)

    # setting new columns' names in DataFrame
    all_league_players.columns = NEW_COLUMNS
    for column_name in NEW_COLUMNS[2:-1]:
        all_league_players[column_name] = pd.to_numeric(
            all_league_players[column_name], errors='coerce')

    # removing unnecessary spaces before and after the item name
    all_league_players['position'] = [position_name.strip()
                                      for position_name in all_league_players['position']]

    # fix indexing in DataFrame
    all_league_players = all_league_players.reset_index(drop=True)

    return all_league_players


def get_team_stats(link):
    """This function fetches the team page for each link, reads the player stats tables and returns a DataFrame"""
    # downloading the web page
    current_data = requests.get(link)

    # processing our html page using the BeautifulSoup class and selecting the appropriate table
    current_soup = BeautifulSoup(
        current_data.text, features='html.parser')
    players_panel = current_soup.select('table.squadPane')
    tag = players_panel[0]

    # getting the contents of the table cells on the page 
    headers = [th.get_text() for th in tag.find_all('th')]
    rows = []
    for tr in tag.find_all('tr'):
        rows.append([td.get_text() for td in tr.find_all('td')])

    #creating the final ordered DataFrame
    players = pd.DataFrame(rows, columns=headers)
    players = players.iloc[1:]

    # Adding the name of their club to the player data
    players['club'] = [get_team_name(link)]*len(players)
    return players


def get_team_name(link):
    """This function searches for the name of the club in the link and returns its name."""
    club_name = re.findall(r'/([^/]+)/$', link)[0].replace('-', ' ')
    print(club_name)
    return club_name


def main():
    get_all_players_season_22_23(TOP_LEAGUES_URLS, CSV_NAMES)


if __name__ == '__main__':
    main()
