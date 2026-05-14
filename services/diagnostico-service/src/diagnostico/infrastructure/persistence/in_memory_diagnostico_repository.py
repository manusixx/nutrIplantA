"""Repositorios en memoria para tests del diagnostico-service."""
from uuid import UUID

from diagnostico.domain.models.diagnostico import Diagnostico
from diagnostico.domain.models.plan_abono import EstadoRecordatorio, PlanAbono, Recordatorio
from diagnostico.domain.repositories.i_diagnostico_repository import (
    IDiagnosticoRepository,
    IPlanAbonoRepository,
    IRecordatorioRepository,
)


class InMemoryDiagnosticoRepository(IDiagnosticoRepository):
    def __init__(self) -> None:
        self._items: dict[UUID, Diagnostico] = {}

    async def save(self, d: Diagnostico) -> Diagnostico:
        self._items[d.id] = d
        return d

    async def find_by_id(self, did: UUID) -> Diagnostico | None:
        return self._items.get(did)

    async def find_by_user(
        self, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[Diagnostico]:
        items = [d for d in self._items.values() if d.user_id == user_id]
        items.sort(key=lambda d: d.created_at, reverse=True)
        return items[offset: offset + limit]

    async def find_by_cultivo(
        self, cultivo_id: UUID, user_id: UUID
    ) -> list[Diagnostico]:
        return [
            d for d in self._items.values()
            if d.cultivo_id == cultivo_id and d.user_id == user_id
        ]

    async def count_by_user(self, user_id: UUID) -> int:
        return sum(1 for d in self._items.values() if d.user_id == user_id)

    def clear(self) -> None:
        self._items.clear()


class InMemoryPlanAbonoRepository(IPlanAbonoRepository):
    def __init__(self) -> None:
        self._items: dict[UUID, PlanAbono] = {}

    async def save(self, plan: PlanAbono) -> PlanAbono:
        self._items[plan.id] = plan
        return plan

    async def find_by_diagnostico(self, did: UUID) -> PlanAbono | None:
        return next(
            (p for p in self._items.values() if p.diagnostico_id == did), None
        )

    async def find_by_user(self, user_id: UUID) -> list[PlanAbono]:
        return [p for p in self._items.values() if p.user_id == user_id]

    def clear(self) -> None:
        self._items.clear()


class InMemoryRecordatorioRepository(IRecordatorioRepository):
    def __init__(self) -> None:
        self._items: dict[UUID, Recordatorio] = {}

    async def save(self, rec: Recordatorio) -> Recordatorio:
        self._items[rec.id] = rec
        return rec

    async def find_by_id(self, rid: UUID) -> Recordatorio | None:
        return self._items.get(rid)

    async def find_by_user_pendientes(self, user_id: UUID) -> list[Recordatorio]:
        return [
            r for r in self._items.values()
            if r.user_id == user_id and r.estado == EstadoRecordatorio.PENDIENTE
        ]

    async def find_by_plan(self, plan_id: UUID) -> list[Recordatorio]:
        return [r for r in self._items.values() if r.plan_id == plan_id]

    def clear(self) -> None:
        self._items.clear()
