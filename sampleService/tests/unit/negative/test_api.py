""" Unit negative tests for Sample Service Rest API. """

import pytest
import allure

from fastapi import HTTPException, status
from pydantic import ValidationError

from src.api import sample
from src.resources.errors import UsernameIsTooLong
from src.schemas import schemas
from tests.helpers import generator, error_msg
from tests.unit.helpers import db_helper

@allure.epic("API")
@allure.feature("Unit tests")
@allure.story("Negative")
def test_get_not_existed_user(db_session_local):
    db = db_session_local
    username = generator.username()
    user_id = db_helper.db_add_user(db, username)

    db_helper.db_remove_user(db, user_id)

    with pytest.raises(HTTPException) as exc:
        sample.test_get(user_id, db)

    assert exc.type == HTTPException
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == error_msg.ERROR_NOT_FOUND

@allure.epic("API")
@allure.feature("Unit tests")
@allure.story("Negative")
def test_get_user_null_id(db_session_local):
    with pytest.raises(HTTPException) as exc:
        sample.test_get(None, db_session_local)

    assert exc.type == HTTPException
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == error_msg.ERROR_NOT_FOUND

@allure.epic("API")
@allure.feature("Unit tests")
@allure.story("Negative")
def test_post_user_null_username(db_session_local):
    with pytest.raises(ValidationError) as exc:
        new_user = schemas.UserCreate(username=None)
        sample.test_post(new_user, db_session_local)

    assert ValidationError == exc.type

@allure.epic("API")
@allure.feature("Unit tests")
@allure.story("Negative")
def test_post_user_empty_username(db_session_local):
    with pytest.raises(ValidationError) as exc:
        new_user = schemas.UserCreate(username='')
        sample.test_post(new_user, db_session_local)

    assert exc.type == ValidationError

@allure.epic("API")
@allure.feature("Unit tests")
@allure.story("Negative")
def test_post_user_too_long_username(db_session_local):
    with pytest.raises(ValidationError) as exc:
        new_user = schemas.UserCreate(username=generator.custom_string(51))
        sample.test_post(new_user, db_session_local)

    assert exc.type == ValidationError
    assert UsernameIsTooLong.DETAIL.value in exc.value.errors()[0]["msg"]
