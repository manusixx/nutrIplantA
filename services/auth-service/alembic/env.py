"""Alembic environment script (síncrono)."""
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Importar el modelo SQLAlchemy para que Alembic detecte cambios
from auth.infrastructure.persistence.user_model import Base  # noqa: F401

config = context.config

# URL de BD desde env vars (sobrescribe la del alembic.ini)
postgres_user = os.getenv("POSTGRES_USER", "nutriplanta")
postgres_password = os.getenv("POSTGRES_PASSWORD", "changeme")
postgres_host = os.getenv("POSTGRES_HOST", "postgres")
postgres_port = os.getenv("POSTGRES_PORT", "5432")
postgres_db = os.getenv("POSTGRES_DB", "nutriplanta")

config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}",
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Migraciones en modo offline (genera SQL sin conectar)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Migraciones online (conecta a la BD)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
