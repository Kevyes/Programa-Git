"""Reportes de auditoría de retiradas temporales (RF05)."""
import csv
import io
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PrestamoTemporal, Producto, Usuario
from app.schemas.schemas import AuditoriaOut


def consultar(
    db: Session,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    empleado_id: Optional[int] = None,
) -> list[AuditoriaOut]:
    consulta = (
        select(PrestamoTemporal, Usuario, Producto)
        .join(Usuario, PrestamoTemporal.empleado_id == Usuario.id)
        .join(Producto, PrestamoTemporal.producto_id == Producto.id)
    )
    if desde:
        consulta = consulta.where(PrestamoTemporal.fecha_hora_salida >= desde)
    if hasta:
        consulta = consulta.where(PrestamoTemporal.fecha_hora_salida <= hasta)
    if empleado_id:
        consulta = consulta.where(PrestamoTemporal.empleado_id == empleado_id)
    consulta = consulta.order_by(PrestamoTemporal.fecha_hora_salida.desc())

    filas = []
    for prestamo, empleado, producto in db.execute(consulta).unique():
        filas.append(AuditoriaOut(
            id=prestamo.id, empleado_id=empleado.id, empleado_nombre=empleado.nombre,
            codigo_empleado=empleado.codigo_empleado,
            producto=f"{producto.marca} {producto.modelo} {producto.color} T{producto.talla}",
            cantidad=prestamo.cantidad, estado=prestamo.estado,
            fecha_hora_salida=prestamo.fecha_hora_salida, fecha_hora_retorno=prestamo.fecha_hora_retorno,
        ))
    return filas


def exportar_csv(filas: list[AuditoriaOut]) -> str:
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["ID", "Empleado", "Codigo", "Producto", "Cantidad", "Estado", "Salida (UTC)", "Retorno (UTC)"])
    for f in filas:
        escritor.writerow([
            f.id, f.empleado_nombre, f.codigo_empleado, f.producto, f.cantidad, f.estado.value,
            f.fecha_hora_salida.isoformat(), f.fecha_hora_retorno.isoformat() if f.fecha_hora_retorno else "",
        ])
    return salida.getvalue()
