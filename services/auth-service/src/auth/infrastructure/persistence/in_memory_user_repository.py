"""
Implementación InMemory del IUserRepository.

Útil para tests unitarios: no requiere PostgreSQL ni docker.
Los datos se almacenan en un dict y se pierden al destruir la instancia.
"""
from uuid import UUID

from auth.domain.models.user import User, UserStatus
from auth.domain.repositories.i_user_repository import IUserRepository


class InMemoryUserRepository(IUserRepository):
    """Repositorio en memoria. Solo para tests."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def save(self, user: User) -> User:
        self._users[user.id] = user
        return user

    async def find_by_email(self, email: str) -> User | None:
        normalized = email.lower()
        for user in self._users.values():
            if user.email.lower() == normalized:
                return user
        return None

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def email_exists(self, email: str) -> bool:
        return await self.find_by_email(email) is not None

    # ----- Helpers solo para tests -----
    def clear(self) -> None:
        """Limpiar todos los datos (útil entre tests)."""
        self._users.clear()

    @property
    def count(self) -> int:
        """Número de usuarios almacenados."""
        return len(self._users)

    async def find_by_status(self, status: UserStatus) -> list[User]:
        return [u for u in self._users.values() if u.status == status]

    async def find_all(self) -> list[User]:
        return list(self._users.values())

