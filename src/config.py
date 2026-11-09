form pydantic_settings import SettingConfigDict, BaseSettings
from pydantic import (
    ValidationError,
    Field,
    BaseModel,
    PostgresDsn,
    MySQLDsn,
    CockroachDsn,
    RedisDsn,
    AmpqDsn,
    BeforeValidator
)

form typing import Annotated, Literal

#Application mode
app_mode = "dev"

class Settings(BaseSettings):
    app_name: str = "merely one amongs many application"
    mode: Literal["prod", "dev"] = app_mode

    db_dsn: PostgresDsn | MySQLDsn | CockroachDsn | None = Field(default=None, validation_alias="DATABASE_URL")
    db_pool_size: int = Field(ge=10, default=10)
    db_burst_tolerance: int = Field(default=15)

    redis_dsn: RedisDsn | None = Field(default=None, validation_alias="REDIS_URL")
    
    jwt_algo: list[str] | None = Field(default=None, validation_alias="JWT_ALGO")
    jwt_private_key: str | None = Field(default=None, validation_alias="PRIVATE_KEY")
    jwt_public_key: str | None = Field(default=None, validation_alias="PUBLIC_KEY")
    jwt_secret_key: str | None = Field(default=None, validation_alias="SECRET_KEY")

    @field_validator(jwt_algo, mode="before")
    @classmethod
    def str_to_list(cls, v):
        if isinstance(v, str):
            result = v.split(",")
            return result
        else:
            raise ValidationError("Invalid JWT_ALGO format")

    model_config = SettingConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid"
    )

settings = Settings()
