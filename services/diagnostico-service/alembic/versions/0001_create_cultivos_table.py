"""creacion tabla cultivos

Revision ID: 0001_create_cultivos_table
Revises:
Create Date: 2026-05-09

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_create_cultivos_table"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear la tabla diagnostico.cultivos."""
    op.create_table(
        "cultivos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre_finca", sa.String(255), nullable=False),
        sa.Column("variedad", sa.String(100), nullable=False),
        sa.Column("vereda", sa.String(255), nullable=False, server_default=""),
        sa.Column("fila", sa.String(100), nullable=False, server_default=""),
        sa.Column("subparcela", sa.String(100), nullable=False, server_default=""),
        sa.Column("notas", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        schema="diagnostico",
    )
    op.create_index(
        "ix_cultivos_user_id",
        "cultivos",
        ["user_id"],
        schema="diagnostico",
    )


def downgrade() -> None:
    op.drop_index("ix_cultivos_user_id", table_name="cultivos", schema="diagnostico")
    op.drop_table("cultivos", schema="diagnostico")
