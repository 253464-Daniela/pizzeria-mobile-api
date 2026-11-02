from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models import Producto
from app.schemas.producto import ProductoOut
from app.models import Pedido, PedidoItem, PedidoItemExtra, Producto, Ingrediente, Cliente
from app.models.catalogo import Categoria
from app.api.deps import get_db, get_current_empleado
from pydantic import BaseModel
from typing import List

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

@router.get("/ingredientes", response_model=list[dict]) # Usamos dict rápido para simplificar
async def listar_ingredientes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ingrediente).where(Ingrediente.disponible == True))
    ingredientes = result.scalars().all()
    return [{"id": str(i.id), "nombre": i.nombre, "precio_extra": float(i.precio_extra)} for i in ingredientes]

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
    ingredientes: List[UUID] = []

@router.post("", response_model=ProductoOut, status_code=201)
async def crear_producto(data: ProductoCreate, db: AsyncSession = Depends(get_db), _emp = Depends(get_current_empleado)):
    # 1. Verificamos la categoría
    cat_id = data.categoria_id
    cat_result = await db.execute(select(Categoria).where(Categoria.id == data.categoria_id))
    if not cat_result.scalar_one_or_none():
        fallback_cat = await db.execute(select(Categoria).where(Categoria.nombre == "Pizzas"))
        cat = fallback_cat.scalar_one_or_none()
        if cat:
            cat_id = cat.id
        else:
            raise HTTPException(400, "La categoría especificada no existe")

    # 2. Creamos el producto (excluyendo los ingredientes del diccionario)
    prod_data = data.model_dump(exclude={"ingredientes"})
    prod_data["categoria_id"] = cat_id # Aseguramos que use el ID correcto
    nuevo = Producto(**prod_data)
    
    # 3. Asignamos los ingredientes seleccionados
    if data.ingredientes:
        ing_result = await db.execute(select(Ingrediente).where(Ingrediente.id.in_(data.ingredientes)))
        nuevo.ingredientes = list(ing_result.scalars().all())
    
    # 4. Guardamos
    db.add(nuevo)
    await db.commit()
    
    # 5. Devolvemos el producto con sus ingredientes cargados
    stmt = select(Producto).options(selectinload(Producto.ingredientes)).where(Producto.id == nuevo.id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def actualizar_producto(producto_id: UUID, data: ProductoCreate, db: AsyncSession = Depends(get_db), _emp = Depends(get_current_empleado)):
    stmt = select(Producto).options(selectinload(Producto.ingredientes)).where(Producto.id == producto_id)
    result = await db.execute(stmt)
    prod = result.scalar_one_or_none()
    
    if not prod: 
        raise HTTPException(404, "No encontrado")
    
    # Actualizar campos básicos
    for key, value in data.model_dump(exclude={"ingredientes"}).items():
        setattr(prod, key, value)
        
    # Actualizar ingredientes (ya están en memoria, así que no hay error)
    if data.ingredientes is not None:
        ing_result = await db.execute(select(Ingrediente).where(Ingrediente.id.in_(data.ingredientes)))
        prod.ingredientes = list(ing_result.scalars().all())
    
    # Guardamos los cambios
    await db.commit()
    
    # Refrescamos el objeto para devolverlo con los datos actualizados
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

