"""Implementación PostgreSQL del IRefreshTokenRepository."""
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.models.refresh_token import RefreshToken
from auth.domain.repositories.i_refresh_token_repository import (
    IRefreshTokenRepository,
)
from auth.infrastructure.persistence.refresh_token_model import RefreshTokenModel


class PostgresRefreshTokenRepository(IRefreshTokenRepository):
    """Persistencia de refresh tokens sobre PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, token: RefreshToken) -> RefreshToken:
        """Insertar o actualizar un refresh token."""
        existing = await self._session.get(RefreshTokenModel, token.jti)
        if existing is None:
            db_token = RefreshTokenModel(
                jti=token.jti,
                user_id=token.user_id,
                parent_jti=token.parent_jti,
                expires_at=token.expires_at,
                revoked_at=token.revoked_at,
                created_at=token.created_at,
            )
            self._session.add(db_token)
        else:
            existing.revoked_at = token.revoked_at
        await self._session.commit()
        return token

    async def find_by_jti(self, jti: UUID) -> RefreshToken | None:
        """Buscar por jti."""
        db_token = await self._session.get(RefreshTokenModel, jti)
        return self._to_domain(db_token) if db_token else None

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        """Revocar todos los tokens activos del usuario."""
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def find_active_by_user(self, user_id: UUID) -> list[RefreshToken]:
        """Listar tokens activos del usuario."""
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.user_id == user_id,
            RefreshTokenModel.revoked_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    @staticmethod
    def _to_domain(db: RefreshTokenModel) -> RefreshToken:
        """Convertir modelo SQLAlchemy a entidad de dominio."""
        return RefreshToken(
            jti=db.jti,
            user_id=db.user_id,
            parent_jti=db.parent_jti,
            expires_at=db.expires_at,
            revoked_at=db.revoked_at,
            created_at=db.created_at,
        )
