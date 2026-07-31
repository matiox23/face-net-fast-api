from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_name: str = Field(default="")
    database_username: str = Field(default="")
    database_password: str = Field(default="")
    database_host: str = Field(default="")
    database_port: int = Field(default=5432)
    database_ssl: str = Field(default="prefer")

    database_debug: bool = Field(default=False)
    database_pool_size: int = Field(default=5)
    database_max_overflow: int = Field(default=10)
    database_pool_recycle: int = Field(default=3600)

    jwt_secret_key: str = Field(default="")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expires_minutes: int = Field(default=30)
    jwt_refresh_token_expires_days: int = Field(default=14)


base_config = BaseConfig()
