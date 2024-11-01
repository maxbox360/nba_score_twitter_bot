import os

import pandas as pd
import requests


class NBAUtils:
    @staticmethod
    def customize_nba_url(info):
        url = f'{info["website"]}/stats/leagueLeaders?ActiveFlag=No&LeagueID=00&PerMode=Totals&Scope=S&' \
              f'Season={info["season"]}Time&SeasonType={info["season_type"]}Season&StatCategory={info["stats"]}'
        return url

    @staticmethod
    def fetch_nba_data(url):
        r = requests.get(url=url).json()
        table_headers = r['resultSet']['headers']
        table = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)
        return table[:250]

    @staticmethod
    def update_table(table, filename):
        table.to_csv(filename, index=False)

    @staticmethod
    def load_table(filename):
        if os.path.exists(filename):
            return pd.read_csv(filename)
