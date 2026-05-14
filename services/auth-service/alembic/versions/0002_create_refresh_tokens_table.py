"""creacion tabla refresh_tokens

Revision ID: 0002_create_refresh_tokens_table
Revises: 0001_create_users_table
Create Date: 2026-05-09

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_create_refresh_tokens_table"
down_revision: str | None = "0001_create_users_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear la tabla auth.refresh_tokens."""
    op.create_table(
        "refresh_tokens",
        sa.Column("jti", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("auth.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("parent_jti", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema="auth",
    )
    op.create_index(
        "ix_refresh_tokens_user_id",
        "refresh_tokens",
        ["user_id"],
        schema="auth",
    )
    op.create_index(
        "ix_refresh_tokens_revoked_at",
        "refresh_tokens",
        ["revoked_at"],
        schema="auth",
    )


def downgrade() -> None:
    """Eliminar la tabla auth.refresh_tokens."""
    op.drop_index("ix_refresh_tokens_revoked_at", table_name="refresh_tokens", schema="auth")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens", schema="auth")
    op.drop_table("refresh_tokens", schema="auth")
