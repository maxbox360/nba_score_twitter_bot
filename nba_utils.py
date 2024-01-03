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
    def calculate_passed_players_info(players_passed_names, points, current_table):
        passed_players_info = []

        for passed_player_name in players_passed_names:
            passed_player = current_table.loc[current_table['PLAYER_NAME'] == passed_player_name]
            passed_rank = passed_player['PTS_RANK'].values[0]
            passed_points = passed_player['PTS'].values[0]
            points_difference = points - passed_points
            passed_players_info.append((passed_player_name, passed_rank, points_difference))

        return passed_players_info

    @staticmethod
    def calculate_next_player_info(current_rank, points, current_table):
        next_rank = current_rank - 1
        next_player = current_table.loc[current_table['PTS_RANK'] == next_rank]
        next_name = next_player['PLAYER_NAME'].values[0]

        next_player_rank = next_player['PTS_RANK'].values[0]
        next_player_pts = next_player['PTS'].values[0]
        difference_to_next = f"{(next_player_pts - points + 1):,}"

        return next_name, next_player_rank, difference_to_next

    @staticmethod
    def single_player_tweets(tweet_data):
        return (
            f"{tweet_data['player_name']} has become the {tweet_data['current_rank']}{tweet_data['ordinal_suffix']} ranked scorer all time in NBA history. "
            f"He has scored {tweet_data['points']:,} points in his career, passing: {tweet_data['players_passed_info'][0][0]}. \n\n"
            f"He is {tweet_data['difference_to_next']} points away from passing {tweet_data['next_name']} "
            f"for {tweet_data['next_player_rank']}{tweet_data['next_ordinal_suffix']} all time."
        )

    @staticmethod
    def two_player_tweets(tweet_data):
        return (
            f"{tweet_data['player_name']} has become the {tweet_data['current_rank']}{tweet_data['ordinal_suffix']} ranked scorer all time in NBA history. "
            f"He has scored {tweet_data['points']:,} points in his career, passing: {tweet_data['players_passed_info'][0][0]} and {tweet_data['players_passed_info'][1][0]}. \n\n"
            f"He is {tweet_data['difference_to_next']} points away from passing {tweet_data['next_name']} "
            f"for {tweet_data['next_player_rank']}{tweet_data['next_ordinal_suffix']} all time."
        )

    @staticmethod
    def multi_player_tweets(tweet_data):
        all_players = ', '.join(names[0] for names in tweet_data['players_passed_info'][
                                                      :-1]) + f", and {tweet_data['players_passed_info'][-1][0]}"
        return (
            f"{tweet_data['player_name']} has become the {tweet_data['current_rank']}{tweet_data['ordinal_suffix']} ranked scorer all time in NBA history. "
            f"He has scored {tweet_data['points']:,} points in his career, passing: {all_players}. \n\n"
            f"He is {tweet_data['difference_to_next']} points away from passing {tweet_data['next_name']} "
            f"for {tweet_data['next_player_rank']}{tweet_data['next_ordinal_suffix']} all time."
        )


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
    def save_table(table, filename):
        table.to_csv(filename, index=False)


    @staticmethod
    def load_table(filename):
        if os.path.exists(filename):
            return pd.read_csv(filename)
