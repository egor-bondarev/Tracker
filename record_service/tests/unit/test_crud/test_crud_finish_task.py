
import pytest
from sqlalchemy.exc import ArgumentError
from tests.helpers import db_helper, generators
from src.crud import task
from src.schemas import schemas

def test_correct(create_started_record, remove_test_data):

    db_session_local, started_record = create_started_record
    new_item = schemas.FinishedTask(id=started_record.id, timestamp=generators.timestamp_now())
    result = task.finish_task(db=db_session_local, item=new_item)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [started_record.id]

    assert started_record.id == result.id
    assert started_record.description == result.description
    assert started_record.start_timestamp == result.start_timestamp
    assert str(new_item.timestamp) == result.finish_timestamp

def test_id_task_that_already_finished(db_session_local, remove_test_data):

    finished_task = db_helper.add_full_record(db_session_local)
    new_item = schemas.FinishedTask(id=finished_task.id, timestamp=generators.timestamp_now())

    with pytest.raises(ArgumentError) as exc:
        task.finish_task(db=db_session_local, item=new_item)

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [finished_task.id]

    assert ArgumentError == exc.type
    assert str(finished_task.id) in str(exc.value)
