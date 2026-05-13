"""Implementaciones PostgreSQL de IPlanAbonoRepository e IRecordatorioRepository."""
import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from diagnostico.domain.models.plan_abono import (
    AplicacionFertilizante,
    EstadoRecordatorio,
    PlanAbono,
    Recordatorio,
)
from diagnostico.domain.repositories.i_diagnostico_repository import (
    IPlanAbonoRepository,
    IRecordatorioRepository,
)
from diagnostico.infrastructure.persistence.models import PlanAbonoModel, RecordatorioModel


def _aplicaciones_to_json(aplicaciones: list[AplicacionFertilizante]) -> str:
    return json.dumps([
        {
            "producto": a.producto,
            "dosis": a.dosis,
            "fecha_sugerida": a.fecha_sugerida.isoformat(),
            "hora_sugerida": a.hora_sugerida,
            "observaciones": a.observaciones,
        }
        for a in aplicaciones
    ])


def _aplicaciones_from_json(data: str) -> list[AplicacionFertilizante]:
    items = json.loads(data)
    return [
        AplicacionFertilizante(
            producto=item["producto"],
            dosis=item["dosis"],
            fecha_sugerida=datetime.fromisoformat(item["fecha_sugerida"]),
            hora_sugerida=item["hora_sugerida"],
            observaciones=item.get("observaciones", ""),
        )
        for item in items
    ]


class PostgresPlanAbonoRepository(IPlanAbonoRepository):
    """Persistencia de planes de abono sobre PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, plan: PlanAbono) -> PlanAbono:
        existing = await self._session.get(PlanAbonoModel, plan.id)
        if existing is None:
            db = PlanAbonoModel(
                id=plan.id,
                diagnostico_id=plan.diagnostico_id,
                cultivo_id=plan.cultivo_id,
                user_id=plan.user_id,
                aplicaciones_json=_aplicaciones_to_json(plan.aplicaciones),
                observaciones_generales=plan.observaciones_generales,
                created_at=plan.created_at,
            )
            self._session.add(db)
            await self._session.commit()
        return plan

    async def find_by_diagnostico(self, did: UUID) -> PlanAbono | None:
        stmt = select(PlanAbonoModel).where(PlanAbonoModel.diagnostico_id == did)
        result = await self._session.execute(stmt)
        db = result.scalar_one_or_none()
        return self._to_domain(db) if db else None

    async def find_by_user(self, user_id: UUID) -> list[PlanAbono]:
        stmt = select(PlanAbonoModel).where(PlanAbonoModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    @staticmethod
    def _to_domain(db: PlanAbonoModel) -> PlanAbono:
        return PlanAbono(
            id=db.id,
            diagnostico_id=db.diagnostico_id,
            cultivo_id=db.cultivo_id,
            user_id=db.user_id,
            aplicaciones=_aplicaciones_from_json(db.aplicaciones_json),
            observaciones_generales=db.observaciones_generales,
            created_at=db.created_at,
        )


class PostgresRecordatorioRepository(IRecordatorioRepository):
    """Persistencia de recordatorios sobre PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, rec: Recordatorio) -> Recordatorio:
        existing = await self._session.get(RecordatorioModel, rec.id)
        if existing is None:
            db = RecordatorioModel(
                id=rec.id,
                plan_id=rec.plan_id,
                cultivo_id=rec.cultivo_id,
                user_id=rec.user_id,
                producto=rec.producto,
                dosis=rec.dosis,
                fecha_programada=rec.fecha_programada,
                hora_programada=rec.hora_programada,
                estado=rec.estado.value,
                notas=rec.notas,
                created_at=rec.created_at,
                updated_at=rec.updated_at,
            )
            self._session.add(db)
        else:
            existing.estado = rec.estado.value
            existing.notas = rec.notas
            existing.updated_at = rec.updated_at
        await self._session.commit()
        return rec

    async def find_by_id(self, rid: UUID) -> Recordatorio | None:
        db = await self._session.get(RecordatorioModel, rid)
        return self._to_domain(db) if db else None

    async def find_by_user_pendientes(self, user_id: UUID) -> list[Recordatorio]:
        stmt = select(RecordatorioModel).where(
            RecordatorioModel.user_id == user_id,
            RecordatorioModel.estado == EstadoRecordatorio.PENDIENTE.value,
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def find_by_plan(self, plan_id: UUID) -> list[Recordatorio]:
        stmt = select(RecordatorioModel).where(RecordatorioModel.plan_id == plan_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    @staticmethod
    def _to_domain(db: RecordatorioModel) -> Recordatorio:
        return Recordatorio(
            id=db.id,
            plan_id=db.plan_id,
            cultivo_id=db.cultivo_id,
            user_id=db.user_id,
            producto=db.producto,
            dosis=db.dosis,
            fecha_programada=db.fecha_programada,
            hora_programada=db.hora_programada,
            estado=EstadoRecordatorio(db.estado),
            notas=db.notas,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )
