from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CategoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str
    orden: int
