from sqlalchemy import DateTime, ForeignKey, Identity, Integer, String

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
    player_1 = db.Column("player_1", ForeignKey(PlayerModel.id), nullable=True)


class PassingModel(db.Model):
    __tablename__ = "passing"

    id = db.Column("id", Integer, Identity(), primary_key=True, nullable=False)
    dealt = db.Column("dealt", String(2 * 13), nullable=False)
    passed = db.Column("passed", String(2 * 3), nullable=False)
    points = db.Column("points", Integer, nullable=False)


class HandModel(db.Model):
    __tablename__ = "hands"

    id = db.Column("id", Integer, Identity(), primary_key=True, nullable=False)
    game = db.Column("game", ForeignKey(GameModel.id), nullable=True)
    player = db.Column("player", ForeignKey(PlayerModel.id), nullable=True)
    dealt = db.Column("dealt", String(2 * 13), nullable=False)
    passed = db.Column("passed", String(2 * 3), nullable=False)
    received = db.Column("received", String(2 * 3), nullable=False)
    playing = db.Column("playing", String(2 * 13), nullable=False)
    turns = db.Column("turns", String((2 + 2 * 4) * 13), nullable=False)
    points = db.Column("points", Integer, nullable=False)
