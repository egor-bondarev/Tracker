from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
import os

class Settings(BaseSettings):
    DATABASE_USER: str = os.getenv('DATABASE_USER')
    DATABASE_PASSWORD: str = os.getenv('DATABASE_PASSWORD')
    DATABASE_HOST: str = os.getenv('DATABASE_HOST')
    DATABASE_PORT: int = os.getenv('DATABASE_PORT')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME')
    
    class Config:
        env_file = "../../.env"
        
    @property
    def get_db_url(self) -> PostgresDsn:
        print(self.DATABASE_NAME)
        conn = PostgresDsn.build(
            scheme='postgresql',
            hosts=None,
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            path=f"{self.DATABASE_NAME}",
        ).unicode_string()
        print(conn)
        return conn

settings = Settings()