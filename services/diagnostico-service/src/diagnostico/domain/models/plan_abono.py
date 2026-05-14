"""Modelo de dominio: PlanAbono y Recordatorio."""
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class EstadoRecordatorio(str, Enum):
    PENDIENTE = "PENDIENTE"
    COMPLETADO = "COMPLETADO"
    OMITIDO = "OMITIDO"


@dataclass
class AplicacionFertilizante:
    """Una aplicación específica dentro del plan de abono."""

    producto: str
    dosis: str
    fecha_sugerida: datetime
    hora_sugerida: str  # HH:MM, entre 05:00 y 09:00
    observaciones: str = ""


@dataclass
class PlanAbono:
    """
    Plan de abono generado a partir de un diagnóstico.

    Reglas invariantes:
    - Vinculado a un diagnóstico específico.
    - No se genera si la planta está enferma o en post-trasplante.
    - No mezcla dos fertilizantes el mismo día.
    - Solo recomienda aplicaciones entre 05:00 y 09:00.
    """

    diagnostico_id: UUID
    cultivo_id: UUID
    user_id: UUID
    aplicaciones: list[AplicacionFertilizante]
    id: UUID = field(default_factory=uuid4)
    observaciones_generales: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Recordatorio:
    """Recordatorio de aplicación de fertilizante."""

    plan_id: UUID
    cultivo_id: UUID
    user_id: UUID
    producto: str
    dosis: str
    fecha_programada: datetime
    hora_programada: str
    id: UUID = field(default_factory=uuid4)
    estado: EstadoRecordatorio = EstadoRecordatorio.PENDIENTE
    notas: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def marcar_completado(self, notas: str = "") -> None:
        self.estado = EstadoRecordatorio.COMPLETADO
        self.notas = notas
        self.updated_at = datetime.now(UTC)

    def omitir(self, notas: str = "") -> None:
        self.estado = EstadoRecordatorio.OMITIDO
        self.notas = notas
        self.updated_at = datetime.now(UTC)
