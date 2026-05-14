"""Tests del módulo api.dependencies."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI, Request

from auth.api.dependencies import (
    get_auth_service,
    get_db_session,
    get_settings_dep,
    get_user_repository,
)
from auth.config import Settings
from auth.infrastructure.persistence.postgres_user_repository import (
    PostgresUserRepository,
)


def _make_request_with_container(container: MagicMock) -> Request:
    """Construir un Request fake con un container mockeado."""
    app = FastAPI()
    app.state.container = container
    # Request mínimo: scope con app
    scope = {
        "type": "http",
        "app": app,
    }
    return Request(scope=scope)


class TestGetSettingsDep:
    """get_settings_dep debe extraer Settings del container."""

    @pytest.mark.asyncio
    async def test_devuelve_settings_del_container(self) -> None:
        # Settings mock
        settings_mock = MagicMock(spec=Settings)

        # Container mock que devuelve el settings al llamar config()
        container = MagicMock()
        container.config.return_value = settings_mock

        request = _make_request_with_container(container)

        result = await get_settings_dep(request)

        assert result is settings_mock
        container.config.assert_called_once()


class TestGetDbSession:
    """get_db_session debe yieldear una sesión del session_factory."""

    @pytest.mark.asyncio
    async def test_yieldea_sesion_y_cierra_correctamente(self) -> None:
        # Mock de la sesión
        session_mock = AsyncMock()

        # Mock del factory que entra/sale como context manager
        factory_mock = MagicMock()
        factory_mock.return_value.__aenter__.return_value = session_mock
        factory_mock.return_value.__aexit__.return_value = None

        container = MagicMock()
        container.session_factory.return_value = factory_mock

        request = _make_request_with_container(container)

        # Consumir el generador
        async for session in get_db_session(request):
            assert session is session_mock

        factory_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_hace_rollback_si_hay_excepcion(self) -> None:
        """Si surge una excepción dentro del bloque async with, debe rollback."""
        session_mock = AsyncMock()

        # Context manager async correcto: __aenter__ devuelve la sesión,
        # __aexit__ recibe (exc_type, exc_val, exc_tb) y debe propagar la
        # excepción haciendo rollback en el __aexit__ real del código.
        class FakeAsyncContextManager:
            async def __aenter__(self):
                return session_mock

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                # No suprimir excepciones
                return False

        factory_mock = MagicMock(return_value=FakeAsyncContextManager())

        container = MagicMock()
        container.session_factory.return_value = factory_mock

        request = _make_request_with_container(container)

        # Consumir el async generator manualmente para poder
        # lanzar excepción al estilo de FastAPI
        agen = get_db_session(request)
        session = await agen.__anext__()
        assert session is session_mock

        # Simular que el endpoint lanzó excepción: athrow propaga al generator
        with pytest.raises(RuntimeError, match="error simulado"):
            await agen.athrow(RuntimeError("error simulado"))

        session_mock.rollback.assert_awaited_once()

class TestGetUserRepository:
    """get_user_repository debe construir el repositorio con la sesión."""

    @pytest.mark.asyncio
    async def test_construye_repositorio_con_sesion(self) -> None:
        session_mock = AsyncMock()

        repo = await get_user_repository(session=session_mock)

        assert isinstance(repo, PostgresUserRepository)


class TestGetAuthService:
    """get_auth_service debe construir AuthService con sus dependencias."""

    @pytest.mark.asyncio
    async def test_construye_auth_service_con_dependencias(self) -> None:
        # Hasher mock
        from auth.domain.repositories.i_password_hasher import IPasswordHasher

        class FakeHasher(IPasswordHasher):
            def hash(self, plain: str) -> str:
                return f"hashed:{plain}"

            def verify(self, plain: str, hashed: str) -> bool:
                return hashed == f"hashed:{plain}"

        hasher = FakeHasher()

        container = MagicMock()
        container.password_hasher.return_value = hasher

        request = _make_request_with_container(container)

        # User repository fake (in-memory)
        # user_repo = InMemoryUserRepository()
        # PostgresUserRepository tiene una interfaz compatible, pero
        # get_auth_service espera específicamente PostgresUserRepository
        # como tipo declarado. Le pasamos uno mock.
        postgres_repo_mock = MagicMock(spec=PostgresUserRepository)

        service = await get_auth_service(request=request, user_repository=postgres_repo_mock)

        # Verificar que el servicio se construyó
        assert service is not None
        assert service._hasher is hasher
        assert service._user_repo is postgres_repo_mock
