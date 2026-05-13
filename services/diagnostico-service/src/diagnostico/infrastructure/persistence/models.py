"""
Modelos SQLAlchemy para el diagnostico-service.

Mapean las entidades de dominio a tablas en el esquema 'diagnostico'.
No deben ser importados por el dominio — solo por infrastructure.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DiagnosticoBase(DeclarativeBase):
    """Base declarativa para todos los modelos del diagnostico-service."""
    pass


class CultivoModel(DiagnosticoBase):
    """Tabla diagnostico.cultivos."""

    __tablename__ = "cultivos"
    __table_args__ = {"schema": "diagnostico"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    nombre_finca: Mapped[str] = mapped_column(String(255), nullable=False)
    variedad: Mapped[str] = mapped_column(String(100), nullable=False)
    vereda: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    fila: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    subparcela: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    notas: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DiagnosticoModel(DiagnosticoBase):
    """Tabla diagnostico.diagnosticos."""

    __tablename__ = "diagnosticos"
    __table_args__ = {"schema": "diagnostico"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    cultivo_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    foto_url: Mapped[str] = mapped_column(Text, nullable=False)
    confianza_global: Mapped[float] = mapped_column(Float, nullable=False)
    estado_general: Mapped[str] = mapped_column(String(30), nullable=False)
    es_imagen_valida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    razon_invalidez: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado_fenologico: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deficiencias_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    patologias_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    descripcion_hallazgo: Mapped[str] = mapped_column(Text, nullable=False, default="")
    recomendacion_tecnica: Mapped[str] = mapped_column(Text, nullable=False, default="")
    recomendacion_natural: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PlanAbonoModel(DiagnosticoBase):
    """Tabla diagnostico.planes_abono."""

    __tablename__ = "planes_abono"
    __table_args__ = {"schema": "diagnostico"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    diagnostico_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    cultivo_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    aplicaciones_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    observaciones_generales: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RecordatorioModel(DiagnosticoBase):
    """Tabla diagnostico.recordatorios."""

    __tablename__ = "recordatorios"
    __table_args__ = {"schema": "diagnostico"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    plan_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    cultivo_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    producto: Mapped[str] = mapped_column(String(255), nullable=False)
    dosis: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_programada: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hora_programada: Mapped[str] = mapped_column(String(5), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    notas: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
