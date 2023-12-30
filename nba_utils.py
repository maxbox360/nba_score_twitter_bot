import os
import pandas as pd
import requests


class NBAUtils:

    @staticmethod
    def get_ordinal_suffix(number):
        if 10 <= number % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
        return suffix


    @staticmethod
    def customize_nba_url(website, stats, season_type, season):
        url = f'{website}/stats/leagueLeaders?ActiveFlag=No&LeagueID=00&PerMode=Totals&Scope=S&' \
              f'Season={season}Time&SeasonType={season_type}Season&StatCategory={stats}'
        return url


    @staticmethod
    def fetch_nba_all_time_scoring(url):
        r = requests.get(url=url).json()
        table_headers = r['resultSet']['headers']
        table = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)
        return table[:250]


    @staticmethod
    def save_table_to_file(table, filename):
        table.to_csv(filename, index=False)


    @staticmethod
    def load_table_from_file(filename):
        if os.path.exists(filename):
            return pd.read_csv(filename)
