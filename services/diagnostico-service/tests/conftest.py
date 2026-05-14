"""Fixtures compartidas para tests del diagnostico-service."""
import pytest

from diagnostico.infrastructure.persistence.in_memory_cultivo_repository import (
    InMemoryCultivoRepository,
)
from diagnostico.infrastructure.persistence.in_memory_diagnostico_repository import (
    InMemoryDiagnosticoRepository,
    InMemoryPlanAbonoRepository,
    InMemoryRecordatorioRepository,
)


@pytest.fixture
def cultivo_repo() -> InMemoryCultivoRepository:
    return InMemoryCultivoRepository()


@pytest.fixture
def diagnostico_repo() -> InMemoryDiagnosticoRepository:
    return InMemoryDiagnosticoRepository()


@pytest.fixture
def plan_repo() -> InMemoryPlanAbonoRepository:
    return InMemoryPlanAbonoRepository()


@pytest.fixture
def rec_repo() -> InMemoryRecordatorioRepository:
    return InMemoryRecordatorioRepository()
