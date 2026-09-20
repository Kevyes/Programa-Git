from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.schemas import LoginIn, RegistroIn, TokenOut, UsuarioOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, db: Session = Depends(get_db)):
    return auth_service.autenticar(db, datos.email, datos.password)


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    return auth_service.registrar_cliente(db, datos)
