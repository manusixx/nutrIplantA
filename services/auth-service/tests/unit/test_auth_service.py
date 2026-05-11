"""Tests unitarios del AuthService."""
import pytest

from auth.domain.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UserDeactivatedError,
    UserNotApprovedError,
)
from auth.domain.models.user import UserRole, UserStatus
from auth.domain.services.auth_service import AuthService


class TestAuthServiceRegister:
    """Comportamiento del registro de usuarios."""

    @pytest.mark.asyncio
    async def test_registra_usuario_nuevo_con_estado_pendiente(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)

        user = await service.register(
            email="nuevo@example.com",
            full_name="Usuario Nuevo",
            plain_password="MiP@ssw0rd!",
        )

        assert user.email == "nuevo@example.com"
        assert user.full_name == "Usuario Nuevo"
        assert user.status == UserStatus.PENDIENTE_APROBACION
        assert user.role is None
        assert user.password_hash != "MiP@ssw0rd!"  # debe estar hasheada
        assert in_memory_repo.count == 1

    @pytest.mark.asyncio
    async def test_normaliza_email_a_minusculas(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)

        user = await service.register(
            email="MiCorreo@Example.COM",
            full_name="Usuario",
            plain_password="MiP@ssw0rd!",
        )

        assert user.email == "micorreo@example.com"

    @pytest.mark.asyncio
    async def test_normaliza_full_name_quitando_espacios(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)

        user = await service.register(
            email="x@x.com",
            full_name="  Manuel Pastrana  ",
            plain_password="MiP@ssw0rd!",
        )

        assert user.full_name == "Manuel Pastrana"

    @pytest.mark.asyncio
    async def test_falla_si_email_ya_existe(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)
        await service.register("duplicado@x.com", "Uno", "MiP@ssw0rd!")

        with pytest.raises(EmailAlreadyRegisteredError):
            await service.register("duplicado@x.com", "Dos", "OtraP@ss!")

    @pytest.mark.asyncio
    async def test_falla_si_email_existe_con_diferente_capitalizacion(
        self, in_memory_repo, fake_hasher
    ) -> None:
        """La unicidad de email es case-insensitive."""
        service = AuthService(in_memory_repo, fake_hasher)
        await service.register("test@x.com", "Uno", "MiP@ssw0rd!")

        with pytest.raises(EmailAlreadyRegisteredError):
            await service.register("TEST@x.com", "Dos", "OtraP@ss!")


class TestAuthServiceAuthenticate:
    """Comportamiento del login."""

    @pytest.mark.asyncio
    async def test_falla_con_credenciales_invalidas_si_no_existe(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)

        with pytest.raises(InvalidCredentialsError):
            await service.authenticate("inexistente@x.com", "p@ssw0rd")

    @pytest.mark.asyncio
    async def test_falla_con_credenciales_invalidas_si_password_incorrecta(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)
        await service.register("user@x.com", "Usuario", "Correct@P4ss!")
        # Aprobar manualmente para llegar al check de password
        user = await in_memory_repo.find_by_email("user@x.com")
        assert user is not None
        user.approve(UserRole.AGRICULTOR)
        await in_memory_repo.save(user)

        with pytest.raises(InvalidCredentialsError):
            await service.authenticate("user@x.com", "Wr0ng@Pass!")

    @pytest.mark.asyncio
    async def test_falla_si_usuario_pendiente_aprobacion(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)
        await service.register("user@x.com", "Usuario", "MiP@ssw0rd!")
        # Sin aprobar

        with pytest.raises(UserNotApprovedError):
            await service.authenticate("user@x.com", "MiP@ssw0rd!")

    @pytest.mark.asyncio
    async def test_falla_si_usuario_desactivado(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)
        await service.register("user@x.com", "Usuario", "MiP@ssw0rd!")
        user = await in_memory_repo.find_by_email("user@x.com")
        assert user is not None
        user.approve(UserRole.AGRICULTOR)
        user.deactivate()
        await in_memory_repo.save(user)

        with pytest.raises(UserDeactivatedError):
            await service.authenticate("user@x.com", "MiP@ssw0rd!")

    @pytest.mark.asyncio
    async def test_autentica_correctamente_si_aprobado(
        self, in_memory_repo, fake_hasher
    ) -> None:
        service = AuthService(in_memory_repo, fake_hasher)
        await service.register("user@x.com", "Usuario", "MiP@ssw0rd!")
        user = await in_memory_repo.find_by_email("user@x.com")
        assert user is not None
        user.approve(UserRole.AGRICULTOR)
        await in_memory_repo.save(user)

        authenticated = await service.authenticate("user@x.com", "MiP@ssw0rd!")

        assert authenticated.email == "user@x.com"
        assert authenticated.role == UserRole.AGRICULTOR
        assert authenticated.can_login() is True
