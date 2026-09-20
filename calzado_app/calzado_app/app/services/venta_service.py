"""Tienda virtual: venta web (RF04)."""
import uuid
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Canal, DetalleVenta, Usuario, Venta
from app.schemas.schemas import ItemIn
from app.services import inventario_service as inventario


def procesar_venta_web(db: Session, cliente: Usuario, items: list[ItemIn]) -> Venta:
    # Une líneas repetidas del mismo producto.
    cantidades: dict[int, int] = defaultdict(int)
    for item in items:
        cantidades[item.producto_id] += item.cantidad

    try:
        venta = Venta(
            numero_factura=f"FAC-{uuid.uuid4().hex[:10].upper()}",
            usuario_id=cliente.id, canal=Canal.WEB, total=0,
        )
        for producto_id, cantidad in cantidades.items():
            producto = inventario.obtener_producto(db, producto_id)
            inventario.descontar_disponible(db, producto_id, cantidad)  # atómico (RNF01)
            venta.detalles.append(
                DetalleVenta(producto_id=producto_id, cantidad=cantidad, precio_unitario=producto.precio)
            )
            venta.total += producto.precio * cantidad
        # Aquí se integraría la pasarela de pago (PSE, tarjeta...). Se simula como aprobado.
        db.add(venta)
        db.commit()
        return venta
    except Exception:
        db.rollback()
        raise
