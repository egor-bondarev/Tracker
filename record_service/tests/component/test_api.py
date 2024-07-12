import pytest
import allure
from fastapi import status
from tests.helpers import api_helper, generators, db_helper, asserts
from src.resources.errors import TimestampFieldError

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("is_task_finished", [True, False])
def test_new_task_missing_timestamp_field(is_task_finished):

    response = api_helper.post_new_task_custom_body(
        {"description": f"{generators.custom_string()}"}, is_task_finished)

    asserts.api_field_required("timestamp", response)

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("is_task_finished", [True, False])
def test_new_task_missing_description_field(is_task_finished):

    response = api_helper.post_new_task_custom_body(
        {"timestamp": f"{generators.timestamp_now()}"}, is_task_finished)

    asserts.api_field_required("description", response)

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
def test_new_task_missing_is_task_finished_flag():

    response = api_helper.post_new_task_without_is_task_finished_flag(
        generators.custom_string(), generators.timestamp_now())

    asserts.api_field_required("is_task_finished", response)

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("is_task_finished", [True, False])
def test_new_task_empty_timestamp_field(is_task_finished):

    response = api_helper.post_new_task_custom_body(
        {"description": f"{generators.custom_string()}", "timestamp": ""}, is_task_finished)

    asserts.api_wrong_field_type("timestamp", response, "datetime")

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("is_task_finished", [True, False])
def test_new_task_empty_description_field(is_task_finished):

    response = api_helper.post_new_task_custom_body(
        {"description": "", "timestamp": f"{generators.timestamp_now()}"}, is_task_finished)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Description can't be empty" in response.json()["detail"][0]["msg"]
    assert "description" in response.json()["detail"][0]["loc"]

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
def test_new_task_empty_is_task_finished_field():

    response = api_helper.post_new_task_custom_body({
        "description": f"{generators.custom_string()}",
        "timestamp": f"{generators.timestamp_now()}"}, '')

    asserts.api_wrong_field_type("is_task_finished", response, "boolean")

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("data_type", ['string', 'integer'])
@pytest.mark.parametrize("is_task_finished", [True, False])
def test_new_task_api_wrong_field_type_timestamp_filed(data_type, is_task_finished):

    if data_type == 'string':
        timestamp = generators.custom_string()
    elif data_type == 'integer':
        timestamp = generators.number()
    response = api_helper.post_new_task_custom_body({
        "description": f"{generators.custom_string()}",
        "timestamp": f"{timestamp}"}, is_task_finished)

    if data_type == 'string':
        asserts.api_wrong_field_type("timestamp", response, "datetime")
    elif data_type == 'integer':
        asserts.api_wrong_field_type_custom_msg(
            "timestamp", response, TimestampFieldError.DETAIL.value)

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("is_task_finished", [True, False])
def test_new_task_api_wrong_field_type_description_field(is_task_finished):

    response = api_helper.post_new_task_custom_body({
        "description": generators.number(),
        "timestamp": f"{generators.timestamp_now()}"}, is_task_finished)

    asserts.api_wrong_field_type("description", response, "string")

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
def test_new_task_api_wrong_field_type_is_task_finished_field():

    response = api_helper.post_new_task_wrong_is_task_finished_flag(
        generators.custom_string(), generators.timestamp_now(), generators.number())

    asserts.api_wrong_field_type("is_task_finished", response, "boolean")

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("is_task_finished", [True, False])
@pytest.mark.parametrize("description", [generators.custom_string(1), generators.custom_string(50)])
def test_new_task_description_field(is_task_finished, description, remove_test_data, db_session_local):

    response = api_helper.post_new_task(description, generators.timestamp_now(), is_task_finished)
    task_id = response.json()['id']

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [task_id]

    assert response.status_code == status.HTTP_200_OK
    assert task_id is not None

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("is_task_finished", [True, False])
def test_new_task_more_than_max_symbols_in_description_field(is_task_finished):

    response = api_helper.post_new_task(
        generators.custom_string(51), generators.timestamp_now(), is_task_finished)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Description is too long" in response.json()["detail"][0]["msg"]
    assert "description" in response.json()["detail"][0]["loc"]

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST new task")
@pytest.mark.parametrize("is_task_finished", [True, False])
def test_new_task_description_repeated_value(is_task_finished, remove_test_data, db_session_local):

    description = generators.custom_string()

    response_first = api_helper.post_new_task(
        description, generators.timestamp_now(), is_task_finished)
    task_id_first = response_first.json()['id']

    response_second = api_helper.post_new_task(
        description, generators.timestamp_now(), is_task_finished)
    task_id_second = response_second.json()['id']

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [task_id_first, task_id_second]

    assert response_second.status_code == status.HTTP_200_OK
    assert task_id_second != task_id_first

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_post_finished_task_is_ok(create_started_record):

    _, task = create_started_record
    response = api_helper.post_finish_task(task.id, generators.timestamp_now())

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['duration'] is not None

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_finish_task_missing_id_field():

    response = api_helper.post_finish_task_custom_body(
        {"timestamp": f"{generators.timestamp_now()}"})

    asserts.api_field_required("id", response)

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_finish_task_missing_timestamp_field():

    response = api_helper.post_finish_task_custom_body({"id": f"{generators.number()}"})

    asserts.api_field_required("timestamp", response)

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_finish_task_api_wrong_field_type_id_field():

    response = api_helper.post_finish_task_custom_body(
        {"id": "", "timestamp": f"{generators.timestamp_now()}"})

    asserts.api_wrong_field_type("id", response, "integer")

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_finish_task_api_wrong_field_type_timestamp_field():

    response = api_helper.post_finish_task_custom_body(
        {"id": f"{generators.number()}", "timestamp": f"{generators.custom_string()}"})

    asserts.api_wrong_field_type("timestamp", response, "datetime")

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_finish_task_not_existed_id(create_started_record):

    db_session, task = create_started_record
    db_helper.remove_record(db_session, task.id)

    response = api_helper.post_finish_task(task.id, generators.timestamp_now())

    assert response.status_code == status.HTTP_404_NOT_FOUND

@allure.epic("Component tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_finish_task_already_finished_task_id_field(db_session_local, remove_test_data):

    existed_task = db_helper.add_full_record(db_session_local)
    response = api_helper.post_finish_task(existed_task.id, generators.timestamp_now())

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [existed_task.id]

    assert response.status_code == status.HTTP_409_CONFLICT
    assert str(existed_task.id) in response.json()["detail"]
