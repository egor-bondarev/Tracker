""" Creating database. """

import time
from dataclasses import dataclass
import psycopg2

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

@dataclass
class ConnectionRole(str):
    """ Roles for db connections. """
    admin: str = 'ADMIN'
    user: str = 'USER'

class Settings(BaseSettings):
    """ Get settings from .env file. """
    database_admin: str
    database_admin_password: str
    database_default_name: str
    sample_service_host: str
    database_external_port: str
    database_name: str
    database_user: str
    database_password: str

    model_config = ConfigDict(extra='ignore', env_file = ".env")

    def get_connection(self, role: ConnectionRole):
        """ Return connection to db. """

        if role == ConnectionRole.admin:
            database_name = self.database_default_name
            database_user = self.database_admin
            database_password = self.database_admin_password
        elif role == ConnectionRole.user:
            database_name = self.database_name
            database_user = self.database_user
            database_password = self.database_password
        else:
            raise psycopg2.DataError()

        ready_flag = False
        counter = 0
        while not ready_flag:
            time.sleep(1)
            try:
                connection = psycopg2.connect(
                    dbname=database_name,
                    user=database_user,
                    password=database_password,
                    host=self.sample_service_host,
                    port=self.database_external_port
                )
                ready_flag = True
                print(f"Connection attempt #{counter}")
            except(psycopg2.OperationalError) as exc:
                print(exc)
                counter += 1
        return connection

settings = Settings()

def create_database():
    """ Creating database. """
    connection = settings.get_connection(ConnectionRole.admin)

    connection.autocommit = True
    cursor_default = connection.cursor()

    try:
        cursor_default.execute(f"CREATE DATABASE {settings.database_name};")
    except psycopg2.errors.DuplicateDatabase as ex:
        print(ex)

    try:
        cursor_default.execute(f"CREATE USER {settings.database_user} WITH PASSWORD '{settings.database_password}';")
    except psycopg2.errors.DuplicateObject as ex:
        print(ex)

    try:
        cursor_default.execute(f"GRANT ALL ON DATABASE {settings.database_name} TO {settings.database_user};")
    except psycopg2.errors.InvalidCatalogName as ex:
        print(ex)

    cursor_default.execute(f"ALTER DATABASE {settings.database_name} OWNER TO {settings.database_user};")

    cursor_default.close()
    connection.close()

def create_tables():
    connection = settings.get_connection(ConnectionRole.user)

    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE tasks (id SERIAL PRIMARY KEY, start_timestamp VARCHAR, finish_timestamp VARCHAR, description VARCHAR NOT NULL, duration VARCHAR);")

    cursor.close()
    connection.close()

if __name__ == "__main__":

    create_database()
    create_tables()
