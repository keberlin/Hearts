from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_

from database import db_init
from logger import logger
from model import GameModel, HandModel, PassingModel, PlayerModel

session = db_init()

now = datetime.utcnow()
start = now - timedelta(hours=1)
session.query(GameModel).filter(GameModel.finish.is_(None), GameModel.start < start).delete()
session.commit()
