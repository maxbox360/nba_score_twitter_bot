import logging
import os
from time import sleep

import pandas as pd
import requests


logger = logging.getLogger(__name__)


class NBAUtils:
    @staticmethod
    def customize_nba_url(info):
        url = (
            f'{info["website"]}/stats/leagueLeaders?'
            f'ActiveFlag=No&LeagueID=00&PerMode=Totals&Scope=S&'
            f'Season={info["season"]}&SeasonType={info["season_type"]}&'
            f'StatCategory={info["stats"]}'
        )

        return url

    @staticmethod
    def fetch_nba_data(url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/118.0.5993.117 Safari/537.36",
            "Referer": "https://www.nba.com/",
            "Origin": "https://www.nba.com",
        }
        retries = 5
        backoff = 2
        last_error = None

        logger.debug("Fetching NBA data from %s", url)
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code != 200:
                    logger.warning(
                        "NBA API returned status %s on attempt %s. Response: %s",
                        response.status_code,
                        attempt,
                        response.text[:500],
                    )
                response.raise_for_status()
                r = response.json()
                if 'resultSet' not in r:
                    raise ValueError(f"resultSet missing in response: {r}")

                table_headers = r['resultSet']['headers']
                table = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)
                logger.info("Fetched %s NBA rows successfully.", len(table[:250]))
                return table[:250]
            except (requests.RequestException, ValueError) as e:
                last_error = e
                wait = backoff * (2 ** (attempt - 1))
                if attempt < retries:
                    logger.warning(
                        "[Attempt %s/%s] Failed to fetch NBA data: %s. Retrying in %ss...",
                        attempt,
                        retries,
                        e,
                        wait,
                    )
                    sleep(wait)
                else:
                    logger.error(
                        "[Attempt %s/%s] Failed to fetch NBA data: %s",
                        attempt,
                        retries,
                        e,
                        exc_info=True,
                    )
        raise RuntimeError(
            f"Failed to fetch NBA data from {url} after {retries} retries"
        ) from last_error

    @staticmethod
    def update_table(table, filename):
        table.to_csv(filename, index=False)
        logger.debug("Saved table with %s rows to %s", len(table), filename)

    @staticmethod
    def load_table(filename):
        if os.path.exists(filename):
            logger.debug("Loading previous table from %s", filename)
            return pd.read_csv(filename)
        logger.warning("No existing table found at %s", filename)
