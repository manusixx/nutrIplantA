"""
Configuración del auth-service vía variables de entorno.

Usa pydantic-settings para validación tipada de la configuración.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración cargada desde variables de entorno."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_env: str = Field(default="development", description="Entorno: development | staging | production")
    log_level: str = Field(default="INFO")

    # --- Database ---
    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="nutriplanta")
    postgres_password: str = Field(default="changeme")
    postgres_db: str = Field(default="nutriplanta")

    # --- JWT ---
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=15, ge=1, le=60)
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1, le=30)

    @property
    def database_url(self) -> str:
        """URL de conexión async a PostgreSQL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """URL de conexión sync (para Alembic, que no soporta async)."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Singleton de configuración (cacheado)."""
    return Settings()  # type: ignore[call-arg]
