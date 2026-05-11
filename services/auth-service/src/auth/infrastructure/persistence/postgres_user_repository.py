"""
Implementación del IUserRepository sobre PostgreSQL con SQLAlchemy 2.0
async. Convierte entre modelo de dominio (User) y modelo SQLAlchemy
(UserModel).
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.models.user import User, UserRole, UserStatus
from auth.domain.repositories.i_user_repository import IUserRepository
from auth.infrastructure.persistence.user_model import UserModel


class PostgresUserRepository(IUserRepository):
    """Persistencia de usuarios sobre PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> User:
        """Insertar o actualizar un usuario en la BD."""
        # Buscar si ya existe
        existing = await self._session.get(UserModel, user.id)

        if existing is None:
            # Nuevo usuario
            db_user = self._to_db_model(user)
            self._session.add(db_user)
        else:
            # Actualizar existente
            existing.email = user.email
            existing.full_name = user.full_name
            existing.password_hash = user.password_hash
            existing.role = user.role.value if user.role else None
            existing.status = user.status.value
            existing.updated_at = user.updated_at

        await self._session.commit()
        return user

    async def find_by_email(self, email: str) -> User | None:
        """Buscar por email (case-insensitive)."""
        stmt = select(UserModel).where(
            func.lower(UserModel.email) == email.lower()
        )
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return self._to_domain(db_user) if db_user else None

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Buscar por UUID."""
        db_user = await self._session.get(UserModel, user_id)
        return self._to_domain(db_user) if db_user else None

    async def email_exists(self, email: str) -> bool:
        """Verificar existencia de email."""
        stmt = select(func.count()).select_from(UserModel).where(
            func.lower(UserModel.email) == email.lower()
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0

    @staticmethod
    def _to_domain(db_user: UserModel) -> User:
        """Convertir modelo SQLAlchemy a entidad de dominio."""
        return User(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            password_hash=db_user.password_hash,
            role=UserRole(db_user.role) if db_user.role else None,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )

    @staticmethod
    def _to_db_model(user: User) -> UserModel:
        """Convertir entidad de dominio a modelo SQLAlchemy."""
        return UserModel(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            password_hash=user.password_hash,
            role=user.role.value if user.role else None,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
