from uuid import UUID
from pydantic import BaseModel, ConfigDict

class IngredienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str
    precio_extra: float

class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    categoria_id: UUID
    nombre: str
    descripcion: str | None
    precio: float
    imagen_url: str | None
    disponible: bool
    ingredientes: list[IngredienteOut] = []