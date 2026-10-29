import asyncio
from decimal import Decimal
from sqlalchemy import select
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models import Empleado, Categoria, Producto, Ingrediente
from app.models.enums import RolEmpleado

async def main():
    async with AsyncSessionLocal() as db:
        # 1. Admin
        result = await db.execute(select(Empleado).where(Empleado.email == "admin@pizzeria.com"))
        if not result.scalar_one_or_none():
            admin = Empleado(
                nombre="Admin", email="admin@pizzeria.com",
                password_hash=hash_password("admin123"), rol=RolEmpleado.ADMIN,
            )
            db.add(admin)
            print("Admin creado.")

        # 2. Categorías
        cat_pizzas = Categoria(nombre="Pizzas", orden=1)
        cat_bebidas = Categoria(nombre="Bebidas", orden=2)
        db.add_all([cat_pizzas, cat_bebidas])
        await db.flush() # Para obtener los IDs

        # 3. Ingredientes
        ing_queso = Ingrediente(nombre="Queso Extra", precio_extra=Decimal("1.50"))
        ing_pepperoni = Ingrediente(nombre="Pepperoni Extra", precio_extra=Decimal("2.00"))
        ing_champinon = Ingrediente(nombre="Champiñones", precio_extra=Decimal("1.00"))
        db.add_all([ing_queso, ing_pepperoni, ing_champinon])
        await db.flush()

        # 4. Productos (Pizzas)
        pizza_margarita = Producto(
            categoria_id=cat_pizzas.id, nombre="Pizza Margarita", 
            precio=Decimal("8.00"), descripcion="Salsa de tomate y mozzarella"
        )
        pizza_pepperoni = Producto(
            categoria_id=cat_pizzas.id, nombre="Pizza Pepperoni", 
            precio=Decimal("10.00"), descripcion="Mozzarella y pepperoni"
        )
        
        # Asignar ingredientes opcionales a las pizzas
        pizza_margarita.ingredientes.extend([ing_queso, ing_champinon])
        pizza_pepperoni.ingredientes.extend([ing_queso, ing_pepperoni])

        # 5. Productos (Bebidas)
        coca_cola = Producto(
            categoria_id=cat_bebidas.id, nombre="Coca-Cola 500ml", 
            precio=Decimal("2.50"), descripcion="Bien fría"
        )

        db.add_all([pizza_margarita, pizza_pepperoni, coca_cola])
        await db.commit()
        print("Menú de ejemplo cargado con éxito.")

if __name__ == "__main__":
    asyncio.run(main())