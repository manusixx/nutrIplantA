"""Tests unitarios del modelo de dominio User."""
import pytest

from auth.domain.models.user import User, UserRole, UserStatus


class TestUser:
    """Comportamiento del modelo User."""

    def test_user_se_crea_con_estado_inicial_pendiente(self) -> None:
        user = User(
            email="manuel@example.com",
            full_name="Manuel Pastrana",
            password_hash="hash123",
        )

        assert user.status == UserStatus.PENDIENTE_APROBACION
        assert user.role is None
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_can_login_es_false_si_pendiente_aprobacion(self) -> None:
        user = User(
            email="x@x.com",
            full_name="X",
            password_hash="h",
        )
        assert user.can_login() is False

    def test_can_login_es_false_si_aprobado_sin_rol(self) -> None:
        user = User(
            email="x@x.com",
            full_name="X",
            password_hash="h",
            status=UserStatus.APROBADO,
            role=None,
        )
        assert user.can_login() is False

    def test_can_login_es_true_si_aprobado_con_rol(self) -> None:
        user = User(
            email="x@x.com",
            full_name="X",
            password_hash="h",
            status=UserStatus.APROBADO,
            role=UserRole.AGRICULTOR,
        )
        assert user.can_login() is True

    def test_approve_asigna_rol_y_cambia_estado(self) -> None:
        user = User(email="x@x.com", full_name="X", password_hash="h")
        original_updated = user.updated_at

        user.approve(UserRole.INVESTIGADOR)

        assert user.status == UserStatus.APROBADO
        assert user.role == UserRole.INVESTIGADOR
        assert user.updated_at >= original_updated

    def test_approve_falla_si_no_esta_pendiente(self) -> None:
        user = User(
            email="x@x.com",
            full_name="X",
            password_hash="h",
            status=UserStatus.APROBADO,
            role=UserRole.AGRICULTOR,
        )
        with pytest.raises(ValueError, match="PENDIENTE_APROBACION"):
            user.approve(UserRole.INVESTIGADOR)

    def test_deactivate_cambia_estado(self) -> None:
        user = User(
            email="x@x.com",
            full_name="X",
            password_hash="h",
            status=UserStatus.APROBADO,
            role=UserRole.AGRICULTOR,
        )

        user.deactivate()

        assert user.status == UserStatus.DESACTIVADO
