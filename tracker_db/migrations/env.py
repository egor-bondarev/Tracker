"""Alembic environment: migrates the database of the application role."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from tracker_db.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)


def database_url():
    # db_init passes the URL as an object attribute so passwords never pass through
    # configparser interpolation.
    url = config.attributes.get('sqlalchemy.url')
    if url is None:
        from tracker_db.config import Settings
        url = Settings().db_url
    return url


def run_migrations_offline():
    context.configure(url=database_url(), target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(database_url())
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=Base.metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
