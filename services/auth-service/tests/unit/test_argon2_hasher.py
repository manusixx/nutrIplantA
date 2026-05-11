"""Tests del Argon2PasswordHasher (real, no fake)."""
import pytest

from auth.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)


class TestArgon2PasswordHasher:
    """Verificación del hasher real con Argon2id."""

    def test_hash_no_es_la_password_original(self) -> None:
        hasher = Argon2PasswordHasher()
        password = "MiP@ssw0rd!"

        hashed = hasher.hash(password)

        assert hashed != password
        assert len(hashed) > len(password)

    def test_hash_es_diferente_cada_vez_por_salt(self) -> None:
        """Argon2id incluye un salt aleatorio: dos hashes deben diferir."""
        hasher = Argon2PasswordHasher()
        password = "MiP@ssw0rd!"

        hash1 = hasher.hash(password)
        hash2 = hasher.hash(password)

        assert hash1 != hash2

    def test_verify_devuelve_true_con_password_correcta(self) -> None:
        hasher = Argon2PasswordHasher()
        password = "MiP@ssw0rd!"
        hashed = hasher.hash(password)

        assert hasher.verify(password, hashed) is True

    def test_verify_devuelve_false_con_password_incorrecta(self) -> None:
        hasher = Argon2PasswordHasher()
        hashed = hasher.hash("CorrectP@ss!")

        assert hasher.verify("WrongP@ss!", hashed) is False

    def test_verify_devuelve_false_con_password_vacia(self) -> None:
        hasher = Argon2PasswordHasher()
        hashed = hasher.hash("MiP@ssw0rd!")

        assert hasher.verify("", hashed) is False

    def test_verify_devuelve_false_con_hash_corrupto(self) -> None:
        hasher = Argon2PasswordHasher()

        assert hasher.verify("MiP@ssw0rd!", "esto-no-es-un-hash") is False

    def test_hash_falla_con_password_vacia(self) -> None:
        hasher = Argon2PasswordHasher()

        with pytest.raises(ValueError):
            hasher.hash("")
