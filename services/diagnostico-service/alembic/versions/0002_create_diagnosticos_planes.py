"""creacion tablas diagnosticos y planes_abono

Revision ID: 0002_create_diagnosticos_planes
Revises: 0001_create_cultivos_table
Create Date: 2026-05-12

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002_create_diagnosticos_planes"
down_revision: str | None = "0001_create_cultivos_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Tabla diagnosticos
    op.create_table(
        "diagnosticos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cultivo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("foto_url", sa.Text, nullable=False),
        sa.Column("confianza_global", sa.Float, nullable=False),
        sa.Column("estado_general", sa.String(30), nullable=False),
        sa.Column("es_imagen_valida", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("razon_invalidez", sa.Text, nullable=True),
        sa.Column("estado_fenologico", sa.String(100), nullable=True),
        sa.Column("deficiencias_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("patologias_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("descripcion_hallazgo", sa.Text, nullable=False, server_default=""),
        sa.Column("recomendacion_tecnica", sa.Text, nullable=False, server_default=""),
        sa.Column("recomendacion_natural", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema="diagnostico",
    )
    op.create_index("ix_diagnosticos_user_id", "diagnosticos", ["user_id"], schema="diagnostico")
    op.create_index("ix_diagnosticos_cultivo_id", "diagnosticos", ["cultivo_id"], schema="diagnostico")

    # Tabla planes_abono
    op.create_table(
        "planes_abono",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("diagnostico_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cultivo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aplicaciones_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("observaciones_generales", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema="diagnostico",
    )
    op.create_index("ix_planes_user_id", "planes_abono", ["user_id"], schema="diagnostico")

    # Tabla recordatorios
    op.create_table(
        "recordatorios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cultivo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("producto", sa.String(255), nullable=False),
        sa.Column("dosis", sa.String(100), nullable=False),
        sa.Column("fecha_programada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hora_programada", sa.String(5), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="PENDIENTE"),
        sa.Column("notas", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        schema="diagnostico",
    )
    op.create_index("ix_recordatorios_user_id", "recordatorios", ["user_id"], schema="diagnostico")
    op.create_index("ix_recordatorios_plan_id", "recordatorios", ["plan_id"], schema="diagnostico")


def downgrade() -> None:
    op.drop_index("ix_recordatorios_plan_id", table_name="recordatorios", schema="diagnostico")
    op.drop_index("ix_recordatorios_user_id", table_name="recordatorios", schema="diagnostico")
    op.drop_table("recordatorios", schema="diagnostico")
    op.drop_index("ix_planes_user_id", table_name="planes_abono", schema="diagnostico")
    op.drop_table("planes_abono", schema="diagnostico")
    op.drop_index("ix_diagnosticos_cultivo_id", table_name="diagnosticos", schema="diagnostico")
    op.drop_index("ix_diagnosticos_user_id", table_name="diagnosticos", schema="diagnostico")
    op.drop_table("diagnosticos", schema="diagnostico")
