import argparse
import os.path
import time

import pandas as pd
from atproto import Client

from nba.nba_utils import NBAUtils
from utils.calculate_ranking import PlayerRankings
from utils.posts import PostComposition

pd.set_option('display.max_columns', None)


class NBA:

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.nba_utils = NBAUtils()
        self.post_comp = PostComposition()
        self.rankings = PlayerRankings()

        parser = argparse.ArgumentParser(description="Running nba_main.py in Debug Mode")
        parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
        self.args = parser.parse_args()

        self.posts = []


    def process_passed_players(self, player_info, passed_players):

        player_name = player_info['player_name']
        current_rank = player_info['current_rank']
        points = player_info['points']
        new_table = player_info['new_table']

        ordinal_suffix = self.rankings.get_ordinal_suffix(player_info['current_rank'])
        players_passed_info = self.rankings.get_passed_player(passed_players, points, new_table)

        next_name, next_player_rank, difference_to_next \
            = self.rankings.get_next_player(current_rank,
                                                        points,
                                                        new_table)
        next_ordinal_suffix = self.rankings.get_ordinal_suffix(next_player_rank)

        post_data = {
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
            post = self.post_comp.single_player_posts(post_data)
        elif len(players_passed_info) == 2:
            post = self.post_comp.two_player_posts(post_data)
        else:
            post = self.post_comp.multi_player_posts(post_data)

        return post

    def check_rank_changes(self, player_id, current_rank, old_table):
        previous_rank = old_table.loc[old_table['PLAYER_ID'] == player_id, 'PTS_RANK'].values
        if len(previous_rank) > 0 and current_rank < previous_rank[0]:
            passed_players = old_table[
                (old_table['PTS_RANK'] >= current_rank) & (old_table['PTS_RANK'] < previous_rank[0])]
            players_passed_names = passed_players['PLAYER_NAME'].tolist()

            return players_passed_names

        return None


    def compose_post(self, new_table, old_table):
        if old_table is None:
            print("No previous data found. Saving current data.")
            return

        self.collect_posts(new_table, old_table)

        # Check if there are any posts before proceeding
        if not self.posts:
            print("No posts to deliver. Exiting")
            return

        self.send_bluesky_post()

    def collect_posts(self, new_table, old_table):
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
                post = self.process_passed_players(player_info, passed_players)
                self.posts.append(post)


    def send_bluesky_post(self):
            client = Client()
            client.login(self.username, self.password)
            # Reverse the order of posts before posting
            self.posts.reverse()

            print(f"There is/are {len(self.posts)} post(s) to send to Bluesky\n")
            for post in self.posts:
                if self.args.debug:
                    print(post)
                else:
                    print(f"post: {post}\n")
                    client.send_post(post)
                    if len(self.posts) > 1:
                        # Wait for 3 minutes between posts
                        minutes = 3 * 60
                        time.sleep(minutes)
            print("All posts sent.")

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
            self.compose_post(new_table, old_table)
        else:
            info = {
                'website': 'https://stats.nba.com',
                'stats': 'PTS',
                'season_type': 'Regular%20',
                'season': 'ALL%20'
            }

            url = self.nba_utils.customize_nba_url(info)

            # Get the file names
            directory_path = os.path.dirname(os.path.realpath(__file__))
            updated_data = os.path.join(directory_path, 'new_nba_scoring_data.csv')
            old_data = os.path.join(directory_path, 'old_nba_scoring_data.csv')

            # Create the new table and grab the previous week table
            new_table = self.nba_utils.fetch_nba_data(url)
            old_table = self.nba_utils.load_table(old_data)

            # Update the current_week file with the new data
            self.nba_utils.update_table(table=new_table, filename=updated_data)
            self.compose_post(new_table, old_table)

            # Update the previous file with this week's table, so we can compare next week
            self.nba_utils.update_table(table=new_table, filename=old_data)
