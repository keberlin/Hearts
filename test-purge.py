from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_

from database import db_init
from logger import logger
from model import GameModel, HandModel, PassingModel, PlayerModel

session = db_init()

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
entries = query.all()
for entry in entries[:50]:
    print(f"entry: {entry.dealt} {entry.direction} {entry.passed} {entry.points} {entry.row}")
