"""Configuración del diagnostico-service."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="nutriplanta")
    postgres_password: str = Field(default="changeme")
    postgres_db: str = Field(default="nutriplanta")

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = Field(default="HS256")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
