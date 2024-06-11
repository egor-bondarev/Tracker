""" SQLAlchemy models for the tables. """

from sqlalchemy import Column, Integer, String
from db.session import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
