"""Create the Tracker role and database, then apply migrations; safe to rerun."""

import time
from enum import Enum

import psycopg2
from psycopg2 import sql
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConnectionRole(str, Enum):
    admin = 'ADMIN'
    user = 'USER'


class Settings(BaseSettings):
    database_admin: str
    database_admin_password: str
    database_default_name: str
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    model_config = SettingsConfigDict(
        extra='ignore', env_file='.env', hide_input_in_errors=True
    )

    def get_connection(self, role: ConnectionRole):
        if role == ConnectionRole.admin:
            database, user, password = (
                self.database_default_name,
                self.database_admin,
                self.database_admin_password,
            )
        elif role == ConnectionRole.user:
            database, user, password = (
                self.database_name, self.database_user, self.database_password
            )
        else:
            raise ValueError('Unknown database role')

        for attempt in range(1, 11):
            try:
                return psycopg2.connect(
                    dbname=database, user=user, password=password,
                    host=self.database_host, port=self.database_port,
                    connect_timeout=5,
                )
            except psycopg2.OperationalError:
                if attempt == 10:
                    raise RuntimeError(
                        'Database connection failed after 10 attempts; check host, port and credentials'
                    ) from None
                print(f'Database unavailable; retry {attempt}/10', flush=True)
                time.sleep(2)


def create_database(settings):
    connection = settings.get_connection(ConnectionRole.admin)
    try:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM pg_roles WHERE rolname = %s', (settings.database_user,))
            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL('CREATE USER {} WITH PASSWORD %s').format(
                        sql.Identifier(settings.database_user)
                    ),
                    (settings.database_password,),
                )
            cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (settings.database_name,))
            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL('CREATE DATABASE {} OWNER {}').format(
                        sql.Identifier(settings.database_name),
                        sql.Identifier(settings.database_user),
                    )
                )
    finally:
        connection.close()


def migration_url(settings):
    from sqlalchemy.engine import URL

    return URL.create(
        'postgresql+psycopg2', username=settings.database_user,
        password=settings.database_password, host=settings.database_host,
        port=settings.database_port, database=settings.database_name,
    )


def run_migrations(settings):
    """Bring the schema to the latest Alembic revision as the application role."""
    from pathlib import Path

    from alembic import command
    from alembic.config import Config
    import tracker_db

    settings.get_connection(ConnectionRole.user).close()  # bounded wait, clear error
    config = Config()
    config.set_main_option('script_location', str(Path(tracker_db.__file__).parent / 'migrations'))
    config.attributes['sqlalchemy.url'] = migration_url(settings)
    command.upgrade(config, 'head')


if __name__ == '__main__':
    settings = Settings()
    create_database(settings)
    run_migrations(settings)
    print('Tracker database initialized', flush=True)
