def get_next_players(post_data):
    next_players = post_data['next_name'].split(', ')
    if len(next_players) >= 3:
        tied_players = ', '.join(next_players[:-1]) + ", and " + next_players[-1]
    elif len(next_players) == 2:
        tied_players = " and ".join(next_players)
    else:
        # This is just the next guy, grab him out of the list
        next_player = next_players[0]
        return next_player
    return tied_players


class PostComposition:

    @staticmethod
    def single_player_posts(post_data):
        next_players = get_next_players(post_data)
        return (
            f"{post_data['player_name']} has become the {post_data['current_rank']}{post_data['ordinal_suffix']} ranked scorer in NBA history. "
            f"He has scored {post_data['points']:,} points in his career, passing: {post_data['players_passed_info'][0][0]}. \n\n"
            f"He needs {post_data['difference_to_next']} points to pass {next_players} "
            f"for {post_data['next_player_rank']}{post_data['next_ordinal_suffix']} all time."
        )

    @staticmethod
    def two_player_posts(post_data):
        next_players = get_next_players(post_data)
        return (
            f"{post_data['player_name']} has become the {post_data['current_rank']}{post_data['ordinal_suffix']} ranked scorer in NBA history. "
            f"He has scored {post_data['points']:,} points in his career, passing: {post_data['players_passed_info'][0][0]} and {post_data['players_passed_info'][1][0]}. \n\n"
            f"He needs {post_data['difference_to_next']} points to pass {next_players} "
            f"for {post_data['next_player_rank']}{post_data['next_ordinal_suffix']} all time."
        )

    @staticmethod
    def multi_player_posts(post_data):
        next_players = get_next_players(post_data)
        all_players = (', '.join(names[0] for names in post_data['players_passed_info'][:-1])
                       + f", and {post_data['players_passed_info'][-1][0]}")

        post = (
            f"{post_data['player_name']} has become the {post_data['current_rank']}{post_data['ordinal_suffix']} ranked scorer in NBA history. "
            f"He has scored {post_data['points']:,} points in his career, passing: {all_players}. \n\n"
            f"He needs {post_data['difference_to_next']} points to pass {next_players} "
            f"for {post_data['next_player_rank']}{post_data['next_ordinal_suffix']} all time."
        )

        # Check if the post exceeds 280 characters
        if len(post) <= 280:
            return post
        else:
            # If it exceeds, mention only the first name and add "and others"
            first_player = post_data['players_passed_info'][0][0]
            return (
                f"{post_data['player_name']} has become the {post_data['current_rank']}{post_data['ordinal_suffix']} ranked scorer in NBA history. "
                f"He has scored {post_data['points']:,} points in his career, passing: {first_player} and others. \n\n"
                f"He needs {post_data['difference_to_next']} points to pass {post_data['next_name']} "
                f"for {post_data['next_player_rank']}{post_data['next_ordinal_suffix']} all time."
            )
