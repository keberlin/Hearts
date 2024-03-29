from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, String

from database import db


class PlayerModel(db.Model):
    __tablename__ = "players"

    id = db.Column("id", Integer, Identity(), primary_key=True, nullable=False)
    name = db.Column("name", String, nullable=False)
    url = db.Column("url", String, nullable=True)


class GameModel(db.Model):
    __tablename__ = "games"

    id = db.Column("id", Integer, Identity(), primary_key=True, nullable=False)
    start = db.Column("start", DateTime, nullable=False)
    finish = db.Column("finish", DateTime, nullable=True)
    player_1 = db.Column("player_1", ForeignKey(PlayerModel.id), nullable=True)
    player_2 = db.Column("player_2", ForeignKey(PlayerModel.id), nullable=True)
    player_3 = db.Column("player_3", ForeignKey(PlayerModel.id), nullable=True)
    player_4 = db.Column("player_4", ForeignKey(PlayerModel.id), nullable=True)
    points_1 = db.Column("points_1", Integer, nullable=True)
    points_2 = db.Column("points_2", Integer, nullable=True)
    points_3 = db.Column("points_3", Integer, nullable=True)
    points_4 = db.Column("points_4", Integer, nullable=True)
    position_1 = db.Column("position_1", Integer, nullable=True)
    position_2 = db.Column("position_2", Integer, nullable=True)
    position_3 = db.Column("position_3", Integer, nullable=True)
    position_4 = db.Column("position_4", Integer, nullable=True)


class PassingModel(db.Model):
    __tablename__ = "passing"
    __table_args__ = (Index("passing_idx", "dealt", "direction", unique=False),)

    id = db.Column("id", Integer, Identity(), primary_key=True, nullable=False)
    dealt = db.Column("dealt", String(2 * 13), nullable=False)
    direction = db.Column("direction", Integer, nullable=False)
    passed = db.Column("passed", String(2 * 3), nullable=False)
    points = db.Column("points", Integer, nullable=False)


class HandModel(db.Model):
    __tablename__ = "hands"
    __table_args__ = (Index("hand_idx", "playing", "turns", unique=True),)

    id = db.Column("id", Integer, Identity(), primary_key=True, nullable=False)
    playing = db.Column("playing", String(2 * 13), nullable=False)
    turns = db.Column("turns", String((2 + 2 * 4) * 13 + (13 - 1)), nullable=False)
    points = db.Column("points", Integer, nullable=False)
