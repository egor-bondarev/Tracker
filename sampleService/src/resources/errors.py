from fastapi import HTTPException
from enum import Enum

# class ErrorTemplate(str, Enum):
#     status_code = 0,
#     detail = ''

class EmptyUserNameError(str, Enum):
    STATUS_CODE = 422
    DETAIL = "Username can't be empty."

class UserNotFound(str, Enum):
    STATUS_CODE = 404
    DETAIL = "User not found"

class UsernameIsTooLong(str, Enum):
    STATUS_CODE = 422
    DETAIL = "Username is too long"
