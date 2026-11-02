from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import Producto
from app.schemas.producto import ProductoOut

from app.api.deps import get_db, get_current_empleado
from pydantic import BaseModel

router = APIRouter(prefix="/productos", tags=["catálogo"])

@router.get("", response_model=list[ProductoOut])
async def listar_productos(
    categoria_id: UUID | None = None,
    solo_disponibles: bool = True,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Producto).options(selectinload(Producto.ingredientes))
    if categoria_id:
        stmt = stmt.where(Producto.categoria_id == categoria_id)
    if solo_disponibles:
        stmt = stmt.where(Producto.disponible.is_(True))
    stmt = stmt.order_by(Producto.nombre)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{producto_id}", response_model=ProductoOut)
async def obtener_producto(producto_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Producto)
        .options(selectinload(Producto.ingredientes))
        .where(Producto.id == producto_id)
    )
    result = await db.execute(stmt)
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: str | None = None
    precio: float
    categoria_id: UUID
    disponible: bool = True

@router.post("", response_model=ProductoOut, status_code=201)
async def crear_producto(data: ProductoCreate, db: AsyncSession = Depends(get_db), _emp = Depends(get_current_empleado)):
    nuevo = Producto(**data.model_dump())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

@router.put("/{producto_id}", response_model=ProductoOut)
async def actualizar_producto(producto_id: UUID, data: ProductoCreate, db: AsyncSession = Depends(get_db), _emp = Depends(get_current_empleado)):
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    prod = result.scalar_one_or_none()
    if not prod: raise HTTPException(404, "No encontrado")
    
    for key, value in data.model_dump().items():
        setattr(prod, key, value)
    
    await db.commit()
    await db.refresh(prod)
    return prod

@router.delete("/{producto_id}", status_code=204)
async def eliminar_producto(producto_id: UUID, db: AsyncSession = Depends(get_db), _emp = Depends(get_current_empleado)):
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    prod = result.scalar_one_or_none()
    if prod:
        await db.delete(prod)
        await db.commit()
    return None