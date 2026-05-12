"""Endpoints CRUD de cultivos — Sprint 5."""
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from diagnostico.api.dtos.diagnostico_dtos import (
    CultivoCreateRequest,
    CultivoResponse,
    CultivoUpdateRequest,
)
from diagnostico.domain.models.cultivo import Cultivo
from diagnostico.domain.services.cultivo_service import CultivoService

router = APIRouter(prefix="/api/v1/diagnostico/cultivos", tags=["cultivos"])


def _cultivo_to_response(c: Cultivo) -> CultivoResponse:
    return CultivoResponse(
        id=c.id,
        user_id=c.user_id,
        nombre_finca=c.nombre_finca,
        variedad=c.variedad,
        vereda=c.vereda,
        fila=c.fila,
        subparcela=c.subparcela,
        notas=c.notas,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def _get_cultivo_service() -> CultivoService:
    raise NotImplementedError


@router.post(
    "",
    response_model=CultivoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar cultivo (HU-06)",
)
async def crear_cultivo(
    payload: CultivoCreateRequest,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: CultivoService = Depends(_get_cultivo_service),
) -> CultivoResponse:
    """Registrar un nuevo cultivo de vid para el usuario autenticado."""
    cultivo = await service.crear(
        user_id=x_user_id,
        nombre_finca=payload.nombre_finca,
        variedad=payload.variedad,
        vereda=payload.vereda,
        fila=payload.fila,
        subparcela=payload.subparcela,
        notas=payload.notas,
    )
    return _cultivo_to_response(cultivo)


@router.get(
    "",
    response_model=list[CultivoResponse],
    summary="Listar cultivos del usuario",
)
async def listar_cultivos(
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: CultivoService = Depends(_get_cultivo_service),
) -> list[CultivoResponse]:
    """Listar todos los cultivos del usuario autenticado."""
    cultivos = await service.listar(x_user_id)
    return [_cultivo_to_response(c) for c in cultivos]


@router.get(
    "/{cultivo_id}",
    response_model=CultivoResponse,
    summary="Obtener cultivo por ID",
)
async def obtener_cultivo(
    cultivo_id: UUID,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: CultivoService = Depends(_get_cultivo_service),
) -> CultivoResponse:
    """Obtener un cultivo específico del usuario autenticado."""
    cultivo = await service.obtener(cultivo_id, x_user_id)
    return _cultivo_to_response(cultivo)


@router.put(
    "/{cultivo_id}",
    response_model=CultivoResponse,
    summary="Actualizar cultivo",
)
async def actualizar_cultivo(
    cultivo_id: UUID,
    payload: CultivoUpdateRequest,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: CultivoService = Depends(_get_cultivo_service),
) -> CultivoResponse:
    """Actualizar datos de un cultivo del usuario autenticado."""
    cultivo = await service.actualizar(
        cultivo_id=cultivo_id,
        user_id=x_user_id,
        **payload.model_dump(exclude_none=True),
    )
    return _cultivo_to_response(cultivo)


@router.delete(
    "/{cultivo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar cultivo",
)
async def eliminar_cultivo(
    cultivo_id: UUID,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: CultivoService = Depends(_get_cultivo_service),
) -> None:
    """Eliminar un cultivo del usuario autenticado."""
    await service.eliminar(cultivo_id, x_user_id)
