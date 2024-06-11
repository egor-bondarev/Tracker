""" Defines Pydantic models for request validation and response formatting. """
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: Optional[str] = None
    id: Optional[int] = None

class  UserCreate(UserBase):
    username: str

class UserResponse(UserBase):
    id: int
