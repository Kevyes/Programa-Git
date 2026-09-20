from app.models.enums import Canal, EstadoPrestamo, Rol
from app.models.prestamo import PrestamoTemporal
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.models.venta import DetalleVenta, Venta

__all__ = [
    "Canal", "EstadoPrestamo", "Rol",
    "PrestamoTemporal", "Producto", "Usuario", "DetalleVenta", "Venta",
]
