class PlayerRankings:
    @staticmethod
    def get_ordinal_suffix(number):
        if 10 <= number % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
        return suffix

    @staticmethod
    def get_passed_player(players_passed_names, points, current_table):
        passed_players_info = []

        for passed_player_name in players_passed_names:
            passed_player = current_table.loc[current_table['PLAYER_NAME'] == passed_player_name]
            passed_rank = passed_player['PTS_RANK'].values[0]
            passed_points = passed_player['PTS'].values[0]
            points_difference = points - passed_points
            passed_players_info.append((passed_player_name, passed_rank, points_difference))

        return passed_players_info

    @staticmethod
    def get_next_player(current_rank, points, current_table):
        try:
            next_rank = current_rank - 1
            next_player = current_table.loc[current_table['PTS_RANK'] == next_rank]

            if not next_player.empty:
                next_name = next_player['PLAYER_NAME'].values[0]
                next_player_rank = next_player['PTS_RANK'].values[0]
                next_player_pts = next_player['PTS'].values[0]
                difference_to_next = f"{(next_player_pts - points + 1):,}"
            else:
                next_name = next_player['PLAYER_NAME'].values[0]
                next_player_rank = next_player['PTS_RANK'].values[0]
                next_player_pts = next_player['PTS'].values[0]
                difference_to_next = f"{(next_player_pts - points + 1):,}"

            return next_name, next_player_rank, difference_to_next
        except IndexError:
            print("IndexError: Skipping to the next player.")
            return 'No Player available', 0, "N/A"