"""
Servicio de dominio: gestión de diagnósticos.

Orquesta la subida de foto, análisis con visión y persistencia.
"""
from uuid import UUID

from diagnostico.domain.exceptions import (
    CultivoNoAutorizadoError,
    CultivoNotFoundError,
    DiagnosticoNotFoundError,
)
from diagnostico.domain.models.diagnostico import Diagnostico
from diagnostico.domain.repositories.i_cultivo_repository import ICultivoRepository
from diagnostico.domain.repositories.i_diagnostico_repository import (
    IDiagnosticoRepository,
)
from diagnostico.domain.repositories.i_vision_provider import IVisionProvider


class DiagnosticoService:
    """Caso de uso: crear y consultar diagnósticos de vid."""

    def __init__(
        self,
        diagnostico_repo: IDiagnosticoRepository,
        cultivo_repo: ICultivoRepository,
        vision_provider: IVisionProvider,
    ) -> None:
        self._repo = diagnostico_repo
        self._cultivo_repo = cultivo_repo
        self._vision = vision_provider

    async def crear_diagnostico(
        self,
        cultivo_id: UUID,
        user_id: UUID,
        foto_url: str,
    ) -> Diagnostico:
        """
        Analizar una foto y crear el diagnóstico.

        Reglas de negocio:
        - El cultivo debe existir y pertenecer al usuario.
        - Se delega el análisis al IVisionProvider.
        """
        cultivo = await self._cultivo_repo.find_by_id(cultivo_id)
        if cultivo is None:
            raise CultivoNotFoundError(str(cultivo_id))
        if cultivo.user_id != user_id:
            raise CultivoNoAutorizadoError()

        result = await self._vision.analyze(foto_url)

        diagnostico = Diagnostico(
            cultivo_id=cultivo_id,
            user_id=user_id,
            foto_url=foto_url,
            confianza_global=result.confianza_global,
            estado_general=result.estado_general,
            es_imagen_valida=result.es_imagen_valida,
            razon_invalidez=result.razon_invalidez,
            estado_fenologico=result.estado_fenologico,
            deficiencias=result.deficiencias,
            patologias=result.patologias,
            descripcion_hallazgo=result.descripcion_hallazgo,
            recomendacion_tecnica=result.recomendacion_tecnica,
            recomendacion_natural="",
        )
        return await self._repo.save(diagnostico)

    async def obtener(self, diagnostico_id: UUID, user_id: UUID) -> Diagnostico:
        """Obtener diagnóstico verificando que pertenece al usuario."""
        diagnostico = await self._repo.find_by_id(diagnostico_id)
        if diagnostico is None:
            raise DiagnosticoNotFoundError(str(diagnostico_id))
        if diagnostico.user_id != user_id:
            raise CultivoNoAutorizadoError()
        return diagnostico

    async def historial_usuario(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Diagnostico]:
        """Listar historial de diagnósticos del usuario."""
        return await self._repo.find_by_user(user_id, limit=limit, offset=offset)

    async def historial_cultivo(
        self,
        cultivo_id: UUID,
        user_id: UUID,
    ) -> list[Diagnostico]:
        """Listar diagnósticos de un cultivo específico."""
        cultivo = await self._cultivo_repo.find_by_id(cultivo_id)
        if cultivo is None:
            raise CultivoNotFoundError(str(cultivo_id))
        if cultivo.user_id != user_id:
            raise CultivoNoAutorizadoError()
        return await self._repo.find_by_cultivo(cultivo_id, user_id)
