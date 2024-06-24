""" SQLAlchemy models for the tables. """

from sqlalchemy import Column, Integer, String
from src.db.session import Base

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, index=True, nullable=False)
