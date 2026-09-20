from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.core.database import get_db
from app.models import Rol
from app.schemas.schemas import ProductoIn, ProductoOut
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["Catálogo"])


@router.get("", response_model=list[ProductoOut])
def catalogo(
    talla: Optional[int] = None,
    marca: Optional[str] = None,
    color: Optional[str] = None,
    modelo: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Público: solo productos con stock disponible (HU03)."""
    return producto_service.listar_catalogo(db, talla, marca, color, modelo, solo_disponibles=True)


@router.get("/todos", response_model=list[ProductoOut], dependencies=[Depends(requiere_roles(Rol.ADMIN))])
def inventario_completo(db: Session = Depends(get_db)):
    return producto_service.listar_catalogo(db, solo_disponibles=False)


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(requiere_roles(Rol.ADMIN))])
def crear(datos: ProductoIn, db: Session = Depends(get_db)):
    return producto_service.crear_producto(db, datos)


@router.put("/{producto_id}", response_model=ProductoOut, dependencies=[Depends(requiere_roles(Rol.ADMIN))])
def actualizar(producto_id: int, datos: ProductoIn, db: Session = Depends(get_db)):
    return producto_service.actualizar_producto(db, producto_id, datos)
