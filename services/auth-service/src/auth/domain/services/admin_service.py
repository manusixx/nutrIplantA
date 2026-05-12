"""
Servicio de dominio: gestión administrativa de usuarios.

Sprint 7 — HU-18, HU-19, HU-20.
Solo accesible por usuarios con rol ADMIN.
"""
from uuid import UUID

from auth.domain.exceptions import UserNotFoundError
from auth.domain.models.user import User, UserRole, UserStatus
from auth.domain.repositories.i_user_repository import IUserRepository


class AdminService:
    """Caso de uso: aprobación y gestión de usuarios por administradores."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._repo = user_repository

    async def listar_pendientes(self) -> list[User]:
        """Listar usuarios en estado PENDIENTE_APROBACION."""
        return await self._repo.find_by_status(UserStatus.PENDIENTE_APROBACION)

    async def listar_todos(self) -> list[User]:
        """Listar todos los usuarios del sistema."""
        return await self._repo.find_all()

    async def aprobar(self, user_id: UUID, rol: UserRole) -> User:
        """
        Aprobar un usuario asignándole un rol.

        Raises:
            UserNotFoundError: si el usuario no existe.
            ValueError: si el usuario no está en estado PENDIENTE_APROBACION.
        """
        user = await self._repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))

        if user.status != UserStatus.PENDIENTE_APROBACION:
            raise ValueError(
                f"El usuario no está pendiente de aprobación. "
                f"Estado actual: {user.status.value}"
            )

        user.approve(rol)
        return await self._repo.save(user)

    async def rechazar(self, user_id: UUID) -> User:
        """
        Rechazar un usuario.

        Raises:
            UserNotFoundError: si el usuario no existe.
        """
        user = await self._repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))

        if user.status != UserStatus.PENDIENTE_APROBACION:
            raise ValueError(
                f"Solo se pueden rechazar usuarios pendientes. "
                f"Estado actual: {user.status.value}"
            )

        user.status = UserStatus.RECHAZADO
        return await self._repo.save(user)

    async def desactivar(self, user_id: UUID) -> User:
        """
        Desactivar un usuario aprobado.

        Raises:
            UserNotFoundError: si el usuario no existe.
        """
        user = await self._repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))

        user.deactivate()
        return await self._repo.save(user)

    async def reactivar(self, user_id: UUID, rol: UserRole) -> User:
        """Reactivar un usuario desactivado asignándole un rol."""
        user = await self._repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))

        if user.status != UserStatus.DESACTIVADO:
            raise ValueError(
                f"Solo se pueden reactivar usuarios desactivados. "
                f"Estado actual: {user.status.value}"
            )

        user.status = UserStatus.APROBADO
        user.role = rol
        return await self._repo.save(user)
