def ranking(points_player, points_game):
    for i, points in enumerate(sorted(set(points_game))):
        if points_player == points:
            return i
    assert False, f"{points_player} is not in {points_game}"
