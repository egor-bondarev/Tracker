import uuid
from datetime import timedelta

import allure
import pytest
from pydantic import ValidationError
from src.crud import category, task
from src.crud.errors import InvalidCategoryError, InvalidTimeRangeError
from src.models import models
from src.schemas import schemas
from tests.helpers import generators


def synced(db, cleanup, client_id, **fields):
    values = {"description": "offline task", "start_timestamp": generators.timestamp_now()}
    values.update(fields)
    found, created = task.sync_task(db, client_id, schemas.TaskSync(**values))
    cleanup["tasks"].append(found.id)
    return found, created


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Sync task")
def test_create_then_finish_same_task(db_session_local, cleanup):
    client_id = uuid.uuid4()
    start = generators.timestamp_now() - timedelta(hours=2)

    started, created = synced(db_session_local, cleanup, client_id, start_timestamp=start)
    assert created and started.client_id == client_id and started.finish_timestamp is None

    finished, created = synced(db_session_local, cleanup, client_id, start_timestamp=start,
                               finish_timestamp=start + timedelta(minutes=45))
    assert not created
    assert finished.id == started.id
    assert finished.duration == timedelta(minutes=45)


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Sync task")
def test_resending_does_not_duplicate(db_session_local, cleanup):
    client_id = uuid.uuid4()
    start = generators.timestamp_now()
    for _ in range(3):
        synced(db_session_local, cleanup, client_id, start_timestamp=start,
               finish_timestamp=start + timedelta(minutes=1))

    count = db_session_local.query(models.Task).filter(models.Task.client_id == client_id).count()
    assert count == 1


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Sync task")
def test_archived_category_is_kept(db_session_local, cleanup):
    cat = category.create_category(
        db_session_local, schemas.CategoryCreate(name=f"cat-{uuid.uuid4().hex[:12]}"))
    cleanup["categories"].append(cat.id)
    category.update_category(db_session_local, cat.id, schemas.CategoryUpdate(archived=True))

    found, _ = synced(db_session_local, cleanup, uuid.uuid4(), category_id=cat.id)

    assert found.category_id == cat.id


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Sync task")
def test_unknown_category_is_rejected(db_session_local):
    with pytest.raises(InvalidCategoryError):
        task.sync_task(db_session_local, uuid.uuid4(), schemas.TaskSync(
            description="x", start_timestamp=generators.timestamp_now(), category_id=0))


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Sync task")
def test_reversed_range_is_rejected(db_session_local):
    start = generators.timestamp_now()
    with pytest.raises(InvalidTimeRangeError):
        task.sync_task(db_session_local, uuid.uuid4(), schemas.TaskSync(
            description="x", start_timestamp=start, finish_timestamp=start - timedelta(seconds=1)))


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Sync task")
@pytest.mark.parametrize("fields", [
    {"start_timestamp": "2026-11-27 10:00:00"},
    {"description": "", "start_timestamp": "2026-11-27 10:00:00"},
    {"description": "x", "start_timestamp": "1764230400"},
])
def test_invalid_payload(fields):
    with pytest.raises(ValidationError):
        schemas.TaskSync(**fields)
