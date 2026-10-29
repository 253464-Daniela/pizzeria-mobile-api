from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import Producto
from app.schemas.producto import ProductoOut

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