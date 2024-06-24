""" Creating database. """

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_database():
    postgres_admin = os.getenv('DATABASE_ADMIN')
    postgres_admin_password = os.getenv('DATABASE_ADMIN_PASSWORD')
    postgres_db_default = os.getenv('DATABASE_DEFAULT_NAME')
    postgres_host = os.getenv('SAMPLE_SERVICE_HOST')
    postgres_port = os.getenv('DATABASE_EXTERNAL_PORT')

    postgres_user = os.getenv('DATABASE_USER')
    postgres_password = os.getenv('DATABASE_PASSWORD')
    postgres_db = os.getenv('DATABASE_NAME')

    default_connection = psycopg2.connect(
        dbname=postgres_db_default,
        user=postgres_admin,
        password=postgres_admin_password,
        host=postgres_host,
        port=postgres_port
    )

    default_connection.autocommit = True
    cursor_default = default_connection.cursor()

    #TODO: Redo to crud approach. for testing docker-compose i need to recreate table each time.
    # Create new database and user
    try:
        cursor_default.execute(f"CREATE DATABASE {postgres_db};")
    except psycopg2.errors.DuplicateDatabase as ex:
        print(ex)

    try:
        cursor_default.execute(f"CREATE USER {postgres_user} WITH PASSWORD '{postgres_password}';")
    except psycopg2.errors.DuplicateObject as ex:
        print(ex)

    try:
        cursor_default.execute(f"GRANT ALL ON DATABASE {postgres_db} TO {postgres_user};")
    except psycopg2.errors.InvalidCatalogName as ex:
        print(ex)

    cursor_default.execute(f"ALTER DATABASE {postgres_db} OWNER TO {postgres_user};")

    cursor_default.close()
    default_connection.close()

def create_tables():
    postgres_user = os.getenv('DATABASE_USER')
    postgres_password = os.getenv('DATABASE_PASSWORD')
    postgres_db = os.getenv('DATABASE_NAME')
    postgres_host = os.getenv('SAMPLE_SERVICE_HOST')
    postgres_port = os.getenv('DATABASE_EXTERNAL_PORT')

    connection = psycopg2.connect(
        dbname=postgres_db,
        user=postgres_user,
        password=postgres_password,
        host=postgres_host,
        port=postgres_port
    )

    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL);")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    create_database()
    create_tables()
