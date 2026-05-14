"""
Interfaz del proveedor de visión por computador.

Implementa el patrón Strategy (ADR-03). El dominio depende de
esta interfaz, no de ninguna implementación concreta.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from diagnostico.domain.models.diagnostico import (
    DeficienciaNutricional,
    EstadoGeneral,
    PatologiaDetectada,
)


@dataclass
class VisionResult:
    """Resultado estructurado del análisis de visión."""

    es_imagen_valida: bool
    razon_invalidez: str | None
    confianza_global: float
    estado_general: EstadoGeneral
    estado_fenologico: str | None
    deficiencias: list[DeficienciaNutricional]
    patologias: list[PatologiaDetectada]
    descripcion_hallazgo: str
    recomendacion_tecnica: str


class IVisionProvider(ABC):
    """Contrato para proveedores de análisis visual de hojas."""

    @abstractmethod
    async def analyze(self, image_url: str) -> VisionResult:
        """
        Analizar una imagen de hoja y retornar el resultado estructurado.

        Args:
            image_url: URL de la imagen en MinIO.

        Returns:
            VisionResult con el diagnóstico completo.
        """
        ...
