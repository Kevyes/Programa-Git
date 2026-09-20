"""Mecanismos de seguridad: hash bcrypt con salt y tokens JWT."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def _a_bytes(password: str) -> bytes:
    # bcrypt solo procesa los primeros 72 bytes.
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt (incluye salt aleatorio) de la contraseña."""
    return bcrypt.hashpw(_a_bytes(password), bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_a_bytes(password), password_hash.encode())
    except ValueError:
        return False


def create_access_token(user_id: int, rol: str) -> str:
    """Crea un JWT con expiración (RNF02)."""
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "rol": rol, "exp": expira}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Valida firma y expiración. Lanza jwt.PyJWTError si el token no es válido."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
