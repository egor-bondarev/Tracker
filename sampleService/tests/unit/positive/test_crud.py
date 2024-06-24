""" Unit positive tests for Sample Service database. """

from src.crud import user
from tests.helpers import generator
from src.schemas.schemas import UserCreate
from tests.unit.helpers import db_helper

def test_create_user(db_session_local):
    db = db_session_local

    new_user = UserCreate(username=generator.username())
    result = user.create_user(db, new_user)
    result_username = result.username

    db_helper.db_remove_user(db, result.id)

    assert new_user.username == result_username

def test_create_user_repeated_username(db_session_local):
    db = db_session_local
    new_user = UserCreate(username=generator.username())

    result_1 = user.create_user(db, new_user)
    result_2 = user.create_user(db, new_user)

    username_1 = result_1.username
    username_2 = result_2.username

    db_helper.db_remove_user(db, result_1.id)
    db_helper.db_remove_user(db, result_2.id)

    assert username_1 == username_2

def test_get_user(db_session_local):
    db = db_session_local

    new_user = UserCreate(username=generator.username())
    new_user_id = user.create_user(db, new_user).id

    result = user.get_user(db, new_user_id)
    username = result

    db_helper.db_remove_user(db, new_user_id)
    assert new_user.username == username
