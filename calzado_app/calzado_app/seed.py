"""Carga datos de ejemplo. Uso:  python seed.py   (es seguro ejecutarlo varias veces)."""
from sqlalchemy import select

from app import models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Producto, Rol, Usuario

USUARIOS = [
    ("Administrador", "admin@calzado.com", "Admin12345", Rol.ADMIN, None),
    ("Carlos Vendedor", "pos1@calzado.com", "Pos12345", Rol.EMPLEADO_POS, "EMP001"),
    ("Laura Vendedora", "pos2@calzado.com", "Pos12345", Rol.EMPLEADO_POS, "EMP002"),
    ("Cliente Demo", "cliente@calzado.com", "Cliente12345", Rol.CLIENTE, None),
]

PRODUCTOS = [
    ("Nike", "Air Max", "Negro", 40, 389900, 10), ("Nike", "Air Max", "Negro", 41, 389900, 8),
    ("Nike", "Air Max", "Blanco", 39, 389900, 5), ("Adidas", "Superstar", "Blanco", 38, 329900, 12),
    ("Adidas", "Superstar", "Blanco", 40, 329900, 7), ("Puma", "Suede", "Azul", 42, 299900, 6),
    ("Puma", "Suede", "Rojo", 41, 299900, 0), ("Converse", "Chuck Taylor", "Negro", 39, 219900, 15),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for nombre, email, clave, rol, codigo in USUARIOS:
            if not db.scalar(select(Usuario).where(Usuario.email == email)):
                db.add(Usuario(nombre=nombre, email=email, password_hash=hash_password(clave), rol=rol, codigo_empleado=codigo))
        if not db.scalar(select(Producto)):
            for marca, modelo, color, talla, precio, stock in PRODUCTOS:
                db.add(Producto(marca=marca, modelo=modelo, color=color, talla=talla, precio=precio, stock_disponible=stock))
        db.commit()
    print("Datos de ejemplo cargados.")


if __name__ == "__main__":
    main()
