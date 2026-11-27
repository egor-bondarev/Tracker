import uuid
from datetime import datetime, timedelta

import allure
import pytest
from pydantic import ValidationError
from src.crud import category, task
from src.crud.errors import InvalidCategoryError, InvalidTimeRangeError, NotFoundError
from src.schemas import schemas
from tests.helpers import generators

FAR_FUTURE = datetime(2999, 1, 1, 9, 0, 0)


def new_category(db, cleanup, archived=False):
    created = category.create_category(
        db, schemas.CategoryCreate(name=f"cat-{uuid.uuid4().hex[:12]}"))
    if archived:
        category.update_category(db, created.id, schemas.CategoryUpdate(archived=True))
    cleanup["categories"].append(created.id)
    return created


def started_task(db, cleanup, timestamp=None, category_id=None):
    created = task.create_task(db, schemas.NewTask(
        description=str(uuid.uuid4())[:50], timestamp=timestamp or generators.timestamp_now(),
        category_id=category_id))
    cleanup["tasks"].append(created.id)
    return created


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_past_timestamp_is_accepted(db_session_local, cleanup):
    yesterday = generators.timestamp_now() - timedelta(days=1)

    created = started_task(db_session_local, cleanup, timestamp=yesterday)

    assert created.start_timestamp == yesterday


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_create_with_category(db_session_local, cleanup):
    cat = new_category(db_session_local, cleanup)

    created = started_task(db_session_local, cleanup, category_id=cat.id)

    assert created.category_id == cat.id


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
@pytest.mark.parametrize("archived", [True, False])
def test_create_with_unavailable_category(db_session_local, cleanup, archived):
    category_id = new_category(db_session_local, cleanup, archived=True).id if archived else 0

    with pytest.raises(InvalidCategoryError):
        task.create_task(db_session_local, schemas.NewTask(
            description='x', timestamp=generators.timestamp_now(), category_id=category_id))


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_active_task_is_latest_unfinished(db_session_local, cleanup):
    started = started_task(db_session_local, cleanup, timestamp=FAR_FUTURE)

    assert task.get_active_task(db_session_local).id == started.id

    task.finish_task(db_session_local, schemas.FinishedTask(
        id=started.id, timestamp=FAR_FUTURE + timedelta(minutes=1)))
    active = task.get_active_task(db_session_local)
    assert active is None or active.id != started.id


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_finish_before_start_is_rejected(db_session_local, cleanup):
    started = started_task(db_session_local, cleanup)

    with pytest.raises(InvalidTimeRangeError):
        task.finish_task(db_session_local, schemas.FinishedTask(
            id=started.id, timestamp=started.start_timestamp - timedelta(seconds=1)))


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_update_fields(db_session_local, cleanup):
    cat = new_category(db_session_local, cleanup)
    started = started_task(db_session_local, cleanup)
    start = started.start_timestamp - timedelta(hours=1)
    finish = start + timedelta(minutes=30)

    updated = task.update_task(db_session_local, started.id, schemas.TaskUpdate(
        description='corrected', category_id=cat.id,
        start_timestamp=start, finish_timestamp=finish))

    assert (updated.description, updated.category_id) == ('corrected', cat.id)
    assert (updated.start_timestamp, updated.finish_timestamp) == (start, finish)
    assert updated.duration == timedelta(minutes=30)


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_update_only_sent_fields(db_session_local, cleanup):
    cat = new_category(db_session_local, cleanup)
    started = started_task(db_session_local, cleanup, category_id=cat.id)

    updated = task.update_task(
        db_session_local, started.id, schemas.TaskUpdate(description='renamed'))
    assert updated.category_id == cat.id

    cleared = task.update_task(
        db_session_local, started.id, schemas.TaskUpdate(category_id=None))
    assert cleared.category_id is None
    assert cleared.description == 'renamed'


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_update_keeps_archived_category(db_session_local, cleanup):
    cat = new_category(db_session_local, cleanup)
    started = started_task(db_session_local, cleanup, category_id=cat.id)
    category.update_category(db_session_local, cat.id, schemas.CategoryUpdate(archived=True))

    updated = task.update_task(db_session_local, started.id, schemas.TaskUpdate(
        category_id=cat.id, description='still allowed'))

    assert updated.category_id == cat.id


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_update_rejects_reversed_range(db_session_local, cleanup):
    started = started_task(db_session_local, cleanup)

    with pytest.raises(InvalidTimeRangeError):
        task.update_task(db_session_local, started.id, schemas.TaskUpdate(
            finish_timestamp=started.start_timestamp - timedelta(minutes=1)))


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
def test_delete(db_session_local, cleanup):
    started = started_task(db_session_local, cleanup)

    task.delete_task(db_session_local, started.id)

    with pytest.raises(NotFoundError):
        task.get_task(db_session_local, started.id)
    with pytest.raises(NotFoundError):
        task.delete_task(db_session_local, started.id)


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Tasks")
@pytest.mark.parametrize("field", ["description", "start_timestamp"])
def test_required_fields_cannot_be_cleared(field):
    with pytest.raises(ValidationError):
        schemas.TaskUpdate(**{field: None})
