""" Pydantic models for request validation and response formatting. """

import re
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, field_validator
from tracker_db.models import format_duration
from src.resources.errors import (
    CategoryNameIsTooLong, DescriptionIsTooLong, EmptyCategoryNameError,
    EmptyDescriptionError, EmptyTimestampError, TimestampFieldError)

UNIX_TIME = re.compile(r'\s*-?\d+(\.\d*)?\s*')


def timestamp_from_text(value):
    """Reject numbers, which pydantic would otherwise read as Unix time."""
    if isinstance(value, (bool, int, float)) or (
            isinstance(value, str) and UNIX_TIME.fullmatch(value)):
        raise ValueError(TimestampFieldError.DETAIL.value)
    return value


class TaskBase(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration: Optional[str] = None

class NewTask(TaskBase):
    description: str
    timestamp: datetime
    category_id: Optional[int] = None

    @field_validator('description')
    def description_not_empty(v):
        if v == '':
            raise ValueError(EmptyDescriptionError.DETAIL.value)
        return v

    @field_validator('description')
    def description_max_length(v):
        if len(v) > 50:
            raise ValueError(DescriptionIsTooLong.DETAIL.value)
        return v

    @field_validator('timestamp', mode='before')
    def timestamp_is_valid(v):
        return timestamp_from_text(v)


class FinishedTask(TaskBase):
    id: int
    timestamp: datetime

    @field_validator('timestamp', mode='before')
    def timestamp_is_valid(v):
        return timestamp_from_text(v)

class TaskStartedResponse(BaseModel):
    id: int

class TaskFinishedResponse(BaseModel):
    duration: str

    @field_validator('duration', mode='before')
    def duration_as_text(v):
        return format_duration(v) if isinstance(v, timedelta) else v


def description_is_valid(value: str) -> str:
    if value == '':
        raise ValueError(EmptyDescriptionError.DETAIL.value)
    if len(value) > 50:
        raise ValueError(DescriptionIsTooLong.DETAIL.value)
    return value


def category_name_is_valid(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(EmptyCategoryNameError.DETAIL.value)
    if len(value) > 50:
        raise ValueError(CategoryNameIsTooLong.DETAIL.value)
    return value


class CategoryCreate(BaseModel):
    name: str

    @field_validator('name')
    def name_is_valid(v):
        return category_name_is_valid(v)


class CategoryUpdate(BaseModel):
    """Only the fields present in the request are changed."""
    name: Optional[str] = None
    archived: Optional[bool] = None

    @field_validator('name')
    def name_is_valid(v):
        return None if v is None else category_name_is_valid(v)


class CategoryResponse(BaseModel):
    id: int
    name: str
    archived: bool


class TaskResponse(BaseModel):
    id: int
    description: str
    category_id: Optional[int] = None
    start_timestamp: Optional[datetime] = None
    finish_timestamp: Optional[datetime] = None
    duration: Optional[str] = None

    @field_validator('duration', mode='before')
    def duration_as_text(v):
        return format_duration(v) if isinstance(v, timedelta) else v


class TaskUpdate(BaseModel):
    """Only the fields present in the request are changed; null clears an optional field."""
    description: Optional[str] = None
    category_id: Optional[int] = None
    start_timestamp: Optional[datetime] = None
    finish_timestamp: Optional[datetime] = None

    @field_validator('description')
    def description_check(v):
        if v is None:
            raise ValueError(EmptyDescriptionError.DETAIL.value)
        return description_is_valid(v)

    @field_validator('start_timestamp', mode='before')
    def start_is_valid(v):
        if v is None:
            raise ValueError(EmptyTimestampError.DETAIL.value)
        return timestamp_from_text(v)

    @field_validator('finish_timestamp', mode='before')
    def finish_is_valid(v):
        # null reopens the task as the active one
        return None if v is None else timestamp_from_text(v)
