"""Módulo de calzado en prueba (RF01, RF02, RF03)."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NoEncontradoError, PermisoError, ReglaNegocioError
from app.models import Canal, DetalleVenta, EstadoPrestamo, PrestamoTemporal, Rol, Usuario, Venta
from app.schemas.schemas import ItemIn
from app.services import inventario_service as inventario


def registrar_salida(db: Session, empleado: Usuario, codigo_empleado: str, items: list[ItemIn]) -> list[PrestamoTemporal]:
    """RF01 + RF02: retira pares del estante y los congela en 'stock en prueba'.

    Todo ocurre en UNA transacción: si un solo ítem falla, ninguno se registra.
    """
    if empleado.codigo_empleado != codigo_empleado:
        raise ReglaNegocioError("El código de empleado no corresponde al usuario autenticado")
    prestamos: list[PrestamoTemporal] = []
    try:
        for item in items:
            inventario.mover_a_prueba(db, item.producto_id, item.cantidad)
            prestamo = PrestamoTemporal(
                producto_id=item.producto_id, empleado_id=empleado.id, cantidad=item.cantidad
            )
            db.add(prestamo)
            prestamos.append(prestamo)
        db.commit()
        for prestamo in prestamos:  # el UPDATE atómico no toca el objeto en memoria: lo releemos
            db.refresh(prestamo.producto)
    except Exception:
        db.rollback()
        raise
    return prestamos


def listar(db: Session, usuario: Usuario, solo_activos: bool = True) -> list[PrestamoTemporal]:
    consulta = select(PrestamoTemporal)
    if usuario.rol != Rol.ADMIN:
        consulta = consulta.where(PrestamoTemporal.empleado_id == usuario.id)
    if solo_activos:
        consulta = consulta.where(PrestamoTemporal.asignacion_activa.is_(True))
    return list(db.scalars(consulta.order_by(PrestamoTemporal.fecha_hora_salida.desc())).unique())


def liquidar(db: Session, usuario: Usuario, prestamo_id: int, accion: str) -> tuple[PrestamoTemporal, Optional[Venta]]:
    """RF03: devuelve el par al estante o lo factura; sella la fecha/hora y libera al empleado."""
    try:
        prestamo = db.scalars(
            select(PrestamoTemporal).where(PrestamoTemporal.id == prestamo_id).with_for_update(of=PrestamoTemporal)
        ).unique().first()
        if prestamo is None:
            raise NoEncontradoError("El préstamo no existe")
        if prestamo.empleado_id != usuario.id and usuario.rol != Rol.ADMIN:
            raise PermisoError("Este préstamo pertenece a otro empleado")
        if prestamo.estado != EstadoPrestamo.EN_PRUEBA:
            raise ReglaNegocioError("Este préstamo ya fue liquidado")

        venta = None
        if accion == "DEVOLVER":
            inventario.devolver_a_estante(db, prestamo.producto_id, prestamo.cantidad)
            prestamo.estado = EstadoPrestamo.DEVUELTO
        else:  # VENDER
            inventario.consumir_en_prueba(db, prestamo.producto_id, prestamo.cantidad)
            precio = prestamo.producto.precio
            venta = Venta(
                numero_factura=f"FAC-{uuid.uuid4().hex[:10].upper()}",
                usuario_id=prestamo.empleado_id, canal=Canal.POS, total=precio * prestamo.cantidad,
            )
            venta.detalles.append(
                DetalleVenta(producto_id=prestamo.producto_id, cantidad=prestamo.cantidad, precio_unitario=precio)
            )
            db.add(venta)
            prestamo.estado = EstadoPrestamo.VENDIDO

        prestamo.asignacion_activa = False
        prestamo.fecha_hora_retorno = datetime.now(timezone.utc)
        db.commit()
        db.refresh(prestamo.producto)
        return prestamo, venta
    except Exception:
        db.rollback()
        raise
