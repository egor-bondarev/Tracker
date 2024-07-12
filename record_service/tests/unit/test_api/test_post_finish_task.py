
import pytest
import allure

from fastapi import HTTPException, status
from pydantic import ValidationError
from tests.helpers import db_helper, generators, asserts
from src.api import task
from src.schemas import schemas

@allure.epic("Unit tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_all_is_correct(create_started_record):

    db_session, started_task = create_started_record
    finish_task = schemas.FinishedTask(id=started_task.id, timestamp=generators.timestamp_now())
    result = task.post_finish_task(finish_task, db_session)

    assert started_task == result, 'Records are not equal.'

@allure.epic("Unit tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_missing_id_field():

    with pytest.raises(ValidationError) as exc:
        schemas.FinishedTask(timestamp=generators.timestamp_now())

    asserts.exception_field_required(exc, 'id')

@allure.epic("Unit tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_missing_timestamp_field(create_started_record):

    _, started_task = create_started_record

    with pytest.raises(ValidationError) as exc:
        schemas.FinishedTask(id=started_task.id)

    asserts.exception_field_required(exc, 'timestamp')

@allure.epic("Unit tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_wrong_type_timestamp_field(create_started_record):

    _, started_task = create_started_record

    with pytest.raises(ValidationError) as exc:
        schemas.FinishedTask(id=started_task.id, timestamp=generators.custom_string())

    asserts.exception_wrong_field_type(exc, 'timestamp', 'datetime')

@allure.epic("Unit tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_wrong_type_id_field():

    with pytest.raises(ValidationError) as exc:
        schemas.FinishedTask(id=None, timestamp=generators.timestamp_now())

    asserts.exception_wrong_field_type(exc, 'id', 'int')

@allure.epic("Unit tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_not_existed_id_field(db_session_local):

    new_task = db_helper.add_full_record(db_session_local)
    db_helper.remove_record(db_session_local, new_task.id)
    finish_task = schemas.FinishedTask(id=new_task.id, timestamp=generators.timestamp_now())

    with pytest.raises(HTTPException) as exc:
        task.post_finish_task(finish_task, db_session_local)

    assert exc.type == HTTPException
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert 'Not Found' in exc.value.detail

@allure.epic("Unit tests")
@allure.feature("API")
@allure.story("POST finish task")
def test_already_finished_task_id_field(db_session_local):

    new_task = db_helper.add_full_record(db_session_local)
    finish_task = schemas.FinishedTask(id=new_task.id, timestamp=generators.timestamp_now())

    with pytest.raises(HTTPException) as exc:
        task.post_finish_task(finish_task, db_session_local)

    db_helper.remove_record(db_session_local, new_task.id)

    assert exc.type == HTTPException
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert str(new_task.id) in exc.value.detail
