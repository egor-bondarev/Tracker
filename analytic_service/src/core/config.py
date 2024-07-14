''' Settings for db connection. '''
#TODO: to avoid duplicate this model in different services move it to external module for all services.

import os
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, ValidationError, ConfigDict

class Settings(BaseSettings):
    ''' Settings for db connection. '''

    model_config = ConfigDict(extra='ignore', env_file = "./.env")

    DATABASE_USER: str = os.getenv('DATABASE_USER')
    DATABASE_PASSWORD: str = os.getenv('DATABASE_PASSWORD')
    DATABASE_HOST: str = os.getenv('DATABASE_HOST')
    DATABASE_PORT: int = os.getenv('DATABASE_PORT')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME')
    DATABASE_URI: PostgresDsn | str = ""

    @property
    def get_db_url(self) -> PostgresDsn:
        ''' Generate db url. '''

        try:
            conn = PostgresDsn.build(
                scheme='postgresql',
                hosts=None,
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOST,
                port=self.DATABASE_PORT,
                path=f"{self.DATABASE_NAME}"
            ).unicode_string()
        except ValidationError as exc:
            print(repr(exc.errors()[0]['type']))
        return conn

settings = Settings()
