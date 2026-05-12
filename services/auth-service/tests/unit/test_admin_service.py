"""Tests unitarios del AdminService."""
from uuid import uuid4

import pytest

from auth.domain.exceptions import UserNotFoundError
from auth.domain.models.user import User, UserRole, UserStatus
from auth.domain.services.admin_service import AdminService
from auth.infrastructure.persistence.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def service(repo: InMemoryUserRepository) -> AdminService:
    return AdminService(repo)


def _make_user(
    status: UserStatus = UserStatus.PENDIENTE_APROBACION,
    role: UserRole | None = None,
) -> User:
    return User(
        email=f"user_{uuid4().hex[:6]}@test.com",
        full_name="Test User",
        password_hash="hashed",
        status=status,
        role=role,
    )


class TestAdminServiceAprobar:
    @pytest.mark.asyncio
    async def test_aprueba_usuario_pendiente_y_asigna_rol(
        self, service: AdminService, repo: InMemoryUserRepository
    ) -> None:
        user = _make_user()
        await repo.save(user)

        aprobado = await service.aprobar(user.id, UserRole.AGRICULTOR)

        assert aprobado.status == UserStatus.APROBADO
        assert aprobado.role == UserRole.AGRICULTOR

    @pytest.mark.asyncio
    async def test_falla_si_usuario_no_existe(self, service: AdminService) -> None:
        with pytest.raises(UserNotFoundError):
            await service.aprobar(uuid4(), UserRole.AGRICULTOR)

    @pytest.mark.asyncio
    async def test_falla_si_usuario_ya_aprobado(
        self, service: AdminService, repo: InMemoryUserRepository
    ) -> None:
        user = _make_user(status=UserStatus.APROBADO, role=UserRole.AGRICULTOR)
        await repo.save(user)

        with pytest.raises(ValueError, match="pendiente"):
            await service.aprobar(user.id, UserRole.INVESTIGADOR)


class TestAdminServiceRechazar:
    @pytest.mark.asyncio
    async def test_rechaza_usuario_pendiente(
        self, service: AdminService, repo: InMemoryUserRepository
    ) -> None:
        user = _make_user()
        await repo.save(user)

        rechazado = await service.rechazar(user.id)

        assert rechazado.status == UserStatus.RECHAZADO

    @pytest.mark.asyncio
    async def test_falla_si_usuario_ya_aprobado(
        self, service: AdminService, repo: InMemoryUserRepository
    ) -> None:
        user = _make_user(status=UserStatus.APROBADO, role=UserRole.AGRICULTOR)
        await repo.save(user)

        with pytest.raises(ValueError):
            await service.rechazar(user.id)


class TestAdminServiceDesactivar:
    @pytest.mark.asyncio
    async def test_desactiva_usuario_aprobado(
        self, service: AdminService, repo: InMemoryUserRepository
    ) -> None:
        user = _make_user(status=UserStatus.APROBADO, role=UserRole.AGRICULTOR)
        await repo.save(user)

        desactivado = await service.desactivar(user.id)

        assert desactivado.status == UserStatus.DESACTIVADO

    @pytest.mark.asyncio
    async def test_falla_si_usuario_no_existe(self, service: AdminService) -> None:
        with pytest.raises(UserNotFoundError):
            await service.desactivar(uuid4())


class TestAdminServiceListar:
    @pytest.mark.asyncio
    async def test_lista_pendientes(
        self, service: AdminService, repo: InMemoryUserRepository
    ) -> None:
        await repo.save(_make_user(status=UserStatus.PENDIENTE_APROBACION))
        await repo.save(_make_user(status=UserStatus.PENDIENTE_APROBACION))
        await repo.save(_make_user(status=UserStatus.APROBADO, role=UserRole.AGRICULTOR))

        pendientes = await service.listar_pendientes()

        assert len(pendientes) == 2
        assert all(u.status == UserStatus.PENDIENTE_APROBACION for u in pendientes)

    @pytest.mark.asyncio
    async def test_lista_todos(
        self, service: AdminService, repo: InMemoryUserRepository
    ) -> None:
        await repo.save(_make_user())
        await repo.save(_make_user())
        await repo.save(_make_user())

        todos = await service.listar_todos()

        assert len(todos) == 3
