"""Endpoints de diagnóstico y plan de abono — Sprints 5 y 6."""
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from diagnostico.api.dtos.diagnostico_dtos import (
    AplicacionResponse,
    CompletarRecordatorioRequest,
    DiagnosticoCreateRequest,
    DiagnosticoResponse,
    PlanAbonoCreateRequest,
    PlanAbonoResponse,
    RecordatorioResponse,
)
from diagnostico.domain.models.diagnostico import Diagnostico
from diagnostico.domain.models.plan_abono import PlanAbono, Recordatorio
from diagnostico.domain.services.diagnostico_service import DiagnosticoService
from diagnostico.domain.services.plan_abono_service import PlanAbonoService

router = APIRouter(prefix="/api/v1/diagnostico", tags=["diagnostico"])


def _diag_to_response(d: Diagnostico) -> DiagnosticoResponse:
    from diagnostico.api.dtos.diagnostico_dtos import (
        DeficienciaResponse,
        PatologiaResponse,
    )
    return DiagnosticoResponse(
        id=d.id,
        cultivo_id=d.cultivo_id,
        user_id=d.user_id,
        foto_url=d.foto_url,
        confianza_global=d.confianza_global,
        estado_general=d.estado_general,
        es_imagen_valida=d.es_imagen_valida,
        razon_invalidez=d.razon_invalidez,
        estado_fenologico=d.estado_fenologico,
        deficiencias=[
            DeficienciaResponse(
                nutriente=def_.nutriente,
                evidencia_visual=def_.evidencia_visual,
                confianza=def_.confianza,
            )
            for def_ in d.deficiencias
        ],
        patologias=[
            PatologiaResponse(
                tipo=pat.tipo,
                nombre=pat.nombre,
                evidencia_visual=pat.evidencia_visual,
                confianza=pat.confianza,
                urgencia=pat.urgencia,
            )
            for pat in d.patologias
        ],
        descripcion_hallazgo=d.descripcion_hallazgo,
        recomendacion_tecnica=d.recomendacion_tecnica,
        recomendacion_natural=d.recomendacion_natural,
        created_at=d.created_at,
    )


def _plan_to_response(p: PlanAbono) -> PlanAbonoResponse:
    return PlanAbonoResponse(
        id=p.id,
        diagnostico_id=p.diagnostico_id,
        cultivo_id=p.cultivo_id,
        user_id=p.user_id,
        aplicaciones=[
            AplicacionResponse(
                producto=a.producto,
                dosis=a.dosis,
                fecha_sugerida=a.fecha_sugerida,
                hora_sugerida=a.hora_sugerida,
                observaciones=a.observaciones,
            )
            for a in p.aplicaciones
        ],
        observaciones_generales=p.observaciones_generales,
        created_at=p.created_at,
    )


def _rec_to_response(r: Recordatorio) -> RecordatorioResponse:
    return RecordatorioResponse(
        id=r.id,
        plan_id=r.plan_id,
        cultivo_id=r.cultivo_id,
        producto=r.producto,
        dosis=r.dosis,
        fecha_programada=r.fecha_programada,
        hora_programada=r.hora_programada,
        estado=r.estado,
        notas=r.notas,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


def _get_diagnostico_service() -> DiagnosticoService:
    raise NotImplementedError


def _get_plan_service() -> PlanAbonoService:
    raise NotImplementedError


# ============================================================
# Diagnósticos
# ============================================================
@router.post(
    "/diagnosticos",
    response_model=DiagnosticoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear diagnóstico (HU-10)",
)
async def crear_diagnostico(
    payload: DiagnosticoCreateRequest,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: DiagnosticoService = Depends(_get_diagnostico_service),
) -> DiagnosticoResponse:
    """Analizar una foto de hoja y crear el diagnóstico nutricional."""
    diagnostico = await service.crear_diagnostico(
        cultivo_id=payload.cultivo_id,
        user_id=x_user_id,
        foto_url=payload.foto_url,
    )
    return _diag_to_response(diagnostico)


@router.get(
    "/diagnosticos",
    response_model=list[DiagnosticoResponse],
    summary="Historial de diagnósticos (HU-13)",
)
async def listar_diagnosticos(
    limit: int = 20,
    offset: int = 0,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: DiagnosticoService = Depends(_get_diagnostico_service),
) -> list[DiagnosticoResponse]:
    """Listar historial de diagnósticos del usuario autenticado."""
    diagnosticos = await service.historial_usuario(x_user_id, limit=limit, offset=offset)
    return [_diag_to_response(d) for d in diagnosticos]


@router.get(
    "/diagnosticos/{diagnostico_id}",
    response_model=DiagnosticoResponse,
    summary="Obtener diagnóstico por ID",
)
async def obtener_diagnostico(
    diagnostico_id: UUID,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: DiagnosticoService = Depends(_get_diagnostico_service),
) -> DiagnosticoResponse:
    """Obtener un diagnóstico específico."""
    diagnostico = await service.obtener(diagnostico_id, x_user_id)
    return _diag_to_response(diagnostico)


@router.get(
    "/cultivos/{cultivo_id}/diagnosticos",
    response_model=list[DiagnosticoResponse],
    summary="Diagnósticos de un cultivo (HU-11)",
)
async def diagnosticos_por_cultivo(
    cultivo_id: UUID,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: DiagnosticoService = Depends(_get_diagnostico_service),
) -> list[DiagnosticoResponse]:
    """Listar diagnósticos de un cultivo específico."""
    diagnosticos = await service.historial_cultivo(cultivo_id, x_user_id)
    return [_diag_to_response(d) for d in diagnosticos]


# ============================================================
# Planes de abono
# ============================================================
@router.post(
    "/planes",
    response_model=PlanAbonoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar plan de abono (HU-09)",
)
async def generar_plan(
    payload: PlanAbonoCreateRequest,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: PlanAbonoService = Depends(_get_plan_service),
) -> PlanAbonoResponse:
    """Generar un plan de abono a partir de un diagnóstico."""
    plan = await service.generar_plan(payload.diagnostico_id, x_user_id)
    return _plan_to_response(plan)


@router.get(
    "/planes",
    response_model=list[PlanAbonoResponse],
    summary="Listar planes de abono (HU-12)",
)
async def listar_planes(
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: PlanAbonoService = Depends(_get_plan_service),
) -> list[PlanAbonoResponse]:
    """Listar planes de abono del usuario."""
    planes = await service.listar_planes(x_user_id)
    return [_plan_to_response(p) for p in planes]


# ============================================================
# Recordatorios
# ============================================================
@router.get(
    "/recordatorios",
    response_model=list[RecordatorioResponse],
    summary="Listar recordatorios pendientes (HU-16)",
)
async def listar_recordatorios(
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: PlanAbonoService = Depends(_get_plan_service),
) -> list[RecordatorioResponse]:
    """Listar recordatorios pendientes del usuario."""
    recordatorios = await service.listar_recordatorios_pendientes(x_user_id)
    return [_rec_to_response(r) for r in recordatorios]


@router.patch(
    "/recordatorios/{recordatorio_id}/completar",
    response_model=RecordatorioResponse,
    summary="Marcar recordatorio completado",
)
async def completar_recordatorio(
    recordatorio_id: UUID,
    payload: CompletarRecordatorioRequest,
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    service: PlanAbonoService = Depends(_get_plan_service),
) -> RecordatorioResponse:
    """Marcar un recordatorio de aplicación como completado."""
    rec = await service.completar_recordatorio(recordatorio_id, x_user_id, payload.notas)
    return _rec_to_response(rec)
