from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_

from database import db_init, HEARTS_DB_URI
from logger import logger
from model import GameModel, HandModel, PassingModel, PlayerModel

session = db_init(HEARTS_DB_URI)

if False:
    print("Checking hands..")
    entries = (
        session.query(HandModel.playing, HandModel.turns, HandModel.points, func.count(HandModel.id))
        .group_by(HandModel.playing, HandModel.turns, HandModel.points)
        .having(func.count(HandModel.id) > 1)
        .order_by(func.count(HandModel.id).desc())
        .all()
    )
    prev = None
    for entry in entries:
        print(f"entry: {entry.playing} {entry.turns} {entry.points}")
        if prev and entry.playing == prev.playing and entry.turns == prev.turns:
            print("Duplicate..")
        prev = entry

print("Checking passing..")
subquery = session.query(
    PassingModel,
    func.row_number()
    .over(
        partition_by=(PassingModel.dealt, PassingModel.direction),
        order_by=(PassingModel.dealt, PassingModel.direction, PassingModel.points),
    )
    .label("row"),
).subquery()
query = session.query(subquery).filter(subquery.c.row >= 3)
print(str(query))
entries = query.all()
prev = None
for entry in entries[:50]:
    print(f"entry: {entry.dealt} {entry.direction} {entry.passed} {entry.points} {entry.row}")
    if prev and entry.dealt == prev.dealt and entry.direction == prev.direction:
        print("Duplicate..")
    prev = entry
