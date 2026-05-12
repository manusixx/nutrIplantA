"""Tests unitarios del modelo de dominio RefreshToken."""
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from auth.domain.models.refresh_token import RefreshToken


class TestRefreshToken:
    """Comportamiento del modelo RefreshToken."""

    def test_create_genera_token_valido(self) -> None:
        user_id = uuid4()
        token = RefreshToken.create(user_id, expire_days=7)

        assert token.user_id == user_id
        assert token.jti is not None
        assert token.is_valid
        assert not token.is_expired
        assert not token.is_revoked
        assert token.parent_jti is None

    def test_token_expira_segun_expire_days(self) -> None:
        token = RefreshToken.create(uuid4(), expire_days=7)
        delta = token.expires_at - token.created_at
        assert 6 * 24 * 3600 < delta.total_seconds() <= 7 * 24 * 3600 + 5

    def test_is_expired_con_token_vencido(self) -> None:
        token = RefreshToken(
            user_id=uuid4(),
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        assert token.is_expired
        assert not token.is_valid

    def test_revoke_cambia_estado(self) -> None:
        token = RefreshToken.create(uuid4())
        token.revoke()

        assert token.is_revoked
        assert token.revoked_at is not None
        assert not token.is_valid

    def test_revoke_es_idempotente(self) -> None:
        token = RefreshToken.create(uuid4())
        token.revoke()
        revoked_at_first = token.revoked_at
        token.revoke()  # Segunda vez no debe cambiar revoked_at
        assert token.revoked_at == revoked_at_first

    def test_rotate_revoca_padre_y_crea_hijo(self) -> None:
        parent = RefreshToken.create(uuid4())
        child = parent.rotate(expire_days=7)

        assert parent.is_revoked
        assert child.is_valid
        assert child.parent_jti == parent.jti
        assert child.user_id == parent.user_id
        assert child.jti != parent.jti

    def test_dos_rotaciones_crean_cadena(self) -> None:
        token1 = RefreshToken.create(uuid4())
        token2 = token1.rotate()
        token3 = token2.rotate()

        assert token1.is_revoked
        assert token2.is_revoked
        assert token3.is_valid
        assert token3.parent_jti == token2.jti
