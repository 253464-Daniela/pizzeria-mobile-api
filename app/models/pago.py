from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.models.enums import EstadoPago, MetodoPago

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    pedido_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pedidos.id", ondelete="CASCADE"), index=True
    )
    metodo: Mapped[MetodoPago] = mapped_column(SAEnum(MetodoPago, name="metodo_pago"))
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    estado: Mapped[EstadoPago] = mapped_column(
        SAEnum(EstadoPago, name="estado_pago"), default=EstadoPago.PENDIENTE
    )
    referencia: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    pedido: Mapped[Pedido] = relationship(back_populates="pagos")