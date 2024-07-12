""" Creating db session. """

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import settings

db_url = settings.get_db_url
engine = create_engine(db_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind = engine)

Base = declarative_base()

def get_db():
    ''' Create db session. '''

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
