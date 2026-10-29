from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_rol
from app.core.security import hash_password
from app.models import Empleado
from app.models.enums import RolEmpleado
from app.schemas.auth import EmpleadoOut
from app.schemas.empleado import EmpleadoCreate, EmpleadoUpdate

router = APIRouter(prefix="/empleados", tags=["empleados"])

@router.post("", response_model=EmpleadoOut, status_code=201)
async def crear_empleado(
    data: EmpleadoCreate, 
    db: AsyncSession = Depends(get_db),
    _admin: Empleado = Depends(require_rol(RolEmpleado.ADMIN))
):
    existe = await db.execute(select(Empleado).where(Empleado.email == data.email))
    if existe.scalar_one_or_none():
        raise HTTPException(400, "El email ya está registrado")

    nuevo = Empleado(
        nombre=data.nombre, email=data.email, 
        password_hash=hash_password(data.password), rol=data.rol
    )
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.get("", response_model=list[EmpleadoOut])
async def listar_empleados(
    db: AsyncSession = Depends(get_db),
    _admin: Empleado = Depends(require_rol(RolEmpleado.ADMIN))
):
    res = await db.execute(select(Empleado).order_by(Empleado.nombre))
    return res.scalars().all()

@router.patch("/{empleado_id}", response_model=EmpleadoOut)
async def actualizar_empleado(
    empleado_id: str,
    data: EmpleadoUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: Empleado = Depends(require_rol(RolEmpleado.ADMIN))
):
    res = await db.execute(select(Empleado).where(Empleado.id == empleado_id))
    emp = res.scalar_one_or_none()
    if not emp:
        raise HTTPException(404, "Empleado no encontrado")
    
    if data.nombre is not None: emp.nombre = data.nombre
    if data.rol is not None: emp.rol = data.rol
    if data.activo is not None: emp.activo = data.activo
    
    await db.commit()
    await db.refresh(emp)
    return emp