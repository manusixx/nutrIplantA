"""Tests unitarios del SessionService: login, logout y refresh."""
from uuid import uuid4

import pytest

from auth.domain.exceptions import InvalidCredentialsError, UserNotApprovedError
from auth.domain.exceptions.token_exceptions import (
    InvalidRefreshTokenError,
    TokenReuseDetectedError,
)
from auth.domain.models.refresh_token import RefreshToken
from auth.domain.models.user import User, UserRole
from auth.domain.services.auth_service import AuthService
from auth.domain.services.session_service import SessionService
from auth.domain.services.token_service import TokenService
from auth.infrastructure.persistence.in_memory_refresh_token_repository import (
    InMemoryRefreshTokenRepository,
)
from auth.infrastructure.persistence.in_memory_user_repository import (
    InMemoryUserRepository,
)

TEST_SECRET = "s" * 64


@pytest.fixture
def token_service() -> TokenService:
    return TokenService(secret_key=TEST_SECRET)


@pytest.fixture
def rt_repo() -> InMemoryRefreshTokenRepository:
    return InMemoryRefreshTokenRepository()


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def session_service(
    fake_hasher,
    token_service: TokenService,
    rt_repo: InMemoryRefreshTokenRepository,
    user_repo: InMemoryUserRepository,
) -> SessionService:
    auth_svc = AuthService(user_repo, fake_hasher)
    return SessionService(
        auth_service=auth_svc,
        token_service=token_service,
        refresh_token_repo=rt_repo,
        user_repo=user_repo,
    )


@pytest.fixture
async def approved_user(user_repo: InMemoryUserRepository, fake_hasher) -> User:
    """Usuario aprobado y persistido en el repo."""
    from auth.domain.services.auth_service import AuthService
    svc = AuthService(user_repo, fake_hasher)
    user = await svc.register("user@test.com", "Usuario Test", "MiP@ssw0rd!")
    user.approve(UserRole.AGRICULTOR)
    await user_repo.save(user)
    return user


class TestSessionServiceLogin:
    """Comportamiento del login."""

    @pytest.mark.asyncio
    async def test_login_exitoso_devuelve_access_y_refresh(
        self, session_service: SessionService, approved_user: User
    ) -> None:
        access, refresh = await session_service.login("user@test.com", "MiP@ssw0rd!")

        assert isinstance(access, str)
        assert len(access) > 50
        assert isinstance(refresh, RefreshToken)
        assert refresh.is_valid

    @pytest.mark.asyncio
    async def test_login_persiste_refresh_token(
        self,
        session_service: SessionService,
        rt_repo: InMemoryRefreshTokenRepository,
        approved_user: User,
    ) -> None:
        _, refresh = await session_service.login("user@test.com", "MiP@ssw0rd!")

        stored = await rt_repo.find_by_jti(refresh.jti)
        assert stored is not None
        assert stored.user_id == approved_user.id

    @pytest.mark.asyncio
    async def test_login_falla_con_credenciales_invalidas(
        self, session_service: SessionService
    ) -> None:
        with pytest.raises(InvalidCredentialsError):
            await session_service.login("noexiste@test.com", "MiP@ssw0rd!")

    @pytest.mark.asyncio
    async def test_login_falla_si_usuario_pendiente(
        self,
        session_service: SessionService,
        user_repo: InMemoryUserRepository,
        fake_hasher,
    ) -> None:
        from auth.domain.services.auth_service import AuthService
        svc = AuthService(user_repo, fake_hasher)
        await svc.register("pendiente@test.com", "Pendiente", "MiP@ssw0rd!")
        # Sin aprobar

        with pytest.raises(UserNotApprovedError):
            await session_service.login("pendiente@test.com", "MiP@ssw0rd!")


class TestSessionServiceLogout:
    """Comportamiento del logout."""

    @pytest.mark.asyncio
    async def test_logout_revoca_refresh_token(
        self,
        session_service: SessionService,
        rt_repo: InMemoryRefreshTokenRepository,
        approved_user: User,
    ) -> None:
        _, refresh = await session_service.login("user@test.com", "MiP@ssw0rd!")

        await session_service.logout(refresh.jti)

        stored = await rt_repo.find_by_jti(refresh.jti)
        assert stored is not None
        assert stored.is_revoked

    @pytest.mark.asyncio
    async def test_logout_es_idempotente(
        self, session_service: SessionService, approved_user: User
    ) -> None:
        """Hacer logout dos veces no falla."""
        _, refresh = await session_service.login("user@test.com", "MiP@ssw0rd!")

        await session_service.logout(refresh.jti)
        await session_service.logout(refresh.jti)  # No debe lanzar

    @pytest.mark.asyncio
    async def test_logout_con_jti_inexistente_no_falla(
        self, session_service: SessionService
    ) -> None:
        await session_service.logout(uuid4())  # No debe lanzar


class TestSessionServiceRefresh:
    """Comportamiento del refresh de tokens."""

    @pytest.mark.asyncio
    async def test_refresh_valido_rota_el_token(
        self,
        session_service: SessionService,
        rt_repo: InMemoryRefreshTokenRepository,
        approved_user: User,
    ) -> None:
        _, refresh_original = await session_service.login("user@test.com", "MiP@ssw0rd!")

        new_access, new_refresh = await session_service.refresh(refresh_original.jti)

        # Token original debe estar revocado
        original_stored = await rt_repo.find_by_jti(refresh_original.jti)
        assert original_stored is not None
        assert original_stored.is_revoked

        # Nuevo token debe estar activo y ser hijo del original
        assert new_refresh.is_valid
        assert new_refresh.parent_jti == refresh_original.jti
        assert isinstance(new_access, str)

    @pytest.mark.asyncio
    async def test_refresh_con_jti_inexistente_falla(
        self, session_service: SessionService
    ) -> None:
        with pytest.raises(InvalidRefreshTokenError):
            await session_service.refresh(uuid4())

    @pytest.mark.asyncio
    async def test_reuso_de_token_rotado_revoca_todos_y_lanza_error(
        self,
        session_service: SessionService,
        rt_repo: InMemoryRefreshTokenRepository,
        approved_user: User,
    ) -> None:
        """
        Si alguien reusa un token ya rotado, es señal de robo.
        El sistema debe revocar todos los tokens del usuario.
        """
        _, refresh_original = await session_service.login("user@test.com", "MiP@ssw0rd!")

        # Rotar el token (uso legítimo)
        _, new_refresh = await session_service.refresh(refresh_original.jti)

        # Reusar el token original ya rotado (posible atacante)
        with pytest.raises(TokenReuseDetectedError):
            await session_service.refresh(refresh_original.jti)

        # Todos los tokens del usuario deben estar revocados
        activos = await rt_repo.find_active_by_user(approved_user.id)
        assert len(activos) == 0

    @pytest.mark.asyncio
    async def test_refresh_con_token_expirado_falla(
        self,
        session_service: SessionService,
        user_repo: InMemoryUserRepository,
        rt_repo: InMemoryRefreshTokenRepository,
        approved_user: User,
    ) -> None:
        from datetime import UTC, datetime, timedelta

        # Crear token ya expirado y guardarlo directamente
        token_expirado = RefreshToken(
            user_id=approved_user.id,
            expires_at=datetime.now(UTC) - timedelta(hours=1),  # ya expiró
        )
        await rt_repo.save(token_expirado)

        with pytest.raises(InvalidRefreshTokenError):
            await session_service.refresh(token_expirado.jti)
