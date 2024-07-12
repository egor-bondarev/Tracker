
import pytest
from pydantic import ValidationError
from tests.helpers import generators, db_helper, asserts
from src.crud import task
from src.resources.errors import EmptyDescriptionError, DescriptionIsTooLong, TimestampFieldError
from src.schemas import schemas

def test_empty_description():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(description='', timestamp=generators.timestamp_now())

    asserts.exception_validate_field(exc, 'description', EmptyDescriptionError.DETAIL.value)

def test_missing_description():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(timestamp=generators.timestamp_now())

    asserts.exception_field_required(exc, 'description')

def test_missing_timestamp():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(description=generators.custom_string())

    asserts.exception_field_required(exc, 'timestamp')

def test_wrong_type_description():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(description=generators.number(), timestamp=generators.timestamp_now())

    asserts.exception_wrong_field_type(exc, 'description', 'string')

@pytest.mark.parametrize("data_type", ['string', 'integer'])
def test_wrong_type_timestamp(data_type):

    if data_type == 'string':
        timestamp = generators.custom_string()
    elif data_type == 'integer':
        timestamp = generators.number()

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(
            description=generators.custom_string(),
            timestamp=timestamp)

    if data_type == 'string':
        asserts.exception_wrong_field_type(exc, 'timestamp', 'datetime')
    elif data_type == 'integer':
        asserts.exception_wrong_field_type_custom_msg(
            exc, 'timestamp', TimestampFieldError.DETAIL.value)

def test_description_repeated_value(db_session_local, remove_test_data):

    existed_task = db_helper.add_full_record(db_session_local)
    new_item = schemas.NewTask(
        description=existed_task.description,
        timestamp=generators.timestamp_now())
    new_task = task.create_task(db=db_session_local, item=new_item)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [new_task.id, existed_task.id]

    assert existed_task.description == new_task.description
    assert existed_task.id != new_task.id

def test_correct(db_session_local, remove_test_data):

    new_item = schemas.NewTask(
        description=generators.custom_string(),
        timestamp=generators.timestamp_now())
    result = task.create_task(db=db_session_local, item=new_item)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [result.id]

    assert new_item.description == result.description
    assert str(new_item.timestamp) == result.start_timestamp
    assert result.finish_timestamp is None

@pytest.mark.parametrize(
    "description_value",
    [generators.custom_string(1), generators.custom_string(50)])
def test_symbols_in_description_field(db_session_local, remove_test_data, description_value):

    new_item = schemas.NewTask(description=description_value, timestamp=generators.timestamp_now())
    result = task.create_task(db=db_session_local, item=new_item)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [result.id]

    assert description_value == result.description
    assert str(new_item.timestamp) == result.start_timestamp
    assert result.finish_timestamp is None

def test_more_than_max_symbols_in_description_field():

    with pytest.raises(ValidationError) as exc:
        schemas.NewTask(
            description=generators.custom_string(51),
            timestamp=generators.timestamp_now())

    asserts.exception_validate_field(exc, 'description', DescriptionIsTooLong.DETAIL.value)
