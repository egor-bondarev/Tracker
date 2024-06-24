""" Helpers for working with API. """

from sampleService.src.api import sample
from sampleService.src.schemas import schemas
from sampleService.tests.unit.helpers.structures import CreateUserResult

def post_user(db, username) -> CreateUserResult:
    result = sample.test_post(schemas.UserCreate(username=username), db)
    return CreateUserResult(id=result.id, username=result.username)
