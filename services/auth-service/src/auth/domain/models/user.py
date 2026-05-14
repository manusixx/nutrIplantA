"""
Modelo de dominio: User.

Este modelo es puro: no depende de SQLAlchemy ni de FastAPI.
Representa un usuario del sistema con sus reglas de negocio invariantes.
"""
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class UserRole(StrEnum):
    """Roles del sistema según el JWT."""

    AGRICULTOR = "AGRICULTOR"
    INVESTIGADOR = "INVESTIGADOR"
    ADMIN = "ADMIN"


class UserStatus(StrEnum):
    """Estados del ciclo de vida de un usuario."""

    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    DESACTIVADO = "DESACTIVADO"


@dataclass
class User:
    """
    Entidad de dominio User.

    Reglas invariantes:
    - id es un UUID generado automáticamente.
    - email es único en el sistema (validado por el repositorio).
    - password_hash NUNCA se expone fuera del dominio.
    - status inicial es PENDIENTE_APROBACION.
    - role es null hasta que un admin lo asigne tras aprobar.
    """

    email: str
    full_name: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)
    role: UserRole | None = None
    status: UserStatus = UserStatus.PENDIENTE_APROBACION
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def can_login(self) -> bool:
        """Solo usuarios aprobados con rol asignado pueden autenticarse."""
        return self.status == UserStatus.APROBADO and self.role is not None

    def approve(self, role: UserRole) -> None:
        """Aprobar usuario asignándole un rol. Cambia status y timestamp."""
        if self.status != UserStatus.PENDIENTE_APROBACION:
            raise ValueError(
                f"Solo se pueden aprobar usuarios PENDIENTE_APROBACION, "
                f"este usuario está en estado {self.status.value}"
            )
        self.role = role
        self.status = UserStatus.APROBADO
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """Desactivar usuario. Preserva datos históricos."""
        self.status = UserStatus.DESACTIVADO
        self.updated_at = datetime.now(UTC)
