import argparse
import sys
import time

import pandas as pd
import requests

from nba_utils import NBAUtils
from utils import Utils
pd.set_option('display.max_columns', None)
import json


# noinspection PyMethodMayBeStatic
class NBA:

    def __init__(self, consumer_key, consumer_secret):
        # User-based authentication (API keys and access tokens)
        self.nba_utils = NBAUtils()
        self.utils = Utils(consumer_key, consumer_secret)

        parser = argparse.ArgumentParser(description="Running nba.py in Debug Mode")
        parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
        self.args = parser.parse_args()
        self.oauth = None

        self.tweets = []

        if self.args.debug:
            print("Debugging\n")
        else:
            resource_owner_key, resource_owner_secret = self.utils.user_auth()
            verifier = self.utils.get_auth_url(resource_owner_key)
            access_token, access_token_secret = self.utils.get_access_token(resource_owner_key,
                                                                            resource_owner_secret,
                                                                            verifier)
            self.oauth = self.utils.make_request(access_token, access_token_secret)

    def process_passed_players(self, player_info, passed_players):

        player_name = player_info['player_name']
        current_rank = player_info['current_rank']
        points = player_info['points']
        new_table = player_info['new_table']

        ordinal_suffix = self.nba_utils.get_ordinal_suffix(player_info['current_rank'])
        players_passed_info = self.nba_utils.calculate_passed_players_info(passed_players, points, new_table)

        next_name, next_player_rank, difference_to_next \
            = self.nba_utils.calculate_next_player_info(current_rank,
                                                        points,
                                                        new_table)
        next_ordinal_suffix = self.nba_utils.get_ordinal_suffix(next_player_rank)

        tweet_data = {
            'player_name': player_name,
            'current_rank': current_rank,
            'ordinal_suffix': ordinal_suffix,
            'points': points,
            'difference_to_next': difference_to_next,
            'next_name': next_name,
            'next_player_rank': next_player_rank,
            'next_ordinal_suffix': next_ordinal_suffix,
            'players_passed_info': players_passed_info
        }

        if len(players_passed_info) == 1:
            tweet = self.nba_utils.single_player_tweets(tweet_data)
        elif len(players_passed_info) == 2:
            tweet = self.nba_utils.two_player_tweets(tweet_data)
        else:
            tweet = self.nba_utils.multi_player_tweets(tweet_data)

        return tweet


    def check_rank_changes(self, player_id, current_rank, old_table):
        previous_rank = old_table.loc[old_table['PLAYER_ID'] == player_id, 'PTS_RANK'].values
        if len(previous_rank) > 0 and current_rank < previous_rank[0]:
            passed_players = old_table[
                (old_table['PTS_RANK'] >= current_rank) & (old_table['PTS_RANK'] < previous_rank[0])]
            players_passed_names = passed_players['PLAYER_NAME'].tolist()

            return players_passed_names

        return None

    def post_tweet(self, payload):
        try:
            # Making the request
            response = self.oauth.post(
                "https://api.twitter.com/2/tweets",
                json=payload,
            )
            response.raise_for_status()  # Raise HTTPError for bad responses

            print("Tweet posted successfully. Response code: {}".format(response.status_code))

            # Saving the response as JSON
            json_response = response.json()
            print(json.dumps(json_response, indent=4, sort_keys=True))

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("403 error: Skipped tweet due to repeated content")
                return
            else:
                raise ValueError(
                    f"Failed to post tweet. Status Code: {e.response.status_code}. Response: {e.response.text}"
                )

        if not self.tweets:
            print("There are no more tweets to post. Exiting")
            sys.exit()

        # Space tweets out instead of posting all in one batch
        minutes = 60 * 5
        time.sleep(minutes)

    def compose_tweet(self, new_table, old_table):
        if old_table is None:
            print("No previous data found. Saving current data.")
            return

        # Iterate through each player in the current table to find changes in ranking
        for _, row in new_table.iterrows():
            player_info = {
                'player_id': row['PLAYER_ID'],
                'player_name': row['PLAYER_NAME'],
                'current_rank': row['PTS_RANK'],
                'points': row['PTS'],
                'old_table': old_table,
                'new_table': new_table
            }

            passed_players = self.check_rank_changes(player_info['player_id'], player_info['current_rank'],
                                                     player_info['old_table'])
            if passed_players:
                tweet = self.process_passed_players(player_info, passed_players)
                self.tweets.append(tweet)

        # Reverse the order of tweets before posting
        self.tweets.reverse()
        for tweet in self.tweets:
            payload = {"text": tweet}
            if self.args.debug:
                print(tweet)
            else:
                self.post_tweet(payload)


    def main(self):
        if self.args.debug:
            # Example of current week table
            new_data = {
                'PLAYER_ID': [1, 5, 2, 3, 4],
                'PLAYER_NAME': ['LeBron James', 'Dirk Nowitzki', 'Karl Malone', 'Kobe Bryant', 'Michael Jordan'],
                'PTS_RANK': [1, 2, 3, 4, 5],
                'PTS': [35291, 33644, 33643, 32292, 31419]
            }

            new_table = pd.DataFrame(new_data)

            # Example of previous week table
            old_data = {
                'PLAYER_ID': [1, 2, 3, 4, 5],
                'PLAYER_NAME': ['LeBron James', 'Karl Malone', 'Kobe Bryant', 'Michael Jordan', 'Dirk Nowitzki'],
                'PTS_RANK': [1, 2, 3, 4, 5],
                'PTS': [36928, 33643, 32292, 31419, 31129]
            }

            old_table = pd.DataFrame(old_data)
            self.compose_tweet(new_table, old_table)
        else:
            info = {
                'website': 'https://stats.nba.com',
                'stats': 'PTS',
                'season_type': 'Regular%20',
                'season': 'ALL%20'
            }

            url = self.nba_utils.customize_nba_url(info)

            # Get the file names
            updated_data = 'new_nba_scoring_data.csv'
            old_data = 'old_nba_scoring_data.csv'

            # Create the new table and grab the previous week table
            new_table = self.nba_utils.fetch_nba_data(url)
            old_table = self.nba_utils.load_table(old_data)

            # Update the current_week file with the new data
            self.nba_utils.update_table(table=new_table, filename=updated_data)
            self.compose_tweet(new_table, old_table)

            # Update the previous file with this week's table, so we can compare next week
            self.nba_utils.update_table(table=new_table, filename=old_data)
