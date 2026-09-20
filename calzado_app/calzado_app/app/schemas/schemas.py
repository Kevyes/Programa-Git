"""Esquemas Pydantic: validan la entrada y dan forma a la salida de la API."""
from datetime import datetime, timezone
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from app.models.enums import Canal, EstadoPrestamo, Rol


def _a_utc_iso(valor: datetime) -> str:
    if valor.tzinfo is None:  # SQLite devuelve fechas sin zona; las guardamos siempre en UTC
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.isoformat()


FechaUTC = Annotated[datetime, PlainSerializer(_a_utc_iso, return_type=str)]
EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


# ---------- Autenticación / usuarios ----------
class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: str = Field(pattern=EMAIL_REGEX, max_length=120)
    password: str = Field(min_length=8, max_length=72)


class UsuarioCrearIn(RegistroIn):
    rol: Rol
    codigo_empleado: Optional[str] = Field(default=None, max_length=20)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: str
    rol: Rol
    codigo_empleado: Optional[str] = None


# ---------- Productos ----------
class ProductoIn(BaseModel):
    marca: str = Field(min_length=1, max_length=60)
    modelo: str = Field(min_length=1, max_length=80)
    color: str = Field(min_length=1, max_length=40)
    talla: int = Field(ge=20, le=50)
    precio: int = Field(gt=0)
    stock_disponible: int = Field(ge=0)


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    marca: str
    modelo: str
    color: str
    talla: int
    precio: int
    stock_disponible: int
    stock_en_prueba: int


# ---------- Préstamos temporales ----------
class ItemIn(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0, le=50)


class PrestamoCrearIn(BaseModel):
    codigo_empleado: str = Field(min_length=1, max_length=20)
    items: list[ItemIn] = Field(min_length=1)


class PrestamoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int
    cantidad: int
    estado: EstadoPrestamo
    asignacion_activa: bool
    fecha_hora_salida: FechaUTC
    fecha_hora_retorno: Optional[FechaUTC] = None
    producto: ProductoOut


class LiquidarIn(BaseModel):
    accion: Literal["DEVOLVER", "VENDER"]


# ---------- Ventas ----------
class VentaWebIn(BaseModel):
    items: list[ItemIn] = Field(min_length=1)


class VentaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero_factura: str
    canal: Canal
    total: int
    fecha_hora: FechaUTC


class LiquidarOut(BaseModel):
    prestamo: PrestamoOut
    venta: Optional[VentaOut] = None


# ---------- Auditoría ----------
class AuditoriaOut(BaseModel):
    id: int
    empleado_id: int
    empleado_nombre: str
    codigo_empleado: Optional[str]
    producto: str
    cantidad: int
    estado: EstadoPrestamo
    fecha_hora_salida: FechaUTC
    fecha_hora_retorno: Optional[FechaUTC] = None
