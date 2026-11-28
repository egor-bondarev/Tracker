from tests.helpers import users
import uuid

import allure
import pytest
from pydantic import ValidationError
from src.crud import category
from src.crud.errors import ConflictError, NotFoundError
from src.resources.errors import CategoryNameIsTooLong, EmptyCategoryNameError
from src.schemas import schemas


def unique_name():
    return f"cat-{uuid.uuid4().hex[:12]}"


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Categories")
def test_create_and_list(db_session_local, cleanup):
    name = unique_name()
    created = category.create_category(db_session_local, schemas.CategoryCreate(name=f"  {name} "), user_id=users.TEST_USER_ID)
    cleanup["categories"].append(created.id)

    assert created.name == name
    assert created.archived is False
    assert created.id in [c.id for c in category.list_categories(db_session_local, user_id=users.TEST_USER_ID)]


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Categories")
def test_duplicate_name_conflicts(db_session_local, cleanup):
    name = unique_name()
    cleanup["categories"].append(
        category.create_category(db_session_local, schemas.CategoryCreate(name=name), user_id=users.TEST_USER_ID).id)

    with pytest.raises(ConflictError):
        category.create_category(db_session_local, schemas.CategoryCreate(name=name), user_id=users.TEST_USER_ID)


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Categories")
def test_archive_hides_from_default_list(db_session_local, cleanup):
    created = category.create_category(
        db_session_local, schemas.CategoryCreate(name=unique_name()), user_id=users.TEST_USER_ID)
    cleanup["categories"].append(created.id)

    category.update_category(db_session_local, created.id, schemas.CategoryUpdate(archived=True), user_id=users.TEST_USER_ID)

    assert created.id not in [c.id for c in category.list_categories(db_session_local, user_id=users.TEST_USER_ID)]
    assert created.id in [c.id for c in category.list_categories(db_session_local, True, user_id=users.TEST_USER_ID)]


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Categories")
def test_rename(db_session_local, cleanup):
    created = category.create_category(
        db_session_local, schemas.CategoryCreate(name=unique_name()), user_id=users.TEST_USER_ID)
    cleanup["categories"].append(created.id)
    new_name = unique_name()

    renamed = category.update_category(
        db_session_local, created.id, schemas.CategoryUpdate(name=new_name), user_id=users.TEST_USER_ID)

    assert renamed.name == new_name
    assert renamed.archived is False


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Categories")
def test_update_missing_category(db_session_local):
    with pytest.raises(NotFoundError):
        category.update_category(db_session_local, 0, schemas.CategoryUpdate(archived=True), user_id=users.TEST_USER_ID)


@allure.epic("Unit tests")
@allure.feature("CRUD")
@allure.story("Categories")
@pytest.mark.parametrize("name, message", [
    ("   ", EmptyCategoryNameError.DETAIL.value),
    ("x" * 51, CategoryNameIsTooLong.DETAIL.value),
])
def test_invalid_name(name, message):
    with pytest.raises(ValidationError) as exc:
        schemas.CategoryCreate(name=name)
    assert message in exc.value.errors()[0]["msg"]
