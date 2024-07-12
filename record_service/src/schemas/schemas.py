""" Pydantic models for request validation and response formatting. """

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from src.resources.errors import EmptyDescriptionError, DescriptionIsTooLong, TimestampFieldError

class TaskBase(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration: Optional[str] = None

class NewTask(TaskBase):
    description: str
    timestamp: datetime

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

    @field_validator('timestamp')
    def timestamp_is_valid(v):
        input_value = re.match(r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d', str(v))[0]

        if datetime.strptime(input_value, '%Y-%m-%d %H:%M:%S').date() < datetime.now().date():
            raise ValueError(TimestampFieldError.DETAIL.value)
        return v

class FinishedTask(TaskBase):
    id: int
    timestamp: datetime

class TaskStartedResponse(BaseModel):
    id: int

class TaskFinishedResponse(BaseModel):
    duration: str
