from collections.abc import AsyncGenerator
from uuid import UUID

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.models import Empleado
from app.models.enums import RolEmpleado

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_empleado(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Empleado:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise cred_exc
        empleado_id = UUID(sub)
    except (pyjwt.PyJWTError, ValueError):
        raise cred_exc

    result = await db.execute(select(Empleado).where(Empleado.id == empleado_id))
    empleado = result.scalar_one_or_none()
    if not empleado or not empleado.activo:
        raise cred_exc
    return empleado

def require_rol(*roles: RolEmpleado):
    async def _check(empleado: Empleado = Depends(get_current_empleado)) -> Empleado:
        if empleado.rol not in roles:
            raise HTTPException(status_code=403, detail="No autorizado para esta acción")
        return empleado
    return _check