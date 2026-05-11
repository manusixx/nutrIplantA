"""
Interfaz del hasher de contraseñas.

Permite intercambiar la implementación concreta (Argon2id, bcrypt, etc.)
sin tocar la lógica del dominio.
"""
from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Contrato para hashear y verificar contraseñas."""

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Generar el hash de una contraseña en texto plano."""
        ...

    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool:
        """Verificar si una contraseña en plano coincide con un hash dado."""
        ...
