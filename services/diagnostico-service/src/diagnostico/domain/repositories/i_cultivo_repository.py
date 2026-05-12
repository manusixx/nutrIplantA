"""Interfaz del repositorio de cultivos."""
from abc import ABC, abstractmethod
from uuid import UUID

from diagnostico.domain.models.cultivo import Cultivo


class ICultivoRepository(ABC):
    """Contrato para persistencia de cultivos."""

    @abstractmethod
    async def save(self, cultivo: Cultivo) -> Cultivo:
        """Guardar o actualizar un cultivo."""
        ...

    @abstractmethod
    async def find_by_id(self, cultivo_id: UUID) -> Cultivo | None:
        """Buscar por ID."""
        ...

    @abstractmethod
    async def find_by_user(self, user_id: UUID) -> list[Cultivo]:
        """Listar todos los cultivos de un usuario."""
        ...

    @abstractmethod
    async def delete(self, cultivo_id: UUID) -> None:
        """Eliminar un cultivo por ID."""
        ...

    @abstractmethod
    async def exists_for_user(self, cultivo_id: UUID, user_id: UUID) -> bool:
        """Verificar que el cultivo existe y pertenece al usuario."""
        ...
