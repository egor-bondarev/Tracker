""" Configurate client for Rest Api and for db. """

from pydantic_settings import BaseSettings, SettingsConfigDict

class ClientSettings(BaseSettings):
    RECORD_SERVICE_HOST: str
    RECORD_SERVICE_PORT: str

    model_config = SettingsConfigDict(
        env_file="./.env",
        hide_input_in_errors=True,
        extra='ignore')

    @property
    def service_url(self) -> str:
        return f"http://{self.RECORD_SERVICE_HOST}:{self.RECORD_SERVICE_PORT}/add-record"

    @property
    def base_url(self) -> str:
        return f"http://{self.RECORD_SERVICE_HOST}:{self.RECORD_SERVICE_PORT}"

class AnalyticsSettings(BaseSettings):
    ANALYTIC_SERVICE_HOST: str
    ANALYTIC_SERVICE_PORT: str

    model_config = SettingsConfigDict(
        env_file="./.env",
        hide_input_in_errors=True,
        extra='ignore')

    @property
    def graphql_url(self) -> str:
        return f"http://{self.ANALYTIC_SERVICE_HOST}:{self.ANALYTIC_SERVICE_PORT}/graphql"

class WebSettings(BaseSettings):
    """The web UI port is fixed in docker-compose.yml; override for other setups."""
    WEB_URL: str = "http://127.0.0.1:8080"

    model_config = SettingsConfigDict(
        env_file="./.env",
        hide_input_in_errors=True,
        extra='ignore')

    @property
    def web_url(self) -> str:
        return self.WEB_URL.rstrip("/")

class Settings(BaseSettings):
    database_user: str
    DATABASE_PASSWORD: str
    RECORD_SERVICE_HOST: str
    DATABASE_EXTERNAL_PORT: int
    DATABASE_NAME: str

    model_config = SettingsConfigDict(
        env_file="./.env",
        hide_input_in_errors=True,
        extra='ignore')
