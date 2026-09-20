from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.core.database import get_db
from app.models import Rol, Usuario
from app.schemas.schemas import VentaOut, VentaWebIn
from app.services import venta_service

router = APIRouter(prefix="/ventas", tags=["Tienda virtual"])


@router.post("/web", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def comprar(datos: VentaWebIn, db: Session = Depends(get_db), cliente: Usuario = Depends(requiere_roles(Rol.CLIENTE))):
    return venta_service.procesar_venta_web(db, cliente, datos.items)
