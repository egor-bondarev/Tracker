""" Pydantic models for request validation and response formatting. """

from typing import Optional
from pydantic import BaseModel, field_validator
from src.resources.errors import EmptyDescriptionError, EmptyTimestampError, DescriptionIsTooLong

class TaskBase(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    timestamp: Optional[str] = None
    is_task_finished: Optional[bool] = None
    duration: Optional[str] = None

class NewTask(TaskBase):
    description: str
    timestamp: str
    is_task_finished: bool

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
    def timestamp_not_empty(v):
        if v == '':
            raise ValueError(EmptyTimestampError.DETAIL.value)
        return v

class FinishedTask(TaskBase):
    id: int
    timestamp: str

    @field_validator('timestamp')
    def timestamp_not_empty(v):
        if v == '':
            raise ValueError(EmptyTimestampError.DETAIL.value)
        return v

class TaskStartedResponse(TaskBase):
    id: int

class TaskFinishedResponse(TaskBase):
    duration: str
