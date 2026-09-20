from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.core.database import get_db
from app.models import Rol, Usuario
from app.schemas.schemas import UsuarioCrearIn, UsuarioOut
from app.services import auth_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios (solo ADMIN)"], dependencies=[Depends(requiere_roles(Rol.ADMIN))])


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCrearIn, db: Session = Depends(get_db)):
    return auth_service.crear_usuario_admin(db, datos)


@router.get("/empleados", response_model=list[UsuarioOut])
def listar_empleados(db: Session = Depends(get_db)):
    return list(db.scalars(select(Usuario).where(Usuario.rol == Rol.EMPLEADO_POS).order_by(Usuario.nombre)))
