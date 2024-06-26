""" Component positive tests for Sample Service Rest API. """

import pytest
import allure

from fastapi import status

from tests.component.helpers import api_helper, db_helper
from tests.helpers import generator

@allure.epic("API")
@allure.feature("Component tests")
@allure.story("Positive")
@pytest.mark.parametrize(
    "username", [(generator.custom_string(1)), (generator.number_one_symbol())])
def test_post_user_one_symbol_name(username):
    response = api_helper.post_user(username)

    db_helper.db_remove_user(response.json()["id"])

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == str(username)

@allure.epic("API")
@allure.feature("Component tests")
@allure.story("Positive")
def test_post_user_max_length():
    username = generator.custom_string(50)
    response = api_helper.post_user(username)

    assert response.status_code == status.HTTP_200_OK

    db_helper.db_remove_user(response.json()["id"])

    assert response.json()["username"] == username

@allure.epic("API")
@allure.feature("Component tests")
@allure.story("Positive")
def test_post_user_existed_name():
    username = generator.username()
    response_first_user = api_helper.post_user(username)

    assert response_first_user.status_code == status.HTTP_200_OK

    response_second_user = api_helper.post_user(username)
    db_helper.db_remove_user(response_first_user.json()["id"])
    db_helper.db_remove_user(response_second_user.json()["id"])

    assert response_second_user.status_code == status.HTTP_200_OK
    assert response_second_user.json()["username"] == username

@allure.epic("API")
@allure.feature("Component tests")
@allure.story("Positive")
@pytest.mark.parametrize(
    "username", [(generator.username()), (generator.number())])
def test_get_user(username):
    response_creating_user = api_helper.post_user(username)

    assert response_creating_user.status_code == status.HTTP_200_OK
    user_id = response_creating_user.json()["id"]

    response_get_user = api_helper.get_user(user_id)
    db_helper.db_remove_user(user_id)

    assert response_get_user.status_code == status.HTTP_200_OK
    assert response_creating_user.json()["username"] == response_get_user.json()
