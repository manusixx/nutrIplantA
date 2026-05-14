"""
Interfaz del repositorio de usuarios.

Actualizada en Sprint 7 con métodos para gestión admin.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from auth.domain.models.user import User, UserStatus


class IUserRepository(ABC):
    """Contrato para persistencia de usuarios."""

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool: ...

    # Métodos Sprint 7
    @abstractmethod
    async def find_by_status(self, status: UserStatus) -> list[User]: ...

    @abstractmethod
    async def find_all(self) -> list[User]: ...
