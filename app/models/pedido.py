from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.models.enums import EstadoPedido, TipoPedido

if TYPE_CHECKING:
    from app.models.cliente import Cliente
    from app.models.empleado import Empleado
    from app.models.mesa import Mesa
    from app.models.pago import Pago


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    cliente_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("clientes.id", ondelete="SET NULL"), nullable=True
    )
    empleado_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True
    )
    mesa_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("mesas.id", ondelete="SET NULL"), nullable=True
    )
    tipo: Mapped[TipoPedido] = mapped_column(SAEnum(TipoPedido, name="tipo_pedido"))
    estado: Mapped[EstadoPedido] = mapped_column(
        SAEnum(EstadoPedido, name="estado_pedido"),
        default=EstadoPedido.PENDIENTE,
        index=True,
    )
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    cliente: Mapped[Cliente | None] = relationship()
    empleado: Mapped[Empleado | None] = relationship(back_populates="pedidos")
    mesa: Mapped[Mesa | None] = relationship()
    items: Mapped[list[PedidoItem]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )
    pagos: Mapped[list[Pago]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class PedidoItem(Base):
    __tablename__ = "pedido_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    pedido_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pedidos.id", ondelete="CASCADE"), index=True
    )
    producto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("productos.id", ondelete="RESTRICT")
    )
    cantidad: Mapped[int] = mapped_column(Integer)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    pedido: Mapped[Pedido] = relationship(back_populates="items")
    extras: Mapped[list[PedidoItemExtra]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )


class PedidoItemExtra(Base):
    __tablename__ = "pedido_item_extras"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    pedido_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pedido_items.id", ondelete="CASCADE"), index=True
    )
    ingrediente_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ingredientes.id", ondelete="RESTRICT")
    )
    precio_extra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    item: Mapped[PedidoItem] = relationship(back_populates="extras")