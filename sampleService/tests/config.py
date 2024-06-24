""" Configurate client for Rest Api and for db. """
from pydantic_settings import BaseSettings, SettingsConfigDict

class ClientSettings(BaseSettings):
    SAMPLE_SERVICE_HOST: str
    SAMPLE_SERVICE_PORT: str
    SAMPLE_SERVICE_PATH: str

    model_config = SettingsConfigDict(
        env_file="./sampleService/.env.testing",
        hide_input_in_errors=True,
        extra='ignore')

    @property
    def service_url(self) -> str:
        return f"http://{self.SAMPLE_SERVICE_HOST}:{self.SAMPLE_SERVICE_PORT}/{self.SAMPLE_SERVICE_PATH}"

class Settings(BaseSettings):
    database_user: str
    DATABASE_PASSWORD: str
    SAMPLE_SERVICE_HOST: str
    DATABASE_EXTERNAL_PORT: int
    DATABASE_NAME: str

    model_config = SettingsConfigDict(
        env_file="./sampleService/.env.testing",
        hide_input_in_errors=True,
        extra='ignore')
