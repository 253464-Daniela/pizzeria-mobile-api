import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.models.enums import EstadoMesa


class Mesa(Base):
    __tablename__ = "mesas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    numero: Mapped[int] = mapped_column(Integer, unique=True)
    estado: Mapped[EstadoMesa] = mapped_column(
        SAEnum(EstadoMesa, name="estado_mesa"), default=EstadoMesa.LIBRE
    )
    qr_token: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )