from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import RolEmpleado

class EmpleadoCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., max_length=120)
    password: str = Field(..., min_length=6, max_length=72)
    rol: RolEmpleado

class EmpleadoUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=120)
    rol: RolEmpleado | None = None
    activo: bool | None = None