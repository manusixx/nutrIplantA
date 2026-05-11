"""
Interfaz del repositorio de usuarios.

Esta interfaz vive en el dominio y NO debe importar nada de
infrastructure. Las implementaciones concretas (Postgres, InMemory)
viven en infrastructure/persistence.

Es una aplicación directa del patrón Repository y del principio de
Inversión de Dependencias.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from auth.domain.models.user import User


class IUserRepository(ABC):
    """Contrato para persistencia de usuarios."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Guardar un usuario nuevo o actualizar uno existente.

        Returns:
            User: el usuario persistido (con id generado si era nuevo).
        """
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """
        Buscar usuario por email (case-insensitive).

        Returns:
            User si existe, None si no.
        """
        ...

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None:
        """
        Buscar usuario por su UUID.

        Returns:
            User si existe, None si no.
        """
        ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Verificar si un email ya está registrado (case-insensitive)."""
        ...
