""" SQLAlchemy models for the tables. """

from sqlalchemy import Column, Integer, String, DateTime
from src.db.session import Base

class Task(Base):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, unique=False, nullable=False)
    start_timestamp = Column(DateTime, unique=False, nullable=True)
    finish_timestamp = Column(DateTime, unique=False, nullable=True)
    duration = Column(String, unique=False, nullable=True)

    def __eq__(self, task):
        return self.id == task.id and \
            self.description == task.description and \
                self.start_timestamp == task.start_timestamp and \
                    self.finish_timestamp == task.finish_timestamp and \
                        self.duration == task.duration
