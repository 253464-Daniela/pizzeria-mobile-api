import random
import string
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_empleado
from app.models import Pedido, PedidoItem, PedidoItemExtra, Producto, Ingrediente, Cliente
from app.models.enums import EstadoPedido, RolEmpleado
from app.schemas.pedido import PedidoCreate, PedidoOut, PedidoEstadoUpdate, PedidoTrackingOut

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

def generar_codigo():
    letras = string.ascii_uppercase
    return "P-" + "".join(random.choices(letras, k=2)) + str(random.randint(100, 999))

# Matriz de transiciones: qué estados puede alcanzar cada estado actual
TRANSICIONES = {
    EstadoPedido.PENDIENTE: [EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADA],
    EstadoPedido.EN_PREPARACION: [EstadoPedido.LISTA, EstadoPedido.CANCELADA],
    EstadoPedido.LISTA: [EstadoPedido.EN_CAMINO, EstadoPedido.ENTREGADA],
    EstadoPedido.EN_CAMINO: [EstadoPedido.ENTREGADA],
}

# Roles permitidos por transición
ROLES_POR_ESTADO = {
    EstadoPedido.EN_PREPARACION: [RolEmpleado.ADMIN, RolEmpleado.COCINERO],
    EstadoPedido.LISTA: [RolEmpleado.ADMIN, RolEmpleado.COCINERO],
    EstadoPedido.EN_CAMINO: [RolEmpleado.ADMIN, RolEmpleado.REPARTIDOR],
    EstadoPedido.ENTREGADA: [RolEmpleado.ADMIN, RolEmpleado.REPARTIDOR, RolEmpleado.CAJERO],
    EstadoPedido.CANCELADA: [RolEmpleado.ADMIN, RolEmpleado.CAJERO],
}

@router.post("", response_model=PedidoOut, status_code=201)
async def crear_pedido(data: PedidoCreate, db: AsyncSession = Depends(get_db)):
    # 1. Manejo del Cliente (si es domicilio, ya validamos en el schema que exista)
    cliente_id = None
    if data.tipo == "DOMICILIO" and data.cliente:
        nuevo_cliente = Cliente(
            nombre=data.cliente.nombre, telefono=data.cliente.telefono, direccion=data.cliente.direccion
        )
        db.add(nuevo_cliente)
        await db.flush()
        cliente_id = nuevo_cliente.id

    # 2. Crear el pedido base
    pedido = Pedido(
        codigo=generar_codigo(),
        tipo=data.tipo,
        cliente_id=cliente_id,
        mesa_id=data.mesa_id,
        notas=data.notas,
        total=0
    )
    db.add(pedido)
    await db.flush() # Para obtener el pedido.id

    total_pedido = 0

    # 3. Procesar items (El servidor NUNCA confía en precios del cliente)
    for item_in in data.items:
        # Buscar producto
        prod_res = await db.execute(select(Producto).where(Producto.id == item_in.producto_id, Producto.disponible == True))
        producto = prod_res.scalar_one_or_none()
        if not producto:
            raise HTTPException(400, f"Producto no disponible o no existe")

        item_total = producto.precio * item_in.cantidad
        
        # Crear item
        nuevo_item = PedidoItem(
            pedido_id=pedido.id, producto_id=producto.id,
            cantidad=item_in.cantidad, precio_unitario=producto.precio, notas=item_in.notas
        )
        db.add(nuevo_item)
        await db.flush()

        # Procesar extras
        for extra in item_in.extras:
            ing_res = await db.execute(select(Ingrediente).where(Ingrediente.id == extra.ingrediente_id))
            ing = ing_res.scalar_one_or_none()
            if ing:
                item_total += ing.precio_extra * item_in.cantidad
                db.add(PedidoItemExtra(
                    pedido_item_id=nuevo_item.id, ingrediente_id=ing.id, precio_extra=ing.precio_extra
                ))

        total_pedido += item_total

    # 4. Actualizar el total final
    pedido.total = total_pedido # type: ignore
    await db.commit()

    # Refrescar para cargar relaciones y devolver
    return await obtener_pedido_por_id(pedido.id, db)

@router.get("/{codigo}", response_model=PedidoTrackingOut)
async def trackear_pedido(codigo: str, db: AsyncSession = Depends(get_db)):
    """Endpoint PÚBLICO para que el cliente vea cómo va su pedido sin login."""
    stmt = select(Pedido).where(Pedido.codigo == codigo)
    res = await db.execute(stmt)
    pedido = res.scalar_one_or_none()
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    return pedido

@router.patch("/{pedido_id}/estado", response_model=PedidoOut)
async def actualizar_estado(
    pedido_id: UUID, 
    data: PedidoEstadoUpdate, 
    db: AsyncSession = Depends(get_db), 
    empleado = Depends(get_current_empleado)
):
    stmt = select(Pedido).where(Pedido.id == pedido_id)
    res = await db.execute(stmt)
    pedido = res.scalar_one_or_none()
    
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    # Validar rol
    roles_validos = ROLES_POR_ESTADO.get(data.nuevo_estado, [])
    if empleado.rol not in roles_validos:
        raise HTTPException(403, f"Tu rol ({empleado.rol.value}) no puede pasar a {data.nuevo_estado.value}")

    # Validar transición
    if data.nuevo_estado not in TRANSICIONES.get(pedido.estado, []):
        raise HTTPException(400, f"No se puede saltar de {pedido.estado.value} a {data.nuevo_estado.value}")

    pedido.estado = data.nuevo_estado
    pedido.empleado_id = empleado.id # Rastrear quién hizo el cambio
    await db.commit()
    
    return await obtener_pedido_por_id(pedido.id, db)

@router.get("", response_model=list[PedidoOut])
async def listar_pedidos(
    estado: EstadoPedido | None = None,
    db: AsyncSession = Depends(get_db),
    _empleado = Depends(get_current_empleado) # Protegido, requiere estar logueado
):
    """Endpoint PRIVADO para que los empleados vean la cola de pedidos."""
    stmt = (
        select(Pedido)
        .options(selectinload(Pedido.items).selectinload(PedidoItem.extras))
        .order_by(Pedido.created_at.desc())
    )
    
    if estado:
        stmt = stmt.where(Pedido.estado == estado)
        
    res = await db.execute(stmt)
    return res.scalars().all()

# Función auxiliar para cargar las relaciones (items y extras)
async def obtener_pedido_por_id(pedido_id: UUID, db: AsyncSession):
    stmt = (
        select(Pedido)
        .options(selectinload(Pedido.items).selectinload(PedidoItem.extras))
        .where(Pedido.id == pedido_id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()