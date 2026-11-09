from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import (
    ValidationError,
    Field,
    BaseModel,
    PostgresDsn,
    MySQLDsn,
    CockroachDsn,
    RedisDsn,
    AmqpDsn,
    BeforeValidator,
    field_validator,
)

from typing import Annotated, Literal

#Application mode
app_mode = "dev"

class Settings(BaseSettings):
    app_name: str = "merely one amongs many application"
    mode: Literal["prod", "dev"] = app_mode

    db_dsn: PostgresDsn | None = Field(alias="DATABASE_URL")
    db_pool_size: int = Field(ge=10, default=10)
    db_burst_tolerance: int = Field(default=15)

    redis_dsn: RedisDsn | None = Field(default=None, alias="REDIS_URL")
    
    jwt_algo: list[str] | None = Field(default=None, alias="JWT_ALGO")
    jwt_private_key: str | None = Field(default=None, alias="PRIVATE_KEY")
    jwt_public_key: str | None = Field(default=None, alias="PUBLIC_KEY")
    jwt_secret_key: str | None = Field(default=None, alias="SECRET_KEY")

    jwt_expire_min: int | None = Field(alias="JWT_EXPIRE_MIN")

    @field_validator("jwt_algo", mode="before")
    @classmethod
    def str_to_list(cls, v):
        if isinstance(v, str):
            result = v.split(",")
            return result
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid"
    )

settings = Settings()
