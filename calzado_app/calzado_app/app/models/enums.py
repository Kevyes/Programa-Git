import enum


class Rol(str, enum.Enum):
    ADMIN = "ADMIN"
    EMPLEADO_POS = "EMPLEADO_POS"
    CLIENTE = "CLIENTE"


class EstadoPrestamo(str, enum.Enum):
    EN_PRUEBA = "EN_PRUEBA"
    DEVUELTO = "DEVUELTO"
    VENDIDO = "VENDIDO"


class Canal(str, enum.Enum):
    WEB = "WEB"
    POS = "POS"
