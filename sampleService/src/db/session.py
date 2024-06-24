""" Creating db session. """
from src.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

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
