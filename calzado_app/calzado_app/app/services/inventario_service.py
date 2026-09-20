"""Operaciones atómicas sobre los estados de stock (RF02, RNF01).

Cada función hace UN UPDATE condicionado. Si la condición no se cumple (por ejemplo
otro cliente compró el último par un instante antes) no se modifica ninguna fila y
se lanza ReglaNegocioError, sin importar cuántas peticiones lleguen en paralelo.
"""
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.exceptions import NoEncontradoError, ReglaNegocioError
from app.models import Producto


def obtener_producto(db: Session, producto_id: int) -> Producto:
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise NoEncontradoError(f"El producto {producto_id} no existe")
    return producto


def _ejecutar(db: Session, condiciones: list, valores: dict, mensaje: str) -> None:
    sentencia = update(Producto).where(*condiciones).values(**valores)
    resultado = db.execute(sentencia.execution_options(synchronize_session=False))
    if resultado.rowcount == 0:
        raise ReglaNegocioError(mensaje)


def mover_a_prueba(db: Session, producto_id: int, cantidad: int) -> None:
    """stockDisponible -> stockEnPrueba."""
    obtener_producto(db, producto_id)
    _ejecutar(
        db,
        [Producto.id == producto_id, Producto.stock_disponible >= cantidad],
        {
            "stock_disponible": Producto.stock_disponible - cantidad,
            "stock_en_prueba": Producto.stock_en_prueba + cantidad,
        },
        f"Stock disponible insuficiente para el producto {producto_id}",
    )


def devolver_a_estante(db: Session, producto_id: int, cantidad: int) -> None:
    """stockEnPrueba -> stockDisponible."""
    _ejecutar(
        db,
        [Producto.id == producto_id, Producto.stock_en_prueba >= cantidad],
        {
            "stock_en_prueba": Producto.stock_en_prueba - cantidad,
            "stock_disponible": Producto.stock_disponible + cantidad,
        },
        "Inconsistencia: no hay suficiente stock en prueba para devolver",
    )


def consumir_en_prueba(db: Session, producto_id: int, cantidad: int) -> None:
    """Venta presencial: el par sale definitivamente del stock en prueba."""
    _ejecutar(
        db,
        [Producto.id == producto_id, Producto.stock_en_prueba >= cantidad],
        {"stock_en_prueba": Producto.stock_en_prueba - cantidad},
        "Inconsistencia: no hay suficiente stock en prueba para vender",
    )


def descontar_disponible(db: Session, producto_id: int, cantidad: int) -> None:
    """Venta web: stockDisponible baja directamente."""
    obtener_producto(db, producto_id)
    _ejecutar(
        db,
        [Producto.id == producto_id, Producto.stock_disponible >= cantidad],
        {"stock_disponible": Producto.stock_disponible - cantidad},
        f"Stock insuficiente para el producto {producto_id}",
    )
