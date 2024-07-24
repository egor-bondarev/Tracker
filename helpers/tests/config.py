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