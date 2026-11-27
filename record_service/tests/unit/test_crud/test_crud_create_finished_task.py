from datetime import timedelta
from unittest.mock import MagicMock

import pytest
import allure

from tests.helpers import generators, db_helper
from src.crud import task
from src.schemas import schemas

@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Add new finished task")
def test_description_repeated_value(db_session_local, remove_test_data):

    existed_task = db_helper.add_full_record(db_session_local)
    new_item = schemas.NewTask(
        description=existed_task.description,
        timestamp=generators.timestamp_now())
    result = task.create_finished_task(db=db_session_local, item=new_item)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [result.id, existed_task.id]

    assert existed_task.description == result.description
    assert existed_task.id != result.id
    assert existed_task.finish_timestamp == result.start_timestamp
    assert new_item.timestamp == result.finish_timestamp

@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Add new finished task")
def test_correct(db_session_local,remove_test_data):

    new_item = schemas.NewTask(
        description=generators.custom_string(),
        timestamp=generators.timestamp_now())
    result = task.create_finished_task(db=db_session_local, item=new_item)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [result.id]

    assert new_item.description == result.description
    assert new_item.timestamp == result.finish_timestamp

@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Add new finished task")
@pytest.mark.parametrize(
    "description_value",
    [generators.custom_string(1), generators.custom_string(50)])
def test_symbols_in_description_field(db_session_local, remove_test_data, description_value):

    new_item = schemas.NewTask(description=description_value, timestamp=generators.timestamp_now())
    result = task.create_finished_task(db=db_session_local, item=new_item)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [result.id]

    assert description_value == result.description
    assert new_item.timestamp == result.finish_timestamp

@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Add finished task")
def test_first_task_starts_at_the_client_time():
    # No finished task yet: the start must not come from the server clock (UTC in a container).
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    timestamp = generators.timestamp_now() - timedelta(hours=5)
    new_item = schemas.NewTask(description=generators.custom_string(), timestamp=timestamp)

    result = task.create_finished_task(db=db, item=new_item)

    assert result.start_timestamp == timestamp
    assert result.finish_timestamp == timestamp
    assert result.duration == timedelta(0)
    db.add.assert_called_once_with(result)
