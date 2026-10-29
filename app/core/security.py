from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

_MAX_BYTES = 72  # límite de bcrypt


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")
    if len(pw) > _MAX_BYTES:
        raise ValueError("Password demasiado largo (máx 72 bytes)")
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, rol: str, nombre: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "rol": rol,
        "nombre": nombre,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])