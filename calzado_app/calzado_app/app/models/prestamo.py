from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, event, inspect
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoPrestamo
from app.models.producto import Producto
from app.models.usuario import Usuario


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class PrestamoTemporal(Base):
    """Calzado retirado del estante por un empleado para que el cliente se lo pruebe."""

    __tablename__ = "prestamos_temporales"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), index=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    cantidad: Mapped[int]
    estado: Mapped[EstadoPrestamo] = mapped_column(
        Enum(EstadoPrestamo, native_enum=False, length=20), default=EstadoPrestamo.EN_PRUEBA
    )
    # True mientras el par siga "a cargo" del empleado. Al liquidar pasa a False (RF03).
    # Se conserva empleado_id para que la auditoría (RF05) siempre sepa quién lo retiró.
    asignacion_activa: Mapped[bool] = mapped_column(default=True)
    fecha_hora_salida: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)
    fecha_hora_retorno: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    producto: Mapped[Producto] = relationship(lazy="joined", innerjoin=True)
    empleado: Mapped[Usuario] = relationship(lazy="joined", innerjoin=True)


@event.listens_for(PrestamoTemporal, "before_update")
def _proteger_marcas_de_tiempo(mapper, connection, target):
    """Inmutabilidad de sellos de tiempo (sección de seguridad del documento).

    - fecha_hora_salida nunca puede modificarse después de creada.
    - fecha_hora_retorno solo puede escribirse una vez (de NULL a un valor).
    """
    estado = inspect(target)
    salida = estado.attrs.fecha_hora_salida.history
    if salida.has_changes() and salida.deleted:
        raise ValueError("fecha_hora_salida es inmutable")
    retorno = estado.attrs.fecha_hora_retorno.history
    if retorno.has_changes() and any(v is not None for v in retorno.deleted):
        raise ValueError("fecha_hora_retorno es inmutable una vez registrada")
