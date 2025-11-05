import os
from time import sleep

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
        retries = 5
        backoff = 2
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url=url, timeout=10)
                response.raise_for_status()
                r = response.json()

                if 'resultSet' not in r:
                    print(f"[Attempt {attempt}] resultSet missing. Response: {r}")

                table_headers = r['resultSet']['headers']
                table = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)
                return table[:250]
            except (requests.RequestException, ValueError) as e:
                wait = backoff * (2 ** (attempt - 1))
                print(f"[Attempt {attempt}] Failed: {e} Retrying in {wait}s...")
                sleep(wait)
        raise RuntimeError(f"Failed to fetch NBA data from {url} after {retries} retries")

    @staticmethod
    def update_table(table, filename):
        table.to_csv(filename, index=False)

    @staticmethod
    def load_table(filename):
        if os.path.exists(filename):
            return pd.read_csv(filename)
