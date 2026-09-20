from typing import Optional

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import Rol


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    rol: Mapped[Rol] = mapped_column(Enum(Rol, native_enum=False, length=20))
    codigo_empleado: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    activo: Mapped[bool] = mapped_column(default=True)
