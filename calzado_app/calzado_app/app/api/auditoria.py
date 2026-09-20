from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.core.database import get_db
from app.models import Rol
from app.schemas.schemas import AuditoriaOut
from app.services import auditoria_service

router = APIRouter(prefix="/auditoria", tags=["Auditoría (solo ADMIN)"], dependencies=[Depends(requiere_roles(Rol.ADMIN))])


@router.get("/prestamos", response_model=list[AuditoriaOut])
def reporte(desde: Optional[datetime] = None, hasta: Optional[datetime] = None,
            empleado_id: Optional[int] = None, db: Session = Depends(get_db)):
    return auditoria_service.consultar(db, desde, hasta, empleado_id)


@router.get("/prestamos/export")
def exportar(desde: Optional[datetime] = None, hasta: Optional[datetime] = None,
             empleado_id: Optional[int] = None, db: Session = Depends(get_db)):
    contenido = auditoria_service.exportar_csv(auditoria_service.consultar(db, desde, hasta, empleado_id))
    return Response(contenido, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=auditoria_prestamos.csv"})
