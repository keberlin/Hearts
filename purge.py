from sqlalchemy import and_, func, or_

from database import db_init, HEARTS_DB_URI
from logger import logger
from model import GameModel, HandModel, PassingModel, PlayerModel

session = db_init(HEARTS_DB_URI)

entries = (
    session.query(func.count(HandModel.id), HandModel.playing, HandModel.turns, HandModel.points)
    .group_by(HandModel.playing, HandModel.turns, HandModel.points)
    .having(func.count(HandModel.id) > 1)
    .order_by(HandModel.playing, HandModel.turns, HandModel.points)
    .all()
)
prev = None
for entry in entries:
    print(f"entry: {entry.playing} {entry.turns} {entry.points}")
    if prev and entry.playing == prev.playing and entry.turns == prev.turns:
        print("Duplicate..")
    prev = entry

entries = (
    session.query(func.count(PassingModel.id), PassingModel.dealt, PassingModel.direction, PassingModel.points)
    .filter(PassingModel.dealt.startswith("2C"))
    .group_by(PassingModel.dealt, PassingModel.direction, PassingModel.points)
    .having(func.count(PassingModel.id) > 1)
    .order_by(PassingModel.dealt, PassingModel.direction, PassingModel.points)
    .all()
)
prev = None
for entry in entries:
    print(f"entry: {entry.dealt} {entry.direction} {entry.points}")
    if prev and entry.dealt == prev.dealt and entry.direction == prev.direction:
        print("Duplicate..")
    prev = entry
