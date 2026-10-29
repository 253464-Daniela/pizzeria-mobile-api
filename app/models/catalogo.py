from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
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


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    productos: Mapped[list[Producto]] = relationship(back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(150))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    imagen_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    categoria: Mapped[Categoria] = relationship(back_populates="productos")
    ingredientes: Mapped[list[Ingrediente]] = relationship(
        secondary="producto_ingredientes", back_populates="productos"
    )


class Ingrediente(Base):
    __tablename__ = "ingredientes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    precio_extra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)

    productos: Mapped[list[Producto]] = relationship(
        secondary="producto_ingredientes", back_populates="ingredientes"
    )


class ProductoIngrediente(Base):
    __tablename__ = "producto_ingredientes"

    producto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("productos.id", ondelete="CASCADE"), primary_key=True
    )
    ingrediente_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ingredientes.id", ondelete="CASCADE"), primary_key=True
    )