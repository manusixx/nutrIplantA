"""Modelo SQLAlchemy para auth.refresh_tokens."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PgUUID  # noqa: N811
from sqlalchemy.orm import Mapped, mapped_column

from auth.infrastructure.persistence.user_model import Base


class RefreshTokenModel(Base):
    """Tabla auth.refresh_tokens."""

    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "auth"}

    jti: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_jti: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
