"""
Dependencias FastAPI para inyección por request.

Coordina el container global con la sesión de BD por request.
"""
from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.config import Settings
from auth.domain.services.admin_service import AdminService
from auth.domain.services.auth_service import AuthService
from auth.domain.services.session_service import SessionService
from auth.domain.services.token_service import TokenService
from auth.infrastructure.persistence.postgres_refresh_token_repository import (
    PostgresRefreshTokenRepository,
)
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


async def get_session_service(
    request: Request,
    user_repository: PostgresUserRepository = Depends(get_user_repository),
    session: AsyncSession = Depends(get_db_session),
) -> SessionService:
    """Construir el SessionService con persistencia real en PostgreSQL."""
    password_hasher = request.app.state.container.password_hasher()
    token_service: TokenService = request.app.state.container.token_service()
    auth_svc = AuthService(
        user_repository=user_repository,
        password_hasher=password_hasher,
    )
    rt_repo = PostgresRefreshTokenRepository(session=session)
    return SessionService(
        auth_service=auth_svc,
        token_service=token_service,
        refresh_token_repo=rt_repo,
        user_repo=user_repository,
        refresh_token_expire_days=7,
    )
async def get_admin_service(
    user_repository: PostgresUserRepository = Depends(get_user_repository),
) -> AdminService:
    """Construir el AdminService."""
    return AdminService(user_repository=user_repository)
