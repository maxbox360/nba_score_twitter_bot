class TweetComposition:

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