"""
Modelo de dominio: RefreshToken.

Representa un refresh token emitido al usuario. Vive en dominio
porque contiene reglas de negocio (rotación, expiración, revocación).
"""
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4


@dataclass
class RefreshToken:
    """
    Entidad de dominio RefreshToken.

    Reglas invariantes:
    - Cada refresh token tiene un jti único.
    - Un token usado (rotado) genera un token hijo.
    - Un token revocado no puede usarse ni generar hijos.
    - La detección de reuso de token ya rotado indica posible robo.
    """

    user_id: UUID
    expires_at: datetime
    jti: UUID = field(default_factory=uuid4)
    parent_jti: UUID | None = None
    revoked_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls, user_id: UUID, expire_days: int = 7) -> "RefreshToken":
        """Crear un nuevo refresh token con expiración estándar."""
        return cls(
            user_id=user_id,
            expires_at=datetime.now(UTC) + timedelta(days=expire_days),
        )

    @property
    def is_expired(self) -> bool:
        """Verificar si el token expiró."""
        return datetime.now(UTC) >= self.expires_at

    @property
    def is_revoked(self) -> bool:
        """Verificar si el token fue revocado."""
        return self.revoked_at is not None

    @property
    def is_valid(self) -> bool:
        """Un token es válido si no expiró y no fue revocado."""
        return not self.is_expired and not self.is_revoked

    def revoke(self) -> None:
        """Revocar el token. Idempotente: revocar dos veces no falla."""
        if self.revoked_at is None:
            self.revoked_at = datetime.now(UTC)

    def rotate(self, expire_days: int = 7) -> "RefreshToken":
        """
        Rotar el token: revoca este y crea uno nuevo hijo.
        El hijo guarda referencia al padre para detectar reuso.
        """
        self.revoke()
        return RefreshToken(
            user_id=self.user_id,
            expires_at=datetime.now(UTC) + timedelta(days=expire_days),
            parent_jti=self.jti,
        )
