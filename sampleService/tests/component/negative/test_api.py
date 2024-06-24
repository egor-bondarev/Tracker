""" Component negative tests for Sample Service Rest API. """

import pytest

from fastapi import status

from sampleService.src.resources.errors import UserNotFound, EmptyUserNameError, UsernameIsTooLong
from sampleService.tests.component.helpers import api_helper, db_helper
from sampleService.tests.helpers import generator, error_msg


def test_post_user_empty_name():
    response = api_helper.post_user('')

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert EmptyUserNameError.DETAIL.value in \
        str(response.json()["detail"][0]["msg"])

def test_post_user_too_long_length():
    response = api_helper.post_user(generator.custom_string(51))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert UsernameIsTooLong.DETAIL.value in response.json()["detail"][0]["msg"]

def test_post_user_none_name():
    response = api_helper.post_user_none_name()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert error_msg.ERROR_VALID_STRING in str(response.json()["detail"])

def test_post_user_empty_body():
    response = api_helper.post_user_custom_body({})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == error_msg.ERROR_FIELD_REQUIRED

def test_post_user_wrong_key_in_body():
    key = generator.custom_string()
    value = generator.username()
    response = api_helper.post_user_custom_body({key: value})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == error_msg.ERROR_FIELD_REQUIRED
    assert response.json()["detail"][0]["input"][key] == value

def test_post_user_wrong_username_type():
    response = api_helper.post_user_custom_body({"username": generator.number()})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == error_msg.ERROR_VALID_STRING

def test_post_user_invalid_json():
    response = api_helper.post_user_invalid_json(f"{{\"username\": {generator.username()}\"}}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == error_msg.ERROR_INVALID_JSON

@pytest.mark.parametrize(
    "user_id", [(generator.custom_string()), (' '), (generator.string_and_num()), (None)])
def test_get_user(user_id):
    response = api_helper.get_user(user_id)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == error_msg.ERROR_INVALID_TYPE_INTEGER

def test_get_user_no_id():
    response = api_helper.get_user_empty_id()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == error_msg.ERROR_NOT_FOUND

def test_get_user_not_existed_id():
    create_user_response = api_helper.post_user(generator.username())
    user_id = create_user_response.json()["id"]

    db_helper.db_remove_user(user_id)

    response = api_helper.get_user(user_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == UserNotFound.DETAIL.value
