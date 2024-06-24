""" Defines Pydantic models for request validation and response formatting. """

from typing import Optional
from pydantic import BaseModel, field_validator
from resources.errors import UsernameIsTooLong, EmptyUserNameError

class UserBase(BaseModel):
    username: Optional[str] = None
    id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    
    # @field_validator('id')
    # def id_must_be_int(v):
    #     if v == None:
    #         raise ValueError('unsupported id data type')
    #     return v

class UserCreate(UserBase):
    username: str
    
    @field_validator('username')
    def username_not_empty(v):
        if v == '':
            raise ValueError(EmptyUserNameError.DETAIL.value)
        return v
    
    @field_validator('username')
    def username_max_length(v):
        if len(v) > 50:
            raise ValueError(UsernameIsTooLong.DETAIL.value)
        return v
    
    # @field_validator('username')
    # def username_is_str(v):
    #     print('LLLL')
    #     if not isinstance(v, str):
    #         raise ValueError('custom custom message', 'unsupported username data type')
    #     return v