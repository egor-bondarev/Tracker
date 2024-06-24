""" Helpers for working with DB. """

from fastapi import Depends
from pydantic import PostgresDsn, ValidationError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlmodel import select
from typing_extensions import Annotated

from src.models import models
from tests import config

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
            host=settings.SAMPLE_SERVICE_HOST,
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

def db_remove_user(user_id: int):
    session = TestingSessionLocal()

    user = session.execute(select(models.User).where(models.User.id == user_id)).first()[0]
    session.delete(user)

    session.commit()
    session.close()
