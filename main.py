import pandas as pd
import requests
pd.set_option('display.max_columns', None)
import time
import numpy as np
import os

url = 'https://stats.nba.com/stats/leagueLeaders?ActiveFlag=No&LeagueID=00&PerMode=Totals&Scope=S&Season=All%20Time&SeasonType=Regular%20Season&StatCategory=PTS'

def fetch_nba_all_time_scoring(url):
    r = requests.get(url=url).json()
    table_headers = r['resultSet']['headers']
    table = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)

    return table


def save_table_to_file(table, filename):
    table.to_csv(filename, index=False)


def load_table_from_file(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)


def compare_tables(current_table, previous_table):
    if previous_table is None:
        print("No previous data found. Saving current data.")
        return

    changed_players = current_table.merge(previous_table, on='PLAYER_ID', how='outer', suffixed=('_current', '_previous'))
    changed_players = changed_players[changed_players['PTS_current'] != changed_players['PTS_previous']]

    if not changed_players.empty:
        print("Changes in rankings found:")
        print(changed_players[['PLAYER_ID', 'PLAYER_NAME_current', 'PTS_current', 'PTS_previous']])
    else:
        print("No changes in rankings found.")


def main():
    current_week_filename = 'nba_all_time_scoring_current_week.csv'
    previous_week_filename = 'nba_all_time_scoring_previous_week.csv'

    current_table = fetch_nba_all_time_scoring(url)

    previous_table = load_table_from_file(previous_week_filename)

    save_table_to_file(current_table, current_week_filename)

    compare_tables(current_table, previous_table)


if __name__ == "__main__":
    main()