from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Producto
from app.schemas.schemas import ProductoIn
from app.services.inventario_service import obtener_producto


def listar_catalogo(
    db: Session,
    talla: Optional[int] = None,
    marca: Optional[str] = None,
    color: Optional[str] = None,
    modelo: Optional[str] = None,
    solo_disponibles: bool = True,
) -> list[Producto]:
    """Catálogo filtrable (RF04). Por defecto solo muestra stock > 0 (HU03)."""
    consulta = select(Producto)
    if solo_disponibles:
        consulta = consulta.where(Producto.stock_disponible > 0)
    if talla is not None:
        consulta = consulta.where(Producto.talla == talla)
    if marca:
        consulta = consulta.where(Producto.marca.ilike(f"%{marca}%"))
    if color:
        consulta = consulta.where(Producto.color.ilike(f"%{color}%"))
    if modelo:
        consulta = consulta.where(Producto.modelo.ilike(f"%{modelo}%"))
    return list(db.scalars(consulta.order_by(Producto.marca, Producto.modelo, Producto.talla)))


def crear_producto(db: Session, datos: ProductoIn) -> Producto:
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    return producto


def actualizar_producto(db: Session, producto_id: int, datos: ProductoIn) -> Producto:
    producto = obtener_producto(db, producto_id)
    for campo, valor in datos.model_dump().items():
        setattr(producto, campo, valor)
    db.commit()
    return producto
