''' Settings for db connection. '''
import os
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, ValidationError, ConfigDict
#from pydantic_core.core_schema import FieldValidationInfo
from typing import Any, Optional

class Settings(BaseSettings):
    ''' Settings for db connection. '''
    model_config = ConfigDict(extra='ignore', env_file = "../../.env.testing") 

    DATABASE_USER: str = os.getenv('DATABASE_USER')
    DATABASE_PASSWORD: str = os.getenv('DATABASE_PASSWORD')
    DATABASE_HOST: str = os.getenv('DATABASE_HOST')
    DATABASE_PORT: int = os.getenv('DATABASE_PORT')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME')
    DATABASE_URI: PostgresDsn | str = ""
    # DATABASE_USER: str
    # DATABASE_PASSWORD: str
    # DATABASE_HOST: str
    # DATABASE_PORT: int
    # DATABASE_NAME: str
    # DATABASE_ADMIN: str
    # DATABASE_ADMIN_PASSWORD: str
    # DATABASE_DEFAULT_NAME: str
    # SAMPLE_SERVICE_HOST: str
    # SAMPLE_SERVICE_PORT: str
    # DATABASE_ROLE: str
    # @field_validator("DATABASE_URI", mode="after")
    # def assemble_db_connection(self, cls, v: str | None, info: FieldValidationInfo) -> Any:
    #     if isinstance(v, str):
    #         if v == "":
    #             return PostgresDsn.build(
    #                 scheme="postgresql",
    #                 username=info.data["DATABASE_USER"],
    #                 password=info.data["DATABASE_PASSWORD"],
    #                 host=info.data["DATABASE_HOST"],
    #                 port=info.data["DATABASE_PORT"],
    #                 path=info.data["DATABASE_NAME"],
    #             )
    #     print(info.data["DATABASE_USER"])
    #     return v
    # db_user: str = Field(..., env='DATABASE_USER')
    # db_password: str = Field(..., env='DATABASE_PASSWORD')
    # db_host: str = Field(..., env='DATABASE_HOST')
    # db_port: str = Field(..., env='DATABASE_PORT')
    # db_name: str = Field(..., env='DATABASE_NAME')
    # database_url: Optional[PostgresDsn] = None
    
    # print('*******')
    # print(db_name)
    # print('*******')
    # print()

    # def model_post_init(self, __context):
    #     self.database_url = PostgresDsn.build(
    #         scheme="postgresql",
    #         user=self.db_user,
    #         password=self.db_password,
    #         host=self.db_host,
    #         port=self.db_port,
    #         path=f"/{self.db_name or ''}"
    #     )

    # class Config:
    #     ''' Get config .env file. '''
        
    #     env_file = "../../.env.testing"
        
        
    
    @property
    def get_db_url(self) -> PostgresDsn:
        ''' Generate db url. '''
        print(self.DATABASE_USER)
        print('*********')
        
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
