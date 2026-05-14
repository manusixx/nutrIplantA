"""
Tests de integración del endpoint POST /api/v1/auth/register.

Levantan FastAPI con dependencias overrideadas para usar
InMemoryUserRepository (no requiere PostgreSQL).
"""
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from auth.api.dependencies import get_auth_service
from auth.api.exception_handler import register_exception_handlers
from auth.api.routes.auth_routes import router as auth_router
from auth.domain.services.auth_service import AuthService
from auth.infrastructure.persistence.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def test_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def test_app(test_repo, fake_hasher) -> FastAPI:
    """App de prueba con dependencias mockeadas."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(auth_router)

    async def override_auth_service() -> AuthService:
        return AuthService(test_repo, fake_hasher)

    app.dependency_overrides[get_auth_service] = override_auth_service
    return app


class TestRegisterEndpoint:
    """Comportamiento del endpoint POST /api/v1/auth/register."""

    @pytest.mark.asyncio
    async def test_registra_usuario_y_responde_201(self, test_app, test_repo) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "nuevo@example.com",
                    "full_name": "Usuario Nuevo",
                    "password": "MiP@ssw0rd!",
                },
            )

        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "nuevo@example.com"
        assert body["full_name"] == "Usuario Nuevo"
        assert body["status"] == "PENDIENTE_APROBACION"
        assert "id" in body
        assert "message" in body
        assert test_repo.count == 1

    @pytest.mark.asyncio
    async def test_responde_409_si_email_duplicado(self, test_app) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            payload = {
                "email": "duplicado@example.com",
                "full_name": "Uno",
                "password": "MiP@ssw0rd!",
            }
            await client.post("/api/v1/auth/register", json=payload)
            response = await client.post(
                "/api/v1/auth/register",
                json={**payload, "full_name": "Dos"},
            )

        assert response.status_code == 409
        body = response.json()
        assert body["error"] == "email_already_registered"
        assert "ya está registrado" in body["message"]

    @pytest.mark.asyncio
    async def test_responde_422_si_email_invalido(self, test_app) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "no-es-un-email",
                    "full_name": "Usuario",
                    "password": "MiP@ssw0rd!",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_responde_422_si_password_debil(self, test_app) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "user@example.com",
                    "full_name": "Usuario",
                    "password": "corta",  # No cumple regla
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_responde_422_si_falta_campo(self, test_app) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={"email": "user@example.com"},
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_health_endpoint_responde(self, test_app) -> None:
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/auth/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == "auth-service"

    @pytest.mark.asyncio
    async def test_responde_500_si_excepcion_no_controlada(
        self, test_app, fake_hasher
    ) -> None:
        """El handler genérico debe responder 500 con mensaje en español."""
        from auth.api.dependencies import get_auth_service
        from auth.domain.repositories.i_user_repository import IUserRepository
        from auth.domain.services.auth_service import AuthService

        class BrokenRepo(IUserRepository):
            """Repositorio que falla siempre con excepción no controlada."""

            async def save(self, user):  # type: ignore[no-untyped-def]
                raise RuntimeError("BD caída inesperadamente")

            async def find_by_email(self, email):  # type: ignore[no-untyped-def]
                return None

            async def find_by_id(self, user_id):  # type: ignore[no-untyped-def]
                return None

            async def email_exists(self, email):  # type: ignore[no-untyped-def]
                return False

        async def override_broken() -> AuthService:
            return AuthService(BrokenRepo(), fake_hasher)

        test_app.dependency_overrides[get_auth_service] = override_broken

        async with AsyncClient(
            transport=ASGITransport(app=test_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "user@example.com",
                    "full_name": "Usuario",
                    "password": "MiP@ssw0rd!",
                },
            )

        assert response.status_code == 500
        body = response.json()
        assert body["error"] == "internal_error"
        assert "intente más tarde" in body["message"].lower()

    @pytest.mark.asyncio
    async def test_handler_de_dominio_generico_responde_400(
        self, test_app, fake_hasher
    ) -> None:
        """Una excepción AuthDomainError no clasificada da 400."""
        from auth.api.dependencies import get_auth_service
        from auth.domain.exceptions import AuthDomainError
        from auth.domain.repositories.i_user_repository import IUserRepository
        from auth.domain.services.auth_service import AuthService

        class DomainErrorRepo(IUserRepository):
            async def save(self, user):  # type: ignore[no-untyped-def]
                raise AuthDomainError("Error genérico de dominio")

            async def find_by_email(self, email):  # type: ignore[no-untyped-def]
                return None

            async def find_by_id(self, user_id):  # type: ignore[no-untyped-def]
                return None

            async def find_all(self):
                return []

            async def find_by_status(self, status):
                return []

            async def email_exists(self, email):  # type: ignore[no-untyped-def]
                return False

        async def override_with_domain_error() -> AuthService:
            return AuthService(DomainErrorRepo(), fake_hasher)

        test_app.dependency_overrides[get_auth_service] = override_with_domain_error

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "user@example.com",
                    "full_name": "Usuario",
                    "password": "MiP@ssw0rd!",
                },
            )

        assert response.status_code == 400
        body = response.json()
        assert body["error"] == "domain_error"
