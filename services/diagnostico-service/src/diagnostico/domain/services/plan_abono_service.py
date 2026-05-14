"""
Servicio de dominio: generación y gestión de planes de abono.

Reglas de negocio clave (ADR-06):
- No se genera plan si la planta está enferma (tiene patologías urgentes).
- No se mezclan dos fertilizantes el mismo día.
- Solo se recomienda entre 05:00 y 09:00.
- Si no hay deficiencias, se genera un plan de mantenimiento estándar.
"""
from datetime import UTC, datetime, timedelta
from uuid import UUID

from diagnostico.domain.exceptions import (
    DiagnosticoNotFoundError,
    PlantaEnfermaError,
)
from diagnostico.domain.models.diagnostico import EstadoGeneral
from diagnostico.domain.models.plan_abono import (
    AplicacionFertilizante,
    PlanAbono,
    Recordatorio,
)
from diagnostico.domain.repositories.i_diagnostico_repository import (
    IDiagnosticoRepository,
    IPlanAbonoRepository,
    IRecordatorioRepository,
)

# Fertilizantes por deficiencia
_FERTILIZANTES: dict[str, dict[str, str]] = {
    "N": {"producto": "Urea (46% N)", "dosis": "40-60 kg/ha"},
    "P": {"producto": "Superfosfato Triple", "dosis": "30-50 kg/ha"},
    "K": {"producto": "Cloruro de Potasio", "dosis": "50-80 kg/ha"},
    "Mg": {"producto": "Sulfato de Magnesio", "dosis": "15-25 kg/ha"},
    "Fe": {"producto": "Sulfato Ferroso (quelato)", "dosis": "10-15 kg/ha"},
    "Mn": {"producto": "Sulfato de Manganeso", "dosis": "5-10 kg/ha"},
    "B": {"producto": "Bórax", "dosis": "2-4 kg/ha"},
    "Zn": {"producto": "Sulfato de Zinc", "dosis": "8-12 kg/ha"},
    "Ca": {"producto": "Nitrato de Calcio", "dosis": "30-40 kg/ha"},
}

_PLAN_MANTENIMIENTO = {
    "producto": "Fertilizante completo NPK 15-15-15",
    "dosis": "25-35 kg/ha",
}


class PlanAbonoService:
    """Caso de uso: generar y gestionar planes de abono."""

    def __init__(
        self,
        diagnostico_repo: IDiagnosticoRepository,
        plan_repo: IPlanAbonoRepository,
        recordatorio_repo: IRecordatorioRepository,
    ) -> None:
        self._diag_repo = diagnostico_repo
        self._plan_repo = plan_repo
        self._rec_repo = recordatorio_repo

    async def generar_plan(
        self,
        diagnostico_id: UUID,
        user_id: UUID,
    ) -> PlanAbono:
        """
        Generar plan de abono a partir de un diagnóstico.

        Raises:
            DiagnosticoNotFoundError: si el diagnóstico no existe.
            PlantaEnfermaError: si la planta tiene patologías urgentes.
        """
        diagnostico = await self._diag_repo.find_by_id(diagnostico_id)
        if diagnostico is None:
            raise DiagnosticoNotFoundError(str(diagnostico_id))
        if diagnostico.user_id != user_id:
            from diagnostico.domain.exceptions import CultivoNoAutorizadoError
            raise CultivoNoAutorizadoError()

        # Regla: no fertilizar si hay patologías urgentes
        if diagnostico.tiene_patologias_urgentes:
            raise PlantaEnfermaError(
                "No se puede generar un plan de abono mientras la planta "
                "tenga patologías activas de urgencia alta. "
                "Trate primero la patología detectada."
            )

        # Construir aplicaciones
        aplicaciones = self._construir_aplicaciones(diagnostico)

        plan = PlanAbono(
            diagnostico_id=diagnostico_id,
            cultivo_id=diagnostico.cultivo_id,
            user_id=user_id,
            aplicaciones=aplicaciones,
            observaciones_generales=(
                "Plan generado automáticamente. Consúltelo con un agrónomo."
                if diagnostico.estado_general == EstadoGeneral.SALUDABLE
                else "Seguimiento recomendado en 15 días tras la aplicación."
            ),
        )
        plan = await self._plan_repo.save(plan)

        # Crear recordatorios automáticamente
        for aplicacion in aplicaciones:
            recordatorio = Recordatorio(
                plan_id=plan.id,
                cultivo_id=plan.cultivo_id,
                user_id=user_id,
                producto=aplicacion.producto,
                dosis=aplicacion.dosis,
                fecha_programada=aplicacion.fecha_sugerida,
                hora_programada=aplicacion.hora_sugerida,
            )
            await self._rec_repo.save(recordatorio)

        return plan

    def _construir_aplicaciones(
        self,
        diagnostico: object,
    ) -> list[AplicacionFertilizante]:
        """Construir lista de aplicaciones según deficiencias detectadas."""
        from diagnostico.domain.models.diagnostico import Diagnostico
        diag: Diagnostico = diagnostico  # type: ignore[assignment]

        aplicaciones: list[AplicacionFertilizante] = []
        fecha_base = datetime.now(UTC) + timedelta(days=1)
        dias_offset = 0

        if not diag.deficiencias:
            # Plan de mantenimiento estándar
            aplicaciones.append(
                AplicacionFertilizante(
                    producto=_PLAN_MANTENIMIENTO["producto"],
                    dosis=_PLAN_MANTENIMIENTO["dosis"],
                    fecha_sugerida=fecha_base,
                    hora_sugerida="06:00",
                    observaciones="Aplicación de mantenimiento preventivo",
                )
            )
        else:
            # Una aplicación por deficiencia, en días distintos (regla: no mezclar)
            for deficiencia in diag.deficiencias:
                nutriente = deficiencia.nutriente
                fertilizante = _FERTILIZANTES.get(
                    nutriente,
                    {"producto": f"Fertilizante para {nutriente}", "dosis": "según etiqueta"},
                )
                aplicaciones.append(
                    AplicacionFertilizante(
                        producto=fertilizante["producto"],
                        dosis=fertilizante["dosis"],
                        fecha_sugerida=fecha_base + timedelta(days=dias_offset),
                        hora_sugerida="06:00",
                        observaciones=f"Corregir deficiencia de {nutriente}: {deficiencia.evidencia_visual}",
                    )
                )
                dias_offset += 3  # Espaciar aplicaciones 3 días

        return aplicaciones

    async def listar_planes(self, user_id: UUID) -> list[PlanAbono]:
        """Listar planes del usuario."""
        return await self._plan_repo.find_by_user(user_id)

    async def listar_recordatorios_pendientes(
        self, user_id: UUID
    ) -> list[Recordatorio]:
        """Listar recordatorios pendientes del usuario."""
        return await self._rec_repo.find_by_user_pendientes(user_id)

    async def completar_recordatorio(
        self,
        recordatorio_id: UUID,
        user_id: UUID,
        notas: str = "",
    ) -> Recordatorio:
        """Marcar recordatorio como completado."""
        from diagnostico.domain.exceptions import RecordatorioNotFoundError
        rec = await self._rec_repo.find_by_id(recordatorio_id)
        if rec is None:
            raise RecordatorioNotFoundError(str(recordatorio_id))
        if rec.user_id != user_id:
            from diagnostico.domain.exceptions import CultivoNoAutorizadoError
            raise CultivoNoAutorizadoError()
        rec.marcar_completado(notas)
        return await self._rec_repo.save(rec)
