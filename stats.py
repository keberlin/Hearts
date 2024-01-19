import logging

from sqlalchemy import and_, or_

from database import db_init, HEARTS_DB_URI
from model import GameModel, PlayerModel

MIN_NUM_GAMES = 5

logger = logging.getLogger()
logging.basicConfig(filename="/var/log/hearts/log", level=logging.DEBUG)

session = db_init(HEARTS_DB_URI)

stats = []

num_games = session.query(GameModel).filter(GameModel.finish.isnot(None)).count()

players = session.query(PlayerModel).all()
for player in players:
    games_played = (
        session.query(GameModel)
        .filter(
            or_(
                GameModel.player_1 == player.id,
                GameModel.player_2 == player.id,
                GameModel.player_3 == player.id,
                GameModel.player_4 == player.id,
            )
        )
        .count()
    )
    if games_played < MIN_NUM_GAMES:
        continue
    games_won = (
        session.query(GameModel)
        .filter(
            or_(
                and_(GameModel.player_1 == player.id, GameModel.position_1 == 0),
                and_(GameModel.player_2 == player.id, GameModel.position_2 == 0),
                and_(GameModel.player_3 == player.id, GameModel.position_3 == 0),
                and_(GameModel.player_4 == player.id, GameModel.position_4 == 0),
            )
        )
        .count()
    )
    stats.append((player, games_played, games_won, games_won * 100 / games_played))

stats.sort(key=lambda x: x[3], reverse=True)

print(f"number of games: {num_games}")
print("")
for stat in stats:
    print(f"{stat[3]:2.0f}% played {stat[1]} won {stat[2]} player: {stat[0].id} {stat[0].name}")
