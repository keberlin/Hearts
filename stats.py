import logging

from sqlalchemy import and_, or_

from database import db_init, HEARTS_DB_URI
from model import GameModel, PlayerModel

logger = logging.getLogger()
logging.basicConfig(filename="/var/log/hearts/log", level=logging.DEBUG)

session = db_init(HEARTS_DB_URI)

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

    if games_played:
        print(f"player: {games_won*100/games_played:.0f}% played {games_played} won {games_won} {player.name}")
