""" Error messages. """

from enum import Enum

class EmptyDescriptionError(str, Enum):
    STATUS_CODE = 422
    DETAIL = "Description can't be empty."

class EmptyTimestampError(str, Enum):
    STATUS_CODE = 422
    DETAIL = "Timestamp can't be empty."

class DescriptionIsTooLong(str, Enum):
    STATUS_CODE = 422
    DETAIL = "Description is too long"

class TimestampFieldError(str, Enum):
    STATUS_CODE = 422
    DETAIL = "Timestamp field type is wrong."
