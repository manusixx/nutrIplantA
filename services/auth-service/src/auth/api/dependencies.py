"""
Dependencias FastAPI para inyección por request.

Coordina el container global con la sesión de BD por request.
"""
from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.config import Settings
from auth.domain.services.auth_service import AuthService
from auth.infrastructure.persistence.postgres_user_repository import (
    PostgresUserRepository,
)


async def get_settings_dep(request: Request) -> Settings:
    """Obtener Settings desde el container."""
    settings: Settings = request.app.state.container.config()
    return settings


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Sesión de BD por request, con cierre automático."""
    session_factory = request.app.state.container.session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgresUserRepository:
    """Construir el repositorio con la sesión actual."""
    return PostgresUserRepository(session=session)


async def get_auth_service(
    request: Request,
    user_repository: PostgresUserRepository = Depends(get_user_repository),
) -> AuthService:
    """Construir el AuthService con sus dependencias."""
    password_hasher = request.app.state.container.password_hasher()
    return AuthService(
        user_repository=user_repository,
        password_hasher=password_hasher,
    )
