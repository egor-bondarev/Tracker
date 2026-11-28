""" Helper for working with DB. """

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import select
import uuid
from tests.helpers import db_helper, users
from tracker_db.auth import generate_token, hash_token
from tests import config

from typing_extensions import Annotated
from fastapi import Depends
from pydantic import PostgresDsn, ValidationError
from src.models import models

def get_settings():
    return config.Settings()

def get_db_url(settings: Annotated[config.Settings, Depends(get_settings)]) -> PostgresDsn:
    ''' Generate db url. '''
    try:
        conn = PostgresDsn.build(
            scheme='postgresql',
            hosts=None,
            username=settings.database_user,
            password=settings.DATABASE_PASSWORD,
            host=settings.RECORD_SERVICE_HOST,
            port=settings.DATABASE_EXTERNAL_PORT,
            path=f"{settings.DATABASE_NAME}"
        ).unicode_string()
    except ValidationError as exc:
        print(repr(exc.errors()[0]['type']))

    return conn

engine = create_engine(get_db_url(get_settings()))

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind = engine)

def create_user(name):
    """A user with a fresh token; returns (id, token)."""
    token = generate_token()
    session = TestingSessionLocal()
    try:
        user = models.User(name=name, token_hash=hash_token(token))
        session.add(user)
        session.commit()
        return user.id, token
    finally:
        session.close()


def delete_user(user_id):
    session = TestingSessionLocal()
    try:
        for model in (models.Task, models.Category):
            session.query(model).filter(model.user_id == user_id).delete(synchronize_session=False)
        session.query(models.User).filter(models.User.id == user_id).delete()
        session.commit()
    finally:
        session.close()


@pytest.fixture(scope="session", autouse=True)
def test_user():
    """Every test acts as this user; it and all its data are removed afterwards."""
    users.TEST_USER_ID, users.TEST_TOKEN = create_user(f"test-{uuid.uuid4().hex[:12]}")
    yield
    delete_user(users.TEST_USER_ID)


@pytest.fixture(name="other_user")
def other_user_fixture():
    """A second user with its own token, for isolation tests."""
    user_id, token = create_user(f"other-{uuid.uuid4().hex[:12]}")
    yield user_id, token
    delete_user(user_id)


@pytest.fixture(name="remove_test_data", scope="function")
def remove_test_data_fixture():
    return {}

def _remove_test_records(session: Session, remove_test_data):
    if remove_test_data.get("action") == 'teardown':
        for record_id in remove_test_data.get("id"):
            try:
                task = session.execute(
                    select(models.Task).where(models.Task.id == record_id)).first()[0]
                session.delete(task)
                session.commit()
            except TypeError:
                print('Task was already deleted.')

@pytest.fixture(scope="function")
def db_session_local(remove_test_data):

    session = TestingSessionLocal()

    yield session

    _remove_test_records(session, remove_test_data)

    session.close()

@pytest.fixture(scope="function")
def create_started_record(remove_test_data):

    session = TestingSessionLocal()
    started_task = db_helper.add_started_record(session)

    yield session, started_task

    remove_test_data["action"] = 'teardown'
    remove_test_data["id"] = [started_task.id]

    _remove_test_records(session, remove_test_data)

    session.close()


@pytest.fixture(name="cleanup")
def cleanup_fixture():
    """Collects task and category ids created by a test and deletes them afterwards."""

    created = {"tasks": [], "categories": []}
    yield created

    session = TestingSessionLocal()
    try:
        for task_id in created["tasks"]:
            task = session.get(models.Task, task_id)
            if task is not None:
                session.delete(task)
        session.flush()
        for category_id in created["categories"]:
            category = session.get(models.Category, category_id)
            if category is not None:
                session.delete(category)
        session.commit()
    finally:
        session.close()
