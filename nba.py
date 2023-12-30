import argparse
import pandas as pd
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

        resource_owner_key, resource_owner_secret = self.utils.user_authentication()
        verifier = self.utils.get_authorization_url(resource_owner_key)
        access_token, access_token_secret = self.utils.get_access_token(resource_owner_key, resource_owner_secret, verifier)
        self.oauth = self.utils.make_request(access_token, access_token_secret)


    def process_players_passed(self, player_name, players_passed_names, current_rank, points):
        ordinal_suffix = self.nba_utils.get_ordinal_suffix(current_rank)

        if len(players_passed_names) == 1:
            tweet = f"{player_name} has become the {current_rank}{ordinal_suffix} ranked scorer all time in NBA history. " \
                    f"He has scored {points:,} points in his career, passing: {players_passed_names[0]}"
        elif len(players_passed_names) == 2:
            tweet = f"{player_name} has become the {current_rank}{ordinal_suffix} ranked scorer all time in NBA history. " \
                    f"He has scored {points:,} points in his career, passing: {players_passed_names[0]} and {players_passed_names[1]}"
        else:
            all_passed_players = ', '.join(players_passed_names[:-1]) + f", and {players_passed_names[-1]}"
            tweet = f"{player_name} has become the {current_rank}{ordinal_suffix} ranked scorer all time in NBA history. " \
                    f"He has scored {points:,} points in his career, passing: {all_passed_players}"

        return tweet


    def check_rank_changes(self, player_id, current_rank, previous_table):
        previous_rank = previous_table.loc[previous_table['PLAYER_ID'] == player_id, 'PTS_RANK'].values
        if len(previous_rank) > 0 and current_rank < previous_rank[0]:
            passed_players = previous_table[
                (previous_table['PTS_RANK'] >= current_rank) & (previous_table['PTS_RANK'] < previous_rank[0])]
            players_passed_names = passed_players['PLAYER_NAME'].tolist()

            return players_passed_names

        return None


    def compare_tables(self, current_table, previous_table):
        if previous_table is None:
            print("No previous data found. Saving current data.")
            return

        # Iterate through each player in the current table to find changes in ranking
        for _, row in current_table.iterrows():
            player_id = row['PLAYER_ID']
            player_name = row['PLAYER_NAME']
            current_rank = row['PTS_RANK']
            points = row['PTS']

            passed_players = self.check_rank_changes(player_id, current_rank, previous_table)
            if passed_players:
                tweet = self.process_players_passed(player_name, passed_players, current_rank, points)
                payload = {"text": tweet}

                # Making the request
                response = self.oauth.post(
                    "https://api.twitter.com/2/tweets",
                    json=payload,
                )

                if response.status_code != 201:
                    raise ValueError(
                        f"Failed to post tweet for {player_name}. Status Code: {response.status_code}. Response: {response.text}"
                    )

                print("Response code: {}".format(response.status_code))

                # Saving the response as JSON
                json_response = response.json()
                print(json.dumps(json_response, indent=4, sort_keys=True))


    def main(self):
        parser = argparse.ArgumentParser(description="Running nba.py in Debug Mode")
        parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
        args = parser.parse_args()
        if args.debug:
            print("Debugging mode is active")
            # Example of current week's table (replace this with your actual data)
            current_data = {
                'PLAYER_ID': [1, 5, 2, 3, 4],
                'PLAYER_NAME': ['LeBron James', 'Dirk Nowitzki', 'Karl Malone', 'Kobe Bryant', 'Michael Jordan'],
                'PTS_RANK': [1, 2, 3, 4, 5],
                'PTS': [35291, 33644, 33643, 32292, 31419]
            }

            current_table = pd.DataFrame(current_data)

            # Example of previous week's table (replace this with your actual data)
            previous_data = {
                'PLAYER_ID': [1, 2, 3, 4, 5],
                'PLAYER_NAME': ['LeBron James', 'Karl Malone', 'Kobe Bryant', 'Michael Jordan', 'Dirk Nowitzki'],
                'PTS_RANK': [1, 2, 3, 4, 5],
                'PTS': [36928, 33643, 32292, 31419, 31129]
            }

            previous_table = pd.DataFrame(previous_data)
            self.compare_tables(current_table, previous_table)
        else:
            website = 'https://stats.nba.com'
            stats = 'PTS'
            season_type = 'Regular%20'
            season = 'ALL%20'

            url = self.nba_utils.customize_nba_url(website=website, stats=stats, season_type=season_type, season=season)

            # Get the file names
            current_week_filename = 'nba_all_time_scoring_current_week.csv'
            previous_week_filename = 'nba_all_time_scoring_previous_week.csv'

            # Create the new table and grab the previous week table
            current_table = self.nba_utils.fetch_nba_all_time_scoring(url)
            previous_table = self.nba_utils.load_table_from_file(previous_week_filename)

            # Save the new data to the current_week file
            self.nba_utils.save_table_to_file(current_table, current_week_filename)
            self.compare_tables(current_table, previous_table)

            # Save this week's table to previous file, so we can compare next week
            self.nba_utils.save_table_to_file(current_table, previous_week_filename)
