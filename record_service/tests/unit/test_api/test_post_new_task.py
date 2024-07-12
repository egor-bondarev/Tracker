
import uuid
import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from tests.helpers import db_helper, generators, asserts
from src.api import task
from src.schemas import schemas
from src.resources.errors import EmptyDescriptionError, DescriptionIsTooLong, TimestampFieldError

def test_missing_timestamp_filed():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(description=str(uuid.uuid4()))

    asserts.exception_field_required(exc, 'timestamp')

def test_missing_description_field():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(timestamp=generators.timestamp_now())

    asserts.exception_field_required(exc, 'description')

def test_missing_is_task_finished_field(db_session_local):

    with pytest.raises(HTTPException) as exc:
        new_task = schemas.NewTask(
            timestamp=generators.timestamp_now(), description=str(uuid.uuid4()))
        task.post_new_task(new_task, db_session_local)

    asserts.exception_missing_field(exc, 'is_task_finished')

def test_empty_description_field():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(
            timestamp=generators.timestamp_now(),
            description='')

    asserts.exception_validate_field(exc, 'description', EmptyDescriptionError.DETAIL.value)

@pytest.mark.parametrize("data_type", ['string', 'integer'])
def test_wrong_type_timestamp_filed(data_type):

    if data_type == 'string':
        timestamp = generators.custom_string()
    elif data_type == 'integer':
        timestamp = generators.number()

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(
            timestamp=timestamp,
            description=str(uuid.uuid4()))

    if data_type == 'string':
        asserts.exception_wrong_field_type(exc, 'timestamp', 'datetime')
    elif data_type == 'integer':
        asserts.exception_wrong_field_type_custom_msg(
            exc, 'timestamp', TimestampFieldError.DETAIL.value)

def test_wrong_type_description_field():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(
            timestamp=generators.timestamp_now(),
            description=generators.number())

    asserts.exception_wrong_field_type(exc, 'description', 'string')

def test_wrong_type_is_task_finished_field(db_session_local):

    with pytest.raises(HTTPException) as exc:
        new_task = schemas.NewTask(
            timestamp=generators.timestamp_now(), description=str(uuid.uuid4()))
        task.post_new_task(new_task, generators.number(), db_session_local)

    asserts.exception_missing_field(exc, 'is_task_finished')

@pytest.mark.parametrize("is_task_finished", [True, False])
@pytest.mark.parametrize(
    "description_value",
    [generators.custom_string(1), generators.custom_string(50)])
def test_description_field(db_session_local, is_task_finished, description_value, remove_test_data):

    new_task = schemas.NewTask(
        timestamp=generators.timestamp_now(),
        description=description_value)
    result = task.post_new_task(new_task, is_task_finished, db_session_local)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [result.id]

    assert new_task.description == result.description

    if is_task_finished:
        assert str(new_task.timestamp) == result.finish_timestamp
        assert result.start_timestamp is not None
    else:
        assert str(new_task.timestamp) == result.start_timestamp
        assert result.finish_timestamp is None

def test_more_than_max_symbols_in_description_field():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(
            timestamp=generators.timestamp_now(),
            description=generators.custom_string(51))

    asserts.exception_validate_field(exc, 'description', DescriptionIsTooLong.DETAIL.value)

def test_all_is_correct(db_session_local, remove_test_data):

    description = str(uuid.uuid4())
    start_timestamp = generators.timestamp_now()
    new_task = schemas.NewTask(
        description=description,
        timestamp=start_timestamp)
    result = task.post_new_task(new_task, False, db_session_local)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [result.id]

    assert description == result.description
    assert str(start_timestamp) == result.start_timestamp
    assert result.finish_timestamp is None

def test_description_repeated_value(db_session_local, remove_test_data):

    existed_record = db_helper.add_full_record(db_session_local)
    start_timestamp = generators.timestamp_now()

    new_task = schemas.NewTask(
        description=existed_record.description,
        timestamp=start_timestamp)
    result = task.post_new_task(new_task, False, db_session_local)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [result.id, existed_record.id]

    assert existed_record.description == result.description
    assert str(start_timestamp) == result.start_timestamp
    assert result.finish_timestamp is None
