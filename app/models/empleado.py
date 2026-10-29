from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.db.types import CIText
from app.models.enums import RolEmpleado

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(CIText, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[RolEmpleado] = mapped_column(
        SAEnum(RolEmpleado, name="rol_empleado", native_enum=True),
        default=RolEmpleado.CAJERO,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    pedidos: Mapped[list[Pedido]] = relationship(back_populates="empleado")