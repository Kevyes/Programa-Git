from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ReglaNegocioError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Rol, Usuario
from app.schemas.schemas import RegistroIn, TokenOut, UsuarioCrearIn


def autenticar(db: Session, email: str, password: str) -> TokenOut:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.lower().strip()))
    # Mismo mensaje si el correo no existe o la clave falla: no revela qué cuentas existen.
    if usuario is None or not usuario.activo or not verify_password(password, usuario.password_hash):
        raise ReglaNegocioError("Credenciales inválidas")
    token = create_access_token(usuario.id, usuario.rol.value)
    return TokenOut(access_token=token, rol=usuario.rol.value, nombre=usuario.nombre)


def _crear(db: Session, datos: RegistroIn, rol: Rol, codigo_empleado=None) -> Usuario:
    email = datos.email.lower().strip()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise ReglaNegocioError("Ya existe un usuario con ese correo")
    if codigo_empleado and db.scalar(select(Usuario).where(Usuario.codigo_empleado == codigo_empleado)):
        raise ReglaNegocioError("Ya existe un empleado con ese código")
    usuario = Usuario(
        nombre=datos.nombre, email=email, password_hash=hash_password(datos.password),
        rol=rol, codigo_empleado=codigo_empleado,
    )
    db.add(usuario)
    db.commit()
    return usuario


def registrar_cliente(db: Session, datos: RegistroIn) -> Usuario:
    """Registro público: siempre crea rol CLIENTE (nadie puede auto-asignarse otro rol)."""
    return _crear(db, datos, Rol.CLIENTE)


def crear_usuario_admin(db: Session, datos: UsuarioCrearIn) -> Usuario:
    if datos.rol == Rol.EMPLEADO_POS and not datos.codigo_empleado:
        raise ReglaNegocioError("Un empleado POS requiere código de empleado")
    return _crear(db, datos, datos.rol, datos.codigo_empleado)
