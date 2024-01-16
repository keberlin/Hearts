from sqlalchemy import Integer, String

from database import db


class PassingModel(db.Model):
    __tablename__ = "passing"
    # __table_args__ = {"schema":"wordpicker"}

    dealt = db.Column("dealt", String(13 * 2), primary_key=True, nullable=False)
    passed = db.Column("passed", String(3 * 2), nullable=False)
    points = db.Column("points", Integer, nullable=False, default=0)
