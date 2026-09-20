from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Producto(Base):
    """Un par de calzado (referencia + talla + color) con sus dos estados de stock."""

    __tablename__ = "productos"
    # Defensa a nivel de BD: el inventario nunca puede quedar negativo (RNF01).
    __table_args__ = (
        CheckConstraint("stock_disponible >= 0", name="ck_stock_disponible_no_negativo"),
        CheckConstraint("stock_en_prueba >= 0", name="ck_stock_en_prueba_no_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marca: Mapped[str] = mapped_column(String(60), index=True)
    modelo: Mapped[str] = mapped_column(String(80), index=True)
    color: Mapped[str] = mapped_column(String(40), index=True)
    talla: Mapped[int] = mapped_column(index=True)
    precio: Mapped[int]  # en pesos colombianos (COP)
    stock_disponible: Mapped[int] = mapped_column(default=0)
    stock_en_prueba: Mapped[int] = mapped_column(default=0)
