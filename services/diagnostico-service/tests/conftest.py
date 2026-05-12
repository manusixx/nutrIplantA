"""Fixtures compartidas para tests del diagnostico-service."""
import pytest

from diagnostico.infrastructure.persistence.in_memory_cultivo_repository import (
    InMemoryCultivoRepository,
)


@pytest.fixture
def cultivo_repo() -> InMemoryCultivoRepository:
    return InMemoryCultivoRepository()
