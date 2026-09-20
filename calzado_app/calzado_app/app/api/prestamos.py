from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.core.database import get_db
from app.models import Rol, Usuario
from app.schemas.schemas import LiquidarIn, LiquidarOut, PrestamoCrearIn, PrestamoOut
from app.services import prestamo_service

router = APIRouter(prefix="/prestamos", tags=["Calzado en prueba (POS)"])
_pos_o_admin = requiere_roles(Rol.EMPLEADO_POS, Rol.ADMIN)
_solo_pos = requiere_roles(Rol.EMPLEADO_POS)


@router.post("", response_model=list[PrestamoOut], status_code=status.HTTP_201_CREATED)
def registrar_salida(datos: PrestamoCrearIn, db: Session = Depends(get_db), empleado: Usuario = Depends(_solo_pos)):
    """RF01/RF02: salida temporal de uno o varios pares."""
    return prestamo_service.registrar_salida(db, empleado, datos.codigo_empleado, datos.items)


@router.get("", response_model=list[PrestamoOut])
def mis_prestamos(activos: bool = True, db: Session = Depends(get_db), usuario: Usuario = Depends(_pos_o_admin)):
    return prestamo_service.listar(db, usuario, solo_activos=activos)


@router.post("/{prestamo_id}/liquidar", response_model=LiquidarOut)
def liquidar(prestamo_id: int, datos: LiquidarIn, db: Session = Depends(get_db), usuario: Usuario = Depends(_pos_o_admin)):
    """RF03: devolver al estante o facturar."""
    prestamo, venta = prestamo_service.liquidar(db, usuario, prestamo_id, datos.accion)
    return LiquidarOut(prestamo=prestamo, venta=venta)
