"""
Implementación concreta del hasher con Argon2id.

Argon2id es el algoritmo recomendado por OWASP (2021+) para hash de
contraseñas. Resiste ataques con GPU y es el ganador del Password
Hashing Competition.

Esta clase implementa la interfaz IPasswordHasher del dominio.
"""
from pwdlib import PasswordHash

from auth.domain.repositories.i_password_hasher import IPasswordHasher


class Argon2PasswordHasher(IPasswordHasher):
    """Hasher Argon2id usando pwdlib (mantenido y recomendado en 2025)."""

    def __init__(self) -> None:
        # PasswordHash.recommended() usa Argon2id con parámetros seguros
        self._hasher = PasswordHash.recommended()

    def hash(self, plain_password: str) -> str:
        """Generar hash Argon2id de la contraseña."""
        if not plain_password:
            raise ValueError("La contraseña no puede estar vacía")
        return str(self._hasher.hash(plain_password))

    def verify(self, plain_password: str, password_hash: str) -> bool:
        """Verificar contraseña contra hash. False si no coincide o hay error."""
        if not plain_password or not password_hash:
            return False
        try:
            return bool(self._hasher.verify(plain_password, password_hash))
        except Exception:
            # Cualquier error en verificación se trata como falla
            # (hash corrupto, formato distinto, etc.)
            return False
