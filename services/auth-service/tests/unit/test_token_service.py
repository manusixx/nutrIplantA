"""Tests unitarios del TokenService (emisión y decodificación de JWT)."""
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from auth.domain.models.user import User, UserRole, UserStatus
from auth.domain.services.token_service import TokenService

# Secret de prueba (mínimo 32 caracteres como exige el constructor)
TEST_SECRET = "a" * 64  # 64 caracteres de 'a'


@pytest.fixture
def token_service() -> TokenService:
    """TokenService con configuración predecible para tests."""
    return TokenService(
        secret_key=TEST_SECRET,
        algorithm="HS256",
        access_token_expire_minutes=15,
    )


@pytest.fixture
def approved_user() -> User:
    """Usuario aprobado con rol AGRICULTOR (puede recibir token)."""
    return User(
        email="agricultor@example.com",
        full_name="Manuel Pastrana",
        password_hash="hash",
        role=UserRole.AGRICULTOR,
        status=UserStatus.APROBADO,
    )


class TestTokenServiceInit:
    """Validaciones del constructor."""

    def test_falla_si_secret_es_vacio(self) -> None:
        with pytest.raises(ValueError, match="al menos 32 caracteres"):
            TokenService(secret_key="")

    def test_falla_si_secret_es_muy_corto(self) -> None:
        with pytest.raises(ValueError, match="al menos 32 caracteres"):
            TokenService(secret_key="corto")

    def test_se_crea_con_secret_de_32_caracteres_minimo(self) -> None:
        # No debe lanzar excepción
        service = TokenService(secret_key="a" * 32)
        assert service is not None


class TestCreateAccessToken:
    """Comportamiento de create_access_token."""

    def test_emite_token_para_usuario_aprobado_con_rol(
        self, token_service: TokenService, approved_user: User
    ) -> None:
        token = token_service.create_access_token(approved_user)

        assert isinstance(token, str)
        assert len(token) > 50  # Un JWT firmado siempre es largo

    def test_falla_si_usuario_no_puede_iniciar_sesion(
        self, token_service: TokenService
    ) -> None:
        """Usuarios sin rol o no aprobados no deben recibir token."""
        user_pendiente = User(
            email="x@x.com",
            full_name="X",
            password_hash="h",
        )  # status default: PENDIENTE_APROBACION

        with pytest.raises(ValueError, match="no puede iniciar sesión"):
            token_service.create_access_token(user_pendiente)

    def test_token_contiene_claims_esperados(
        self, token_service: TokenService, approved_user: User
    ) -> None:
        token = token_service.create_access_token(approved_user)
        payload = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])

        assert payload["sub"] == str(approved_user.id)
        assert payload["email"] == approved_user.email
        assert payload["role"] == UserRole.AGRICULTOR.value
        assert payload["type"] == "access"
        assert "jti" in payload
        assert "iat" in payload
        assert "exp" in payload

    def test_token_tiene_jti_unico_en_cada_emision(
        self, token_service: TokenService, approved_user: User
    ) -> None:
        """Dos tokens del mismo usuario deben tener jti distintos."""
        token1 = token_service.create_access_token(approved_user)
        token2 = token_service.create_access_token(approved_user)

        payload1 = jwt.decode(token1, TEST_SECRET, algorithms=["HS256"])
        payload2 = jwt.decode(token2, TEST_SECRET, algorithms=["HS256"])

        assert payload1["jti"] != payload2["jti"]

    def test_token_expira_15_minutos_despues_de_emision(
        self, token_service: TokenService, approved_user: User
    ) -> None:
        token = token_service.create_access_token(approved_user)
        payload = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])

        # exp - iat debe ser aproximadamente 15 minutos
        delta = payload["exp"] - payload["iat"]
        assert delta == 15 * 60  # 15 minutos en segundos


class TestDecodeToken:
    """Comportamiento de decode_token."""

    def test_decodifica_token_emitido_por_el_mismo_servicio(
        self, token_service: TokenService, approved_user: User
    ) -> None:
        token = token_service.create_access_token(approved_user)

        payload = token_service.decode_token(token)

        assert payload["sub"] == str(approved_user.id)
        assert payload["email"] == approved_user.email

    def test_falla_con_token_invalido(self, token_service: TokenService) -> None:
        with pytest.raises(jwt.InvalidTokenError):
            token_service.decode_token("esto-no-es-un-jwt")

    def test_falla_con_token_firmado_por_otra_secret(
        self, token_service: TokenService, approved_user: User
    ) -> None:
        """Un token firmado por otro secret debe ser rechazado."""
        otro_secret = "b" * 64
        otro_service = TokenService(secret_key=otro_secret)
        token_de_otro = otro_service.create_access_token(approved_user)

        with pytest.raises(jwt.InvalidSignatureError):
            token_service.decode_token(token_de_otro)

    def test_falla_con_token_expirado(self, approved_user: User) -> None:
        """Token con exp en el pasado debe lanzar ExpiredSignatureError."""
        # Crear manualmente un token ya expirado
        now = datetime.now(UTC)
        payload = {
            "sub": str(approved_user.id),
            "email": approved_user.email,
            "role": approved_user.role.value if approved_user.role else None,
            "jti": str(uuid4()),
            "iat": int((now - timedelta(hours=1)).timestamp()),
            "exp": int((now - timedelta(minutes=30)).timestamp()),
            "type": "access",
        }
        expired_token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")

        service = TokenService(secret_key=TEST_SECRET)
        with pytest.raises(jwt.ExpiredSignatureError):
            service.decode_token(expired_token)