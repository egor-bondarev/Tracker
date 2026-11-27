''' Domain errors raised by CRUD functions and mapped to HTTP responses by the API. '''


class NotFoundError(LookupError):
    ''' The requested record does not exist. '''


class ConflictError(ValueError):
    ''' The change conflicts with existing data. '''


class InvalidCategoryError(ValueError):
    ''' The category does not exist or is archived. '''


class InvalidTimeRangeError(ValueError):
    ''' The finish time is before the start time. '''
