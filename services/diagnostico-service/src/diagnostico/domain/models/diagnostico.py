"""
Modelo de dominio: Diagnostico.

Representa el resultado de analizar una foto de hoja de vid.
Contiene deficiencias detectadas, patologías y nivel de confianza.
"""
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class NivelConfianza(str, Enum):
    """Nivel de confianza del análisis de visión."""

    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class EstadoGeneral(str, Enum):
    """Estado general de la planta según el diagnóstico."""

    SALUDABLE = "SALUDABLE"
    REQUIERE_ATENCION = "REQUIERE_ATENCION"
    CRITICO = "CRITICO"


@dataclass
class DeficienciaNutricional:
    """Deficiencia nutricional detectada en la hoja."""

    nutriente: str  # N, P, K, Mg, Fe, Mn, B, Zn, Ca
    evidencia_visual: str
    confianza: NivelConfianza


@dataclass
class PatologiaDetectada:
    """Patología detectada en la hoja."""

    tipo: str  # hongo, insecto, bacteria, viral, dano_mecanico
    nombre: str
    evidencia_visual: str
    confianza: NivelConfianza
    urgencia: NivelConfianza


@dataclass
class Diagnostico:
    """
    Entidad de dominio Diagnostico.

    Reglas invariantes:
    - Pertenece a un cultivo y a un usuario.
    - La foto_url apunta al archivo en MinIO.
    - Las deficiencias y patologías pueden estar vacías si la planta está sana.
    """

    cultivo_id: UUID
    user_id: UUID
    foto_url: str
    confianza_global: float  # 0.0 a 1.0
    estado_general: EstadoGeneral
    id: UUID = field(default_factory=uuid4)
    es_imagen_valida: bool = True
    razon_invalidez: str | None = None
    estado_fenologico: str | None = None
    deficiencias: list[DeficienciaNutricional] = field(default_factory=list)
    patologias: list[PatologiaDetectada] = field(default_factory=list)
    descripcion_hallazgo: str = ""
    recomendacion_tecnica: str = ""
    recomendacion_natural: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def tiene_deficiencias_criticas(self) -> bool:
        """Tiene al menos una deficiencia con confianza alta o media."""
        return any(
            d.confianza in (NivelConfianza.ALTA, NivelConfianza.MEDIA)
            for d in self.deficiencias
        )

    @property
    def tiene_patologias_urgentes(self) -> bool:
        """Tiene al menos una patología con urgencia alta."""
        return any(p.urgencia == NivelConfianza.ALTA for p in self.patologias)
