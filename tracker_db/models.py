"""SQLAlchemy models for the Tracker database. Schema changes need an Alembic migration."""

import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Uuid, false
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base whose metadata Alembic compares against."""


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    archived: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false())


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    start_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    finish_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    # Set by clients that queue tasks offline; makes resending a task idempotent.
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, nullable=True, unique=True, index=True)

    category: Mapped[Category | None] = relationship()

    @property
    def duration(self) -> timedelta | None:
        """Elapsed time of a finished task; None while it is running."""
        if self.start_timestamp is None or self.finish_timestamp is None:
            return None
        return self.finish_timestamp - self.start_timestamp


def format_duration(value: timedelta | None) -> str | None:
    """Format as HH:MM:SS, the API format of the legacy column; hours may exceed 24."""
    if value is None:
        return None
    total = int(value.total_seconds())
    sign = '-' if total < 0 else ''
    hours, rest = divmod(abs(total), 3600)
    minutes, seconds = divmod(rest, 60)
    return f'{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'
