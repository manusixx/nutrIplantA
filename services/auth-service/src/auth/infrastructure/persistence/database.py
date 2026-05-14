"""
Factory para crear sesiones SQLAlchemy async.

Vive en infrastructure. Se conecta a PostgreSQL usando los parámetros
de configuración inyectados.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    """Crear el engine asíncrono de SQLAlchemy."""
    return create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Crear la fábrica de sesiones."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Generador de sesiones con manejo automático de cierre.

    Usado por FastAPI Depends() para inyectar sesión por request.
    """
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
