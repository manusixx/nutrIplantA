"""Configuración de fixtures compartidas entre tests."""
import pytest

from auth.domain.repositories.i_password_hasher import IPasswordHasher
from auth.infrastructure.persistence.in_memory_user_repository import (
    InMemoryUserRepository,
)


class FakePasswordHasher(IPasswordHasher):
    """Hasher fake que solo añade prefijo. Para tests rápidos."""

    PREFIX = "fake-hashed:"

    def hash(self, plain_password: str) -> str:
        return f"{self.PREFIX}{plain_password}"

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return password_hash == f"{self.PREFIX}{plain_password}"


@pytest.fixture
def in_memory_repo() -> InMemoryUserRepository:
    """Repositorio en memoria limpio por test."""
    return InMemoryUserRepository()


@pytest.fixture
def fake_hasher() -> FakePasswordHasher:
    """Hasher fake para tests rápidos (sin Argon2)."""
    return FakePasswordHasher()
