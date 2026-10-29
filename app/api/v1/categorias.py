from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models import Categoria
from app.schemas.categoria import CategoriaOut

router = APIRouter(prefix="/categorias", tags=["catálogo"])

@router.get("", response_model=list[CategoriaOut])
async def listar_categorias(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Categoria).order_by(Categoria.orden))
    return result.scalars().all()