"""Tests de integración para endpoints de sesión: login, logout, refresh."""
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from auth.api.dependencies import get_session_service
from auth.api.exception_handler import register_exception_handlers
from auth.api.routes.auth_routes import router as auth_router
from auth.api.routes.session_routes import router as session_router
from auth.domain.exceptions import InvalidCredentialsError, UserNotApprovedError
from auth.domain.exceptions.token_exceptions import (
    InvalidRefreshTokenError,
    TokenReuseDetectedError,
)
from auth.domain.models.refresh_token import RefreshToken
from auth.domain.models.user import User, UserRole, UserStatus
from auth.domain.services.session_service import SessionService


def make_approved_user() -> User:
    user = User(
        email="test@example.com",
        full_name="Test User",
        password_hash="fake-hashed:MiP@ssw0rd!",
        role=UserRole.AGRICULTOR,
        status=UserStatus.APROBADO,
    )
    return user


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(session_router)
    return app


class TestLoginEndpoint:
    @pytest.mark.asyncio
    async def test_login_exitoso_devuelve_access_token(
        self, test_app: FastAPI
    ) -> None:
        user = make_approved_user()
        refresh = RefreshToken.create(user.id)

        mock_service = AsyncMock(spec=SessionService)
        mock_service.login.return_value = ("access.token.fake", refresh)

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "MiP@ssw0rd!"},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"] == "access.token.fake"
        assert body["token_type"] == "bearer"
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_credenciales_invalidas_da_401(
        self, test_app: FastAPI
    ) -> None:
        mock_service = AsyncMock(spec=SessionService)
        mock_service.login.side_effect = InvalidCredentialsError()

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "x@x.com", "password": "wrong"},
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_usuario_pendiente_da_403(
        self, test_app: FastAPI
    ) -> None:
        mock_service = AsyncMock(spec=SessionService)
        mock_service.login.side_effect = UserNotApprovedError()

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "x@x.com", "password": "MiP@ssw0rd!"},
            )

        assert response.status_code == 403


class TestLogoutEndpoint:
    @pytest.mark.asyncio
    async def test_logout_exitoso_elimina_cookie(
        self, test_app: FastAPI
    ) -> None:
        mock_service = AsyncMock(spec=SessionService)
        mock_service.logout.return_value = None

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        jti = str(uuid4())

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/logout",
                cookies={"refresh_token": jti},
            )

        assert response.status_code == 200
        body = response.json()
        assert "cerrada" in body["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_sin_cookie_no_falla(
        self, test_app: FastAPI
    ) -> None:
        mock_service = AsyncMock(spec=SessionService)

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200


class TestRefreshEndpoint:
    @pytest.mark.asyncio
    async def test_refresh_valido_devuelve_nuevo_token(
        self, test_app: FastAPI
    ) -> None:
        user_id = uuid4()
        new_refresh = RefreshToken.create(user_id)

        mock_service = AsyncMock(spec=SessionService)
        mock_service.refresh.return_value = ("new.access.token", new_refresh)

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        jti = str(uuid4())

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/refresh",
                cookies={"refresh_token": jti},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"] == "new.access.token"

    @pytest.mark.asyncio
    async def test_refresh_sin_cookie_da_401(
        self, test_app: FastAPI
    ) -> None:
        mock_service = AsyncMock(spec=SessionService)

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_invalido_da_401(
        self, test_app: FastAPI
    ) -> None:
        mock_service = AsyncMock(spec=SessionService)
        mock_service.refresh.side_effect = InvalidRefreshTokenError()

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        jti = str(uuid4())

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/refresh",
                cookies={"refresh_token": jti},
            )

        assert response.status_code == 401
        assert response.json()["error"] == "invalid_refresh_token"

    @pytest.mark.asyncio
    async def test_refresh_reuso_detectado_da_401(
        self, test_app: FastAPI
    ) -> None:
        mock_service = AsyncMock(spec=SessionService)
        mock_service.refresh.side_effect = TokenReuseDetectedError()

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        jti = str(uuid4())

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/refresh",
                cookies={"refresh_token": jti},
            )

        assert response.status_code == 401
        assert response.json()["error"] == "token_reuse_detected"

    @pytest.mark.asyncio
    async def test_refresh_con_jti_no_uuid_da_401(
        self, test_app: FastAPI
    ) -> None:
        mock_service = AsyncMock(spec=SessionService)

        test_app.dependency_overrides[get_session_service] = lambda: mock_service

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/refresh",
                cookies={"refresh_token": "esto-no-es-uuid"},
            )

        assert response.status_code == 401
