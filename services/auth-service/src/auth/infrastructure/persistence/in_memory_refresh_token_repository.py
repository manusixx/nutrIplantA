"""InMemory implementation del IRefreshTokenRepository. Solo para tests."""
from uuid import UUID

from auth.domain.models.refresh_token import RefreshToken
from auth.domain.repositories.i_refresh_token_repository import IRefreshTokenRepository


class InMemoryRefreshTokenRepository(IRefreshTokenRepository):
    """Repositorio en memoria. Solo para tests."""

    def __init__(self) -> None:
        self._tokens: dict[UUID, RefreshToken] = {}

    async def save(self, token: RefreshToken) -> RefreshToken:
        self._tokens[token.jti] = token
        return token

    async def find_by_jti(self, jti: UUID) -> RefreshToken | None:
        return self._tokens.get(jti)

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        for token in self._tokens.values():
            if token.user_id == user_id and not token.is_revoked:
                token.revoke()

    async def find_active_by_user(self, user_id: UUID) -> list[RefreshToken]:
        return [
            t for t in self._tokens.values()
            if t.user_id == user_id and t.is_valid
        ]

    def clear(self) -> None:
        self._tokens.clear()

    @property
    def count(self) -> int:
        return len(self._tokens)
