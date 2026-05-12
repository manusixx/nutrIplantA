"""
Interfaz del repositorio de refresh tokens.

Vive en dominio. Las implementaciones concretas en infrastructure.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from auth.domain.models.refresh_token import RefreshToken


class IRefreshTokenRepository(ABC):
    """Contrato para persistencia de refresh tokens."""

    @abstractmethod
    async def save(self, token: RefreshToken) -> RefreshToken:
        """Guardar o actualizar un refresh token."""
        ...

    @abstractmethod
    async def find_by_jti(self, jti: UUID) -> RefreshToken | None:
        """Buscar por identificador único del token."""
        ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> None:
        """
        Revocar todos los tokens activos de un usuario.
        Usado cuando se detecta reuso de token (posible robo).
        """
        ...

    @abstractmethod
    async def find_active_by_user(self, user_id: UUID) -> list[RefreshToken]:
        """Listar todos los tokens activos de un usuario."""
        ...
