from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime

from app.models.enums import TipoPedido
from app.models.enums import EstadoPedido


class ClienteInput(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    telefono: str = Field(..., min_length=7, max_length=30)
    direccion: str | None = Field(None, max_length=500)


class PedidoItemExtraInput(BaseModel):
    ingrediente_id: UUID


class PedidoItemInput(BaseModel):
    producto_id: UUID
    cantidad: int = Field(..., ge=1, le=50)
    notas: str | None = Field(None, max_length=500)
    extras: list[PedidoItemExtraInput] = Field(default_factory=list)


class PedidoCreate(BaseModel):
    tipo: TipoPedido
    cliente: ClienteInput | None = None
    mesa_id: UUID | None = None
    notas: str | None = Field(None, max_length=1000)
    items: list[PedidoItemInput] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validar_por_tipo(self) -> "PedidoCreate":
        if self.tipo == TipoPedido.DOMICILIO:
            if not self.cliente:
                raise ValueError("Pedido a domicilio requiere datos del cliente")
            if not self.cliente.telefono:
                raise ValueError("Pedido a domicilio requiere teléfono")
            if not self.cliente.direccion:
                raise ValueError("Pedido a domicilio requiere dirección")
        if self.tipo == TipoPedido.LOCAL and not self.mesa_id:
            raise ValueError("Pedido en local requiere mesa_id")
        return self


class PedidoItemExtraOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ingrediente_id: UUID
    precio_extra: float


class PedidoItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    producto_id: UUID
    cantidad: int
    precio_unitario: float
    notas: str | None
    extras: list[PedidoItemExtraOut]


class PedidoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo: str
    tipo: TipoPedido
    estado: str
    total: float
    items: list[PedidoItemOut]
    

class PedidoEstadoUpdate(BaseModel):
    nuevo_estado: EstadoPedido

class PedidoTrackingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    codigo: str
    estado: EstadoPedido
    total: float
    created_at: datetime