"""Implementación PostgreSQL del ICultivoRepository."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from diagnostico.domain.models.cultivo import Cultivo, VariedadVid
from diagnostico.domain.repositories.i_cultivo_repository import ICultivoRepository
from diagnostico.infrastructure.persistence.models import CultivoModel


class PostgresCultivoRepository(ICultivoRepository):
    """Persistencia de cultivos sobre PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, cultivo: Cultivo) -> Cultivo:
        existing = await self._session.get(CultivoModel, cultivo.id)
        if existing is None:
            db = CultivoModel(
                id=cultivo.id,
                user_id=cultivo.user_id,
                nombre_finca=cultivo.nombre_finca,
                variedad=cultivo.variedad.value,
                vereda=cultivo.vereda,
                fila=cultivo.fila,
                subparcela=cultivo.subparcela,
                notas=cultivo.notas,
                created_at=cultivo.created_at,
                updated_at=cultivo.updated_at,
            )
            self._session.add(db)
        else:
            existing.nombre_finca = cultivo.nombre_finca
            existing.variedad = cultivo.variedad.value
            existing.vereda = cultivo.vereda
            existing.fila = cultivo.fila
            existing.subparcela = cultivo.subparcela
            existing.notas = cultivo.notas
            existing.updated_at = cultivo.updated_at
        await self._session.commit()
        return cultivo

    async def find_by_id(self, cultivo_id: UUID) -> Cultivo | None:
        db = await self._session.get(CultivoModel, cultivo_id)
        return self._to_domain(db) if db else None

    async def find_by_user(self, user_id: UUID) -> list[Cultivo]:
        stmt = select(CultivoModel).where(CultivoModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def delete(self, cultivo_id: UUID) -> None:
        db = await self._session.get(CultivoModel, cultivo_id)
        if db:
            await self._session.delete(db)
            await self._session.commit()

    async def exists_for_user(self, cultivo_id: UUID, user_id: UUID) -> bool:
        db = await self._session.get(CultivoModel, cultivo_id)
        return db is not None and db.user_id == user_id

    @staticmethod
    def _to_domain(db: CultivoModel) -> Cultivo:
        return Cultivo(
            id=db.id,
            user_id=db.user_id,
            nombre_finca=db.nombre_finca,
            variedad=VariedadVid(db.variedad),
            vereda=db.vereda,
            fila=db.fila,
            subparcela=db.subparcela,
            notas=db.notas,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )
