"""DTOs para los endpoints del diagnostico-service."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from diagnostico.domain.models.cultivo import VariedadVid
from diagnostico.domain.models.diagnostico import EstadoGeneral, NivelConfianza
from diagnostico.domain.models.plan_abono import EstadoRecordatorio


# ============================================================
# Cultivos
# ============================================================
class CultivoCreateRequest(BaseModel):
    nombre_finca: str = Field(..., min_length=2, max_length=255)
    variedad: VariedadVid
    vereda: str = Field(default="", max_length=255)
    fila: str = Field(default="", max_length=100)
    subparcela: str = Field(default="", max_length=100)
    notas: str = Field(default="", max_length=1000)


class CultivoUpdateRequest(BaseModel):
    nombre_finca: str | None = Field(default=None, min_length=2, max_length=255)
    variedad: VariedadVid | None = None
    vereda: str | None = Field(default=None, max_length=255)
    fila: str | None = Field(default=None, max_length=100)
    subparcela: str | None = Field(default=None, max_length=100)
    notas: str | None = Field(default=None, max_length=1000)


class CultivoResponse(BaseModel):
    id: UUID
    user_id: UUID
    nombre_finca: str
    variedad: VariedadVid
    vereda: str
    fila: str
    subparcela: str
    notas: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Diagnósticos
# ============================================================
class DiagnosticoCreateRequest(BaseModel):
    cultivo_id: UUID
    foto_url: str = Field(..., min_length=5, description="URL de la imagen en MinIO")


class DeficienciaResponse(BaseModel):
    nutriente: str
    evidencia_visual: str
    confianza: NivelConfianza


class PatologiaResponse(BaseModel):
    tipo: str
    nombre: str
    evidencia_visual: str
    confianza: NivelConfianza
    urgencia: NivelConfianza


class DiagnosticoResponse(BaseModel):
    id: UUID
    cultivo_id: UUID
    user_id: UUID
    foto_url: str
    confianza_global: float
    estado_general: EstadoGeneral
    es_imagen_valida: bool
    razon_invalidez: str | None
    estado_fenologico: str | None
    deficiencias: list[DeficienciaResponse]
    patologias: list[PatologiaResponse]
    descripcion_hallazgo: str
    recomendacion_tecnica: str
    recomendacion_natural: str
    created_at: datetime


# ============================================================
# Planes de abono
# ============================================================
class PlanAbonoCreateRequest(BaseModel):
    diagnostico_id: UUID


class AplicacionResponse(BaseModel):
    producto: str
    dosis: str
    fecha_sugerida: datetime
    hora_sugerida: str
    observaciones: str


class PlanAbonoResponse(BaseModel):
    id: UUID
    diagnostico_id: UUID
    cultivo_id: UUID
    user_id: UUID
    aplicaciones: list[AplicacionResponse]
    observaciones_generales: str
    created_at: datetime


# ============================================================
# Recordatorios
# ============================================================
class RecordatorioResponse(BaseModel):
    id: UUID
    plan_id: UUID
    cultivo_id: UUID
    producto: str
    dosis: str
    fecha_programada: datetime
    hora_programada: str
    estado: EstadoRecordatorio
    notas: str
    created_at: datetime
    updated_at: datetime


class CompletarRecordatorioRequest(BaseModel):
    notas: str = Field(default="")
