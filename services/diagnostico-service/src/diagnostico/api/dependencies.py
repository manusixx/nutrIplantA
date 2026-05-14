"""
Dependencias FastAPI para el diagnostico-service.
Valida JWT y extrae el user_id del token.
"""
import os
from uuid import UUID

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException


# Singleton para evitar B008
def _get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY", "")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY no configurada")
    return secret


async def get_current_user_id(
    authorization: str = Header(..., alias="Authorization"),
) -> UUID:
    """
    Valida el JWT del header Authorization y retorna el user_id (sub).
    Lanza 401 si el token es inválido o expirado.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    token = authorization.removeprefix("Bearer ")
    secret = _get_jwt_secret()
    try:
        payload = pyjwt.decode(token, secret, algorithms=["HS256"])
        return UUID(str(payload["sub"]))
    except pyjwt.ExpiredSignatureError as err:
        raise HTTPException(status_code=401, detail="Token expirado") from err
    except pyjwt.InvalidTokenError as err:
        raise HTTPException(status_code=401, detail="Token inválido") from err
    except (KeyError, ValueError) as err:
        raise HTTPException(status_code=401, detail="Token malformado") from err


# Singleton a nivel de módulo — evita B008
CURRENT_USER_ID = Depends(get_current_user_id)
