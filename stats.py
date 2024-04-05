import argparse
from datetime import timedelta
import logging

from sqlalchemy import and_, or_

from database import db_init
from logger import logger
from model import GameModel, HandModel, PassingModel, PlayerModel

session = db_init()

parser = argparse.ArgumentParser(description="Statistics for Hearts card game.")
parser.add_argument("-t", dest="top", type=int, default=20, help="Report top highest scoring players", required=False)
parser.add_argument("-g", dest="min_games", type=int, default=15, help="Minimum number of games played", required=False)
args = parser.parse_args()
top = args.top
min_games = args.min_games

total = 0
games = (
    session.query(
        GameModel.start,
        GameModel.finish,
    )
    .filter(GameModel.finish.isnot(None))
    .all()
)
for game in games:
    total += (game.finish - game.start) / timedelta(milliseconds=1)
count = len(games)

print("")
print(f"number of played games: {count:,}, average game time: {total/count/1000:.2f}s")
print("")

count = session.query(PassingModel).count()

print("")
print(f"number of passing hands recorded: {count:,}")
print("")

count = session.query(HandModel).count()

print("")
print(f"number of hands recorded: {count:,}")
print("")

players = {}
games = (
    session.query(
        GameModel.player_1,
        GameModel.player_2,
        GameModel.player_3,
        GameModel.player_4,
        GameModel.position_1,
        GameModel.position_2,
        GameModel.position_3,
        GameModel.position_4,
    )
    .filter(GameModel.finish.isnot(None))
    .all()
)
for game in games:
    for player, position in zip(
        [game.player_1, game.player_2, game.player_3, game.player_4],
        [game.position_1, game.position_2, game.position_3, game.position_4],
    ):
        if not player in players:
            players[player] = [0, 0]
        players[player][0] += 1
        if position == 0:
            players[player][1] += 1

stats = []
for player, counts in players.items():
    played, won = counts
    if played < min_games:
        continue
    stats.append((player, played, won, won * 100 / played))

stats.sort(key=lambda x: x[3], reverse=True)

for i, stat in enumerate(stats):
    if i == top:
        break
    player = session.query(PlayerModel.name).filter(PlayerModel.id == stat[0]).one()
    print(f"{stat[3]:2.0f}% played {stat[1]} won {stat[2]} player: {stat[0]} {player.name}")
print("")
