from fastapi import APIRouter
from app.api.v1 import auth, categorias, productos, pedidos, empleados

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(categorias.router)
api_router.include_router(productos.router)
api_router.include_router(pedidos.router)
api_router.include_router(empleados.router)