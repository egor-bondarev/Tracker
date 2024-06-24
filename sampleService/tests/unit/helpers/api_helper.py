""" Helpers for working with API. """

from src.api import sample
from src.schemas import schemas
from tests.unit.helpers.structures import CreateUserResult

def post_user(db, username) -> CreateUserResult:
    result = sample.test_post(schemas.UserCreate(username=username), db)
    return CreateUserResult(id=result.id, username=result.username)
