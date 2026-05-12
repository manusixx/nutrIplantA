"""
Contenedor de Inyección de Dependencias.

Usa dependency-injector para wirear interfaces con implementaciones.
Es el ÚNICO archivo que importa de las tres capas (api, domain,
infrastructure).
"""
from dependency_injector import containers, providers

from auth.config import Settings
from auth.domain.services.auth_service import AuthService
from auth.domain.services.session_service import SessionService
from auth.domain.services.token_service import TokenService
from auth.infrastructure.persistence.database import (
    create_engine,
    create_session_factory,
)
from auth.infrastructure.persistence.in_memory_refresh_token_repository import (
    InMemoryRefreshTokenRepository,
)
from auth.infrastructure.persistence.postgres_user_repository import (
    PostgresUserRepository,
)
from auth.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)


class Container(containers.DeclarativeContainer):
    """Container principal del auth-service."""

    # Configuración
    config = providers.Singleton(Settings)

    # --- Infrastructure ---
    engine = providers.Singleton(
        create_engine,
        database_url=config.provided.database_url,
        echo=False,
    )

    session_factory = providers.Singleton(
        create_session_factory,
        engine=engine,
    )

    password_hasher = providers.Singleton(Argon2PasswordHasher)

    # --- Repositorios ---
    user_repository = providers.Factory(
        PostgresUserRepository,
        # session se inyecta por dependencia FastAPI en runtime
    )

    refresh_token_repository = providers.Factory(
        InMemoryRefreshTokenRepository,
        # En producción: PostgresRefreshTokenRepository con sesión por request
    )

    # --- Domain services ---
    token_service = providers.Singleton(
        TokenService,
        secret_key=config.provided.jwt_secret_key,
        algorithm=config.provided.jwt_algorithm,
        access_token_expire_minutes=config.provided.jwt_access_token_expire_minutes,
    )

    auth_service = providers.Factory(
        AuthService,
        password_hasher=password_hasher,
        # user_repository se inyecta en cada request via dependencies.py
    )

    session_service = providers.Factory(
        SessionService,
        auth_service=auth_service,
        token_service=token_service,
        refresh_token_repo=refresh_token_repository,
        user_repository=user_repository,
        refresh_token_expire_days=config.provided.jwt_refresh_token_expire_days,
    )
