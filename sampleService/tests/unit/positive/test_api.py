""" Unit positive tests for Sample Service Rest API. """

from src.api import sample
from tests.helpers import generator
from tests.unit.helpers import api_helper, db_helper

def test_get_user(db_session_local):
    db = db_session_local

    username = generator.username()
    user_id = db_helper.db_add_user(db, username)

    result_username = sample.test_get(user_id, db)
    db_helper.db_remove_user(db, user_id)

    assert result_username == username

def test_post_user(db_session_local):
    db=db_session_local
    username = generator.username()
    user = api_helper.post_user(db, username)

    db_helper.db_remove_user(db, user.id)

    assert user.username == username

def test_post_user_max_length_username(db_session_local):
    db=db_session_local
    username = generator.custom_string(50)
    user = api_helper.post_user(db, username)

    db_helper.db_remove_user(db, user.id)

    assert user.username == username

def test_post_user_short_username(db_session_local):
    db=db_session_local
    username = generator.custom_string(1)
    user = api_helper.post_user(db, username)

    db_helper.db_remove_user(db, user.id)

    assert user.username == username
