from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_empleado, get_db
from app.core.security import create_access_token, verify_password
from app.models import Empleado
from app.schemas.auth import EmpleadoOut, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Empleado).where(Empleado.email == form.username))
    empleado = result.scalar_one_or_none()
    if (
        not empleado
        or not empleado.activo
        or not verify_password(form.password, empleado.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )
    token = create_access_token(str(empleado.id), empleado.rol.value, empleado.nombre)
    return TokenResponse(access_token=token, rol=empleado.rol, nombre=empleado.nombre)


@router.get("/me", response_model=EmpleadoOut)
async def me(empleado: Empleado = Depends(get_current_empleado)):
    return empleado
