"""Punto de entrada: crea la app FastAPI, registra routers, errores y el frontend estático."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401  (registra las tablas en Base.metadata)
from app.api import auditoria, auth, prestamos, productos, usuarios, ventas
from app.core.database import Base, engine
from app.core.exceptions import NoEncontradoError, PermisoError, ReglaNegocioError

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # crea las tablas si no existen
    yield


app = FastAPI(title="Sistema de Calzado: POS + Tienda Virtual", version="1.0.0", lifespan=lifespan)

for router in (auth.router, usuarios.router, productos.router, prestamos.router, ventas.router, auditoria.router):
    app.include_router(router, prefix="/api")


@app.get("/api/health", tags=["Sistema"])
def health():
    return {"estado": "ok"}


@app.exception_handler(ReglaNegocioError)
async def _regla(_: Request, exc: ReglaNegocioError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(NoEncontradoError)
async def _no_encontrado(_: Request, exc: NoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(PermisoError)
async def _permiso(_: Request, exc: PermisoError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


# El frontend se sirve en la raíz (debe ir al final para no tapar /api).
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
