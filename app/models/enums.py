import enum


class RolEmpleado(str, enum.Enum):
    ADMIN = "ADMIN"
    CAJERO = "CAJERO"
    COCINERO = "COCINERO"
    REPARTIDOR = "REPARTIDOR"


class TipoPedido(str, enum.Enum):
    LOCAL = "LOCAL"
    DOMICILIO = "DOMICILIO"
    RECOGER = "RECOGER"


class EstadoPedido(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PREPARACION = "EN_PREPARACION"
    LISTA = "LISTA"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADA = "ENTREGADA"
    CANCELADA = "CANCELADA"


class EstadoMesa(str, enum.Enum):
    LIBRE = "LIBRE"
    OCUPADA = "OCUPADA"
    RESERVADA = "RESERVADA"


class MetodoPago(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    TRANSFERENCIA = "TRANSFERENCIA"
    PAGO_MOVIL = "PAGO_MOVIL"


class EstadoPago(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PAGADO = "PAGADO"
    FALLIDO = "FALLIDO"
    REEMBOLSADO = "REEMBOLSADO"