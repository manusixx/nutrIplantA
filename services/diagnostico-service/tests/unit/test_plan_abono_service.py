"""Tests unitarios del PlanAbonoService."""
from uuid import uuid4

import pytest

from diagnostico.domain.exceptions import DiagnosticoNotFoundError, PlantaEnfermaError
from diagnostico.domain.models.diagnostico import (
    DeficienciaNutricional,
    Diagnostico,
    EstadoGeneral,
    NivelConfianza,
    PatologiaDetectada,
)
from diagnostico.domain.models.plan_abono import EstadoRecordatorio
from diagnostico.domain.services.plan_abono_service import PlanAbonoService
from diagnostico.infrastructure.persistence.in_memory_diagnostico_repository import (
    InMemoryDiagnosticoRepository,
    InMemoryPlanAbonoRepository,
    InMemoryRecordatorioRepository,
)

USER_ID = uuid4()


@pytest.fixture
def diag_repo() -> InMemoryDiagnosticoRepository:
    return InMemoryDiagnosticoRepository()


@pytest.fixture
def plan_repo() -> InMemoryPlanAbonoRepository:
    return InMemoryPlanAbonoRepository()


@pytest.fixture
def rec_repo() -> InMemoryRecordatorioRepository:
    return InMemoryRecordatorioRepository()


@pytest.fixture
def service(
    diag_repo: InMemoryDiagnosticoRepository,
    plan_repo: InMemoryPlanAbonoRepository,
    rec_repo: InMemoryRecordatorioRepository,
) -> PlanAbonoService:
    return PlanAbonoService(diag_repo, plan_repo, rec_repo)


def _make_diagnostico(
    user_id: object = None,
    estado: EstadoGeneral = EstadoGeneral.REQUIERE_ATENCION,
    deficiencias: list = None,
    patologias: list = None,
) -> Diagnostico:
    if patologias is None:
        patologias = []
    if deficiencias is None:
        deficiencias = []
    uid = user_id if user_id is not None else USER_ID
    return Diagnostico(
        cultivo_id=uuid4(),
        user_id=uid,  # type: ignore[arg-type]
        foto_url="minio://test/foto.jpg",
        confianza_global=0.9,
        estado_general=estado,
        deficiencias=list(deficiencias),
        patologias=list(patologias),
    )


class TestPlanAbonoServiceGenerar:
    @pytest.mark.asyncio
    async def test_genera_plan_para_diagnostico_sin_deficiencias(
        self,
        service: PlanAbonoService,
        diag_repo: InMemoryDiagnosticoRepository,
    ) -> None:
        diag = _make_diagnostico(estado=EstadoGeneral.SALUDABLE)
        await diag_repo.save(diag)

        plan = await service.generar_plan(diag.id, USER_ID)

        assert plan.id is not None
        assert plan.diagnostico_id == diag.id
        assert len(plan.aplicaciones) == 1  # Plan de mantenimiento
        assert "NPK" in plan.aplicaciones[0].producto

    @pytest.mark.asyncio
    async def test_genera_plan_con_aplicacion_por_deficiencia(
        self,
        service: PlanAbonoService,
        diag_repo: InMemoryDiagnosticoRepository,
    ) -> None:
        deficiencias = [
            DeficienciaNutricional("N", "Clorosis", NivelConfianza.ALTA),
            DeficienciaNutricional("K", "Necrosis", NivelConfianza.MEDIA),
        ]
        diag = _make_diagnostico(deficiencias=deficiencias)
        await diag_repo.save(diag)

        plan = await service.generar_plan(diag.id, USER_ID)

        assert len(plan.aplicaciones) == 2
        productos = [a.producto for a in plan.aplicaciones]
        assert any("Urea" in p for p in productos)
        assert any("Potasio" in p for p in productos)

    @pytest.mark.asyncio
    async def test_no_mezcla_fertilizantes_mismo_dia(
        self,
        service: PlanAbonoService,
        diag_repo: InMemoryDiagnosticoRepository,
    ) -> None:
        deficiencias = [
            DeficienciaNutricional("N", "Clorosis", NivelConfianza.ALTA),
            DeficienciaNutricional("K", "Necrosis", NivelConfianza.ALTA),
        ]
        diag = _make_diagnostico(deficiencias=deficiencias)
        await diag_repo.save(diag)

        plan = await service.generar_plan(diag.id, USER_ID)

        fechas = [a.fecha_sugerida.date() for a in plan.aplicaciones]
        assert len(set(fechas)) == len(fechas)  # Todas distintas

    @pytest.mark.asyncio
    async def test_falla_si_planta_tiene_patologia_urgente(
        self,
        service: PlanAbonoService,
        diag_repo: InMemoryDiagnosticoRepository,
    ) -> None:
        patologias = [
            PatologiaDetectada(
                tipo="hongo",
                nombre="Botrytis cinerea",
                evidencia_visual="Manchas grises",
                confianza=NivelConfianza.ALTA,
                urgencia=NivelConfianza.ALTA,
            )
        ]
        diag = _make_diagnostico(
            estado=EstadoGeneral.CRITICO,
            patologias=patologias,
        )
        await diag_repo.save(diag)

        with pytest.raises(PlantaEnfermaError):
            await service.generar_plan(diag.id, USER_ID)

    @pytest.mark.asyncio
    async def test_falla_si_diagnostico_no_existe(
        self, service: PlanAbonoService
    ) -> None:
        with pytest.raises(DiagnosticoNotFoundError):
            await service.generar_plan(uuid4(), USER_ID)

    @pytest.mark.asyncio
    async def test_crea_recordatorios_automaticamente(
        self,
        service: PlanAbonoService,
        diag_repo: InMemoryDiagnosticoRepository,
        rec_repo: InMemoryRecordatorioRepository,
    ) -> None:
        deficiencias = [DeficienciaNutricional("N", "Clorosis", NivelConfianza.ALTA)]
        diag = _make_diagnostico(deficiencias=deficiencias)
        await diag_repo.save(diag)

        plan = await service.generar_plan(diag.id, USER_ID)
        recordatorios = await rec_repo.find_by_plan(plan.id)

        assert len(recordatorios) == 1
        assert recordatorios[0].estado == EstadoRecordatorio.PENDIENTE

    @pytest.mark.asyncio
    async def test_completar_recordatorio(
        self,
        service: PlanAbonoService,
        diag_repo: InMemoryDiagnosticoRepository,
    ) -> None:
        diag = _make_diagnostico()
        await diag_repo.save(diag)
        plan = await service.generar_plan(diag.id, USER_ID)
        assert plan is not None

        pendientes = await service.listar_recordatorios_pendientes(USER_ID)
        assert len(pendientes) > 0

        rec_completado = await service.completar_recordatorio(
            pendientes[0].id, USER_ID, "Aplicado exitosamente"
        )

        assert rec_completado.estado == EstadoRecordatorio.COMPLETADO
        assert rec_completado.notas == "Aplicado exitosamente"
