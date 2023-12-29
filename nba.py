from requests_oauthlib import OAuth1Session
import pandas as pd
import requests
pd.set_option('display.max_columns', None)
import os
import json


# noinspection PyMethodMayBeStatic
class NBA:

    def __init__(self, consumer_key, consumer_secret, access_token, token_secret):
        # User-based authentication (API keys and access tokens)
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.token_secret = token_secret

        # Get request token
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print(
                "There may have been an issue with the consumer_key or consumer_secret you entered."
            )

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got OAuth token: %s" % resource_owner_key)

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: %s" % authorization_url)
        verifier = input("Paste the PIN here: ")

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        # Make the request
        self.oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )


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
                if len(passed_players_names) > 1:
                    # If there are multiple passed players, add 'and' before the last name
                    passed_players_names[-1] = 'and ' + passed_players_names[-1]

                tweet = f"{player_name} has become the {current_rank}{ordinal_suffix} ranked scorer all time in NBA history. " \
                        f"He has scored {points:,} points in his career, passing: {', '.join(passed_players_names)}"

                payload = {"text": tweet}

                # Making the request
                response = self.oauth.post(
                    "https://api.twitter.com/2/tweets",
                    json=payload,
                )

                if response.status_code != 201:
                    raise Exception(
                        "Request returned an error: {} {}".format(response.status_code, response.text)
                    )

                print("Response code: {}".format(response.status_code))

                # Saving the response as JSON
                json_response = response.json()
                print(json.dumps(json_response, indent=4, sort_keys=True))


    def main(self):
        """Keeping this commented out code for debugging purposes"""
        # # Example of current week's table (replace this with your actual data)
        # current_data = {
        #     'PLAYER_ID': [1, 5, 2, 3, 4],
        #     'PLAYER_NAME': ['LeBron James', 'Dirk Nowitzki', 'Karl Malone', 'Kobe Bryant', 'Michael Jordan'],
        #     'PTS_RANK': [1, 2, 3, 4, 5],
        #     'PTS': [35291, 33644, 33643, 32292, 31419]
        # }
        #
        # current_table = pd.DataFrame(current_data)
        #
        # # Example of previous week's table (replace this with your actual data)
        # previous_data = {
        #     'PLAYER_ID': [1, 2, 3, 4, 5],
        #     'PLAYER_NAME': ['LeBron James', 'Karl Malone', 'Kobe Bryant', 'Michael Jordan', 'Dirk Nowitzki'],
        #     'PTS_RANK': [1, 2, 3, 4, 5],
        #     'PTS': [36928, 33643, 32292, 31419, 31129]
        # }
        #
        # previous_table = pd.DataFrame(previous_data)

        website = 'https://stats.nba.com'
        stats = 'PTS'
        season_type = 'Regular%20'
        season = 'ALL%20'

        url = self.customize_nba_url(website=website, stats=stats, season_type=season_type, season=season)

        # Get the file names
        current_week_filename = 'nba_all_time_scoring_current_week.csv'
        previous_week_filename = 'nba_all_time_scoring_previous_week.csv'

        # Create the new table and grab the previous week table
        current_table = self.fetch_nba_all_time_scoring(url)
        previous_table = self.load_table_from_file(previous_week_filename)

        # Save the new data to the current_week file
        self.save_table_to_file(current_table, current_week_filename)
        self.compare_tables(current_table, previous_table)

        # Save this week's table to previous file so we can compare next week
        self.save_table_to_file(current_table, previous_week_filename)
