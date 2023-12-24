import tweepy
import pandas as pd
import requests
pd.set_option('display.max_columns', None)
import os


# noinspection PyMethodMayBeStatic
class NBA:

    def __init__(self, api_key, api_secret_key, access_token, access_token_secret):
        # User-based authentication (API keys and access tokens)
        self.user_api = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret_key,
                             access_token=access_token, access_token_secret=access_token_secret)

    def get_ordinal_suffix(self, number):
        if 10 <= number % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
        return suffix


    def customize_nba_url(self, website, stats, season_type, season):
        url = f'{website}/stats/leagueLeaders?ActiveFlag=No&LeagueID=00&PerMode=Totals&Scope=S&' \
              f'Season={season}Time&SeasonType={season_type}Season&StatCategory={stats}'
        return url

    def fetch_nba_all_time_scoring(self, url):
        r = requests.get(url=url).json()
        table_headers = r['resultSet']['headers']
        table = pd.DataFrame(r['resultSet']['rowSet'], columns=table_headers)

        return table[:250]


    def save_table_to_file(self, table, filename):
        table.to_csv(filename, index=False)


    def load_table_from_file(self, filename):
        if os.path.exists(filename):
            return pd.read_csv(filename)

    # TODO: Fix Tweet authentication issue
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

            previous_rank = previous_table.loc[previous_table['PLAYER_ID'] == player_id, 'PTS_RANK'].values
            if len(previous_rank) > 0 and current_rank < previous_rank[0]:
                passed_players = previous_table[
                    (previous_table['PTS_RANK'] >= current_rank) & (previous_table['PTS_RANK'] < previous_rank[0])]
                passed_players_names = passed_players['PLAYER_NAME'].tolist()

                ordinal_suffix = self.get_ordinal_suffix(current_rank)
                try:
                    tweet = f"{player_name} has become the {current_rank}{ordinal_suffix} ranked scorer all time in NBA history. " \
                        f"He has scored {points:,} points in his career, passing: {', '.join(passed_players_names)}"

                    self.user_api.create_tweet(text=tweet)
                except tweepy.TweepyException as e:
                    print(f"Error posting tweet: {e}")


    def main(self):
        """Keeping this commented out code for debugging purposes"""
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

        website = 'https://stats.nba.com'
        stats = 'PTS'
        season_type = 'Regular%20'
        season = 'ALL%20'

        url = self.customize_nba_url(website=website, stats=stats, season_type=season_type, season=season)

        # # Get the file names
        # current_week_filename = 'nba_all_time_scoring_current_week.csv'
        # previous_week_filename = 'nba_all_time_scoring_previous_week.csv'
        #
        # # Create the new table and grab the previous week table
        # current_table = self.fetch_nba_all_time_scoring(url)
        # previous_table = self.load_table_from_file(previous_week_filename)
        #
        # # Save the new data to the current_week file
        # self.save_table_to_file(current_table, current_week_filename)
        self.compare_tables(current_table, previous_table)

        # # Save this week's table to previous file so we can compare next week
        # self.save_table_to_file(current_table, previous_week_filename)
