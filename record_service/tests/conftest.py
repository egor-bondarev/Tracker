""" Helper for working with DB. """

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import select
from tests.helpers import db_helper
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
