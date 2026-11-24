from __future__ import annotations

import codecs
from typing import Literal

from pydantic import (
    Field,
    PostgresDsn,
    RedisDsn,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# Application mode
app_mode = "dev"


class Settings(BaseSettings):
    app_title: str = "merely one amongs many application"
    app_description: str = "merely a simple description"
    app_version: str = "0.0.1"
    license_info: dict = {
        "name": "MIT License",
        "identifier": "MIT",
    }

    mode: Literal["prod", "dev"] = "dev"
    openapi_url: str = Field(default="/openapi.json", alias="OPENAPI_URL")

    db_dsn: PostgresDsn | None = Field(alias="DATABASE_URL")
    db_pool_size: int = Field(ge=10, default=10)
    db_burst_tolerance: int = Field(default=15)

    redis_dsn: RedisDsn | None = Field(default=None, alias="REDIS_URL")

    jwt_algo: list[str] | None = Field(default=None, alias="JWT_ALGO")
    jwt_private_key: str | None = Field(default=None, alias="PRIVATE_KEY")
    jwt_public_key: str | None = Field(default=None, alias="PUBLIC_KEY")
    jwt_secret_key: str | None = Field(default=None, alias="SECRET_KEY")

    api_key_expire_day: int | None = Field(alias="API_KEY_EXPIRE_DAY")
    jwt_expire_min: int | None = Field(alias="JWT_EXPIRE_MIN")

    @field_validator("jwt_private_key", "jwt_public_key", mode="before")
    @classmethod
    def validate_rsa_key(cls, v):
        if v is None:
            return v
        return codecs.decode(v, "unicode_escape").replace("\r", "")

    @field_validator("jwt_algo", mode="before")
    @classmethod
    def str_to_list(cls, v):
        if isinstance(v, str):
            result = v.split(",")
            return result
        return v

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


app_title = "Warehouse Management"
app_description = "Web application for managing warehouse"

settings = Settings(
    app_title=app_title,
    app_description=app_description,
)
