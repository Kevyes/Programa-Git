"""Dependencias de seguridad: usuario autenticado (JWT) y control de roles (RBAC)."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models import Rol, Usuario

_bearer = HTTPBearer(auto_error=False)


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    no_autorizado = HTTPException(status.HTTP_401_UNAUTHORIZED, "Token ausente, inválido o vencido")
    if credenciales is None:
        raise no_autorizado
    try:
        payload = decode_token(credenciales.credentials)
        usuario = db.get(Usuario, int(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise no_autorizado
    if usuario is None or not usuario.activo:
        raise no_autorizado
    return usuario


def requiere_roles(*roles: Rol):
    """Fábrica de dependencias RBAC: @router.get(..., dependencies=[Depends(requiere_roles(Rol.ADMIN))])"""

    def verificador(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permisos para esta operación")
        return usuario

    return verificador
