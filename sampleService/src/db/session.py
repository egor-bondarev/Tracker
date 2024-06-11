from core.config import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = settings.get_db_url
engine = create_engine(db_url)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind = engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)