"""Engine and session factory for the application role."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tracker_db.config import Settings

engine = create_engine(Settings().db_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a session and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
