"""InMemory implementation del ICultivoRepository. Solo para tests."""
from uuid import UUID

from diagnostico.domain.models.cultivo import Cultivo
from diagnostico.domain.repositories.i_cultivo_repository import ICultivoRepository


class InMemoryCultivoRepository(ICultivoRepository):
    """Repositorio en memoria. Solo para tests."""

    def __init__(self) -> None:
        self._cultivos: dict[UUID, Cultivo] = {}

    async def save(self, cultivo: Cultivo) -> Cultivo:
        self._cultivos[cultivo.id] = cultivo
        return cultivo

    async def find_by_id(self, cultivo_id: UUID) -> Cultivo | None:
        return self._cultivos.get(cultivo_id)

    async def find_by_user(self, user_id: UUID) -> list[Cultivo]:
        return [c for c in self._cultivos.values() if c.user_id == user_id]

    async def delete(self, cultivo_id: UUID) -> None:
        self._cultivos.pop(cultivo_id, None)

    async def exists_for_user(self, cultivo_id: UUID, user_id: UUID) -> bool:
        cultivo = self._cultivos.get(cultivo_id)
        return cultivo is not None and cultivo.user_id == user_id

    def clear(self) -> None:
        self._cultivos.clear()

    @property
    def count(self) -> int:
        return len(self._cultivos)
