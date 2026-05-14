"""Interfaces de repositorios del diagnostico-service."""
from abc import ABC, abstractmethod
from uuid import UUID

from diagnostico.domain.models.diagnostico import Diagnostico
from diagnostico.domain.models.plan_abono import PlanAbono, Recordatorio


class IDiagnosticoRepository(ABC):
    """Contrato para persistencia de diagnósticos."""

    @abstractmethod
    async def save(self, diagnostico: Diagnostico) -> Diagnostico: ...

    @abstractmethod
    async def find_by_id(self, diagnostico_id: UUID) -> Diagnostico | None: ...

    @abstractmethod
    async def find_by_user(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Diagnostico]: ...

    @abstractmethod
    async def find_by_cultivo(
        self,
        cultivo_id: UUID,
        user_id: UUID,
    ) -> list[Diagnostico]: ...

    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int: ...


class IPlanAbonoRepository(ABC):
    """Contrato para persistencia de planes de abono."""

    @abstractmethod
    async def save(self, plan: PlanAbono) -> PlanAbono: ...

    @abstractmethod
    async def find_by_diagnostico(
        self, diagnostico_id: UUID
    ) -> PlanAbono | None: ...

    @abstractmethod
    async def find_by_user(self, user_id: UUID) -> list[PlanAbono]: ...


class IRecordatorioRepository(ABC):
    """Contrato para persistencia de recordatorios."""

    @abstractmethod
    async def save(self, recordatorio: Recordatorio) -> Recordatorio: ...

    @abstractmethod
    async def find_by_id(self, recordatorio_id: UUID) -> Recordatorio | None: ...

    @abstractmethod
    async def find_by_user_pendientes(
        self, user_id: UUID
    ) -> list[Recordatorio]: ...

    @abstractmethod
    async def find_by_plan(self, plan_id: UUID) -> list[Recordatorio]: ...
