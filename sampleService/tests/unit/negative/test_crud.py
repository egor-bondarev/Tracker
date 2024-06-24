""" Unit negative tests for Sample Service database. """

import pytest

from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound

from sampleService.src.crud import user
from sampleService.src.schemas.schemas import UserCreate
from sampleService.tests.helpers import generator
from sampleService.tests.unit.helpers import db_helper

@pytest.mark.parametrize("username", [(''), (None)])
def test_create_user_invalid_username(db_session_local, username):

    with pytest.raises(ValidationError) as exc:
        user.create_user(db_session_local, UserCreate(username=username))

    assert ValidationError == exc.type

def test_get_user_null_id(db_session_local):
    with pytest.raises(NoResultFound) as exc:
        user.get_user(db_session_local, None)

    assert exc.type == NoResultFound

def test_get_not_existed_user(db_session_local):
    db = db_session_local
    user_id = user.create_user(db=db, item=UserCreate(username=generator.username())).id

    db_helper.db_remove_user(db, user_id)

    with pytest.raises(NoResultFound) as exc:
        user.get_user(db, user_id)

    assert exc.type == NoResultFound
