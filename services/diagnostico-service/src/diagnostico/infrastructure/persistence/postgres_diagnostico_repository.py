"""Implementación PostgreSQL del IDiagnosticoRepository."""
import json
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from diagnostico.domain.models.diagnostico import (
    Diagnostico,
    DeficienciaNutricional,
    EstadoGeneral,
    NivelConfianza,
    PatologiaDetectada,
)
from diagnostico.domain.repositories.i_diagnostico_repository import IDiagnosticoRepository
from diagnostico.infrastructure.persistence.models import DiagnosticoModel


def _deficiencias_to_json(deficiencias: list[DeficienciaNutricional]) -> str:
    return json.dumps([
        {
            "nutriente": d.nutriente,
            "evidencia_visual": d.evidencia_visual,
            "confianza": d.confianza.value,
        }
        for d in deficiencias
    ])


def _patologias_to_json(patologias: list[PatologiaDetectada]) -> str:
    return json.dumps([
        {
            "tipo": p.tipo,
            "nombre": p.nombre,
            "evidencia_visual": p.evidencia_visual,
            "confianza": p.confianza.value,
            "urgencia": p.urgencia.value,
        }
        for p in patologias
    ])


def _deficiencias_from_json(data: str) -> list[DeficienciaNutricional]:
    items = json.loads(data)
    return [
        DeficienciaNutricional(
            nutriente=item["nutriente"],
            evidencia_visual=item["evidencia_visual"],
            confianza=NivelConfianza(item["confianza"]),
        )
        for item in items
    ]


def _patologias_from_json(data: str) -> list[PatologiaDetectada]:
    items = json.loads(data)
    return [
        PatologiaDetectada(
            tipo=item["tipo"],
            nombre=item["nombre"],
            evidencia_visual=item["evidencia_visual"],
            confianza=NivelConfianza(item["confianza"]),
            urgencia=NivelConfianza(item["urgencia"]),
        )
        for item in items
    ]


class PostgresDiagnosticoRepository(IDiagnosticoRepository):
    """Persistencia de diagnósticos sobre PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, d: Diagnostico) -> Diagnostico:
        existing = await self._session.get(DiagnosticoModel, d.id)
        if existing is None:
            db = DiagnosticoModel(
                id=d.id,
                cultivo_id=d.cultivo_id,
                user_id=d.user_id,
                foto_url=d.foto_url,
                confianza_global=d.confianza_global,
                estado_general=d.estado_general.value,
                es_imagen_valida=d.es_imagen_valida,
                razon_invalidez=d.razon_invalidez,
                estado_fenologico=d.estado_fenologico,
                deficiencias_json=_deficiencias_to_json(d.deficiencias),
                patologias_json=_patologias_to_json(d.patologias),
                descripcion_hallazgo=d.descripcion_hallazgo,
                recomendacion_tecnica=d.recomendacion_tecnica,
                recomendacion_natural=d.recomendacion_natural,
                created_at=d.created_at,
            )
            self._session.add(db)
            await self._session.commit()
        return d

    async def find_by_id(self, did: UUID) -> Diagnostico | None:
        db = await self._session.get(DiagnosticoModel, did)
        return self._to_domain(db) if db else None

    async def find_by_user(
        self, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[Diagnostico]:
        stmt = (
            select(DiagnosticoModel)
            .where(DiagnosticoModel.user_id == user_id)
            .order_by(DiagnosticoModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def find_by_cultivo(
        self, cultivo_id: UUID, user_id: UUID
    ) -> list[Diagnostico]:
        stmt = (
            select(DiagnosticoModel)
            .where(
                DiagnosticoModel.cultivo_id == cultivo_id,
                DiagnosticoModel.user_id == user_id,
            )
            .order_by(DiagnosticoModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def count_by_user(self, user_id: UUID) -> int:
        stmt = select(func.count()).where(DiagnosticoModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    def _to_domain(db: DiagnosticoModel) -> Diagnostico:
        return Diagnostico(
            id=db.id,
            cultivo_id=db.cultivo_id,
            user_id=db.user_id,
            foto_url=db.foto_url,
            confianza_global=db.confianza_global,
            estado_general=EstadoGeneral(db.estado_general),
            es_imagen_valida=db.es_imagen_valida,
            razon_invalidez=db.razon_invalidez,
            estado_fenologico=db.estado_fenologico,
            deficiencias=_deficiencias_from_json(db.deficiencias_json),
            patologias=_patologias_from_json(db.patologias_json),
            descripcion_hallazgo=db.descripcion_hallazgo,
            recomendacion_tecnica=db.recomendacion_tecnica,
            recomendacion_natural=db.recomendacion_natural,
            created_at=db.created_at,
        )
