"""Database connection settings shared by the Tracker services."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    """Application role connection settings, read from the environment or ./.env."""

    model_config = SettingsConfigDict(extra='ignore', env_file='./.env', hide_input_in_errors=True)

    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str

    @property
    def db_url(self) -> URL:
        """SQLAlchemy URL for the application role."""
        return URL.create(
            'postgresql+psycopg2',
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
        )
