from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

HEARTS_DB_URI = "postgresql://postgres:postgres@localhost:5432/hearts"

db = SQLAlchemy()


def db_init(uri=HEARTS_DB_URI):
    engine = create_engine(uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
