"""
MockVisionProvider: implementación simulada para desarrollo y tests.

Devuelve respuestas predefinidas realistas sin llamar a ningún servicio
externo. Selecciona la respuesta según el hash de la URL de la imagen
para que las respuestas sean deterministas (misma imagen = mismo resultado).
"""
from diagnostico.domain.models.diagnostico import (
    DeficienciaNutricional,
    EstadoGeneral,
    NivelConfianza,
    PatologiaDetectada,
)
from diagnostico.domain.repositories.i_vision_provider import (
    IVisionProvider,
    VisionResult,
)

_MOCK_SCENARIOS = [
    VisionResult(
        es_imagen_valida=True,
        razon_invalidez=None,
        confianza_global=0.942,
        estado_general=EstadoGeneral.REQUIERE_ATENCION,
        estado_fenologico="Brotación",
        deficiencias=[
            DeficienciaNutricional(
                nutriente="N",
                evidencia_visual="Clorosis generalizada en hojas basales, amarillamiento uniforme del limbo",
                confianza=NivelConfianza.ALTA,
            )
        ],
        patologias=[],
        descripcion_hallazgo=(
            "Se observa clorosis generalizada que comienza en las hojas basales. "
            "La decoloración amarillenta es uniforme en todo el limbo foliar, "
            "indicando deficiencia de nitrógeno."
        ),
        recomendacion_tecnica=(
            "Aplicar fertilizante nitrogenado de liberación rápida (Urea o Nitrato de Amonio) "
            "en dosis de 40-60 kg/ha. Realizar seguimiento foliar en 15 días."
        ),
    ),
    VisionResult(
        es_imagen_valida=True,
        razon_invalidez=None,
        confianza_global=0.987,
        estado_general=EstadoGeneral.SALUDABLE,
        estado_fenologico="Floración",
        deficiencias=[],
        patologias=[],
        descripcion_hallazgo="La hoja presenta coloración verde uniforme sin síntomas visibles de deficiencias o patologías.",
        recomendacion_tecnica="La planta se encuentra en estado óptimo. Mantener el plan de fertilización actual.",
    ),
    VisionResult(
        es_imagen_valida=True,
        razon_invalidez=None,
        confianza_global=0.876,
        estado_general=EstadoGeneral.CRITICO,
        estado_fenologico="Envero",
        deficiencias=[
            DeficienciaNutricional(
                nutriente="K",
                evidencia_visual="Necrosis marginal en hojas maduras, bordes marrones y secos",
                confianza=NivelConfianza.ALTA,
            ),
            DeficienciaNutricional(
                nutriente="Mg",
                evidencia_visual="Clorosis internerval en hojas medias",
                confianza=NivelConfianza.MEDIA,
            ),
        ],
        patologias=[
            PatologiaDetectada(
                tipo="hongo",
                nombre="Botrytis cinerea",
                evidencia_visual="Manchas pardas con esporulación gris en el envés",
                confianza=NivelConfianza.MEDIA,
                urgencia=NivelConfianza.ALTA,
            )
        ],
        descripcion_hallazgo=(
            "Se detectan múltiples problemas: deficiencia severa de potasio con necrosis "
            "marginal, deficiencia de magnesio y posible presencia de Botrytis cinerea."
        ),
        recomendacion_tecnica=(
            "Atención urgente requerida. Tratar primero la infección fúngica con fungicida "
            "apropiado antes de iniciar plan de fertilización."
        ),
    ),
    VisionResult(
        es_imagen_valida=False,
        razon_invalidez="La imagen está borrosa o con poca iluminación",
        confianza_global=0.0,
        estado_general=EstadoGeneral.REQUIERE_ATENCION,
        estado_fenologico=None,
        deficiencias=[],
        patologias=[],
        descripcion_hallazgo="",
        recomendacion_tecnica="",
    ),
]


class MockVisionProvider(IVisionProvider):
    """
    Proveedor de visión simulado. Devuelve escenarios predefinidos
    de forma determinista según el hash de la URL.
    """

    async def analyze(self, image_url: str) -> VisionResult:
        """Seleccionar escenario según hash de la URL."""
        scenario_index = hash(image_url) % len(_MOCK_SCENARIOS)
        return _MOCK_SCENARIOS[scenario_index]
