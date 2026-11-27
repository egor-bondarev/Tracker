''' Map CRUD domain errors to HTTP errors. '''

from contextlib import contextmanager

from fastapi import HTTPException, status
from src.crud.errors import ConflictError, InvalidCategoryError, InvalidTimeRangeError, NotFoundError


@contextmanager
def http_errors():
    ''' Translate domain errors raised inside the block. '''
    try:
        yield
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except (InvalidCategoryError, InvalidTimeRangeError) as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
