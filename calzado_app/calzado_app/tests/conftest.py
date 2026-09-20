import os

os.environ["BCRYPT_ROUNDS"] = "4"  # hashes rápidos solo para pruebas
os.environ["DATABASE_URL"] = "sqlite://"  # nunca tocar la BD real durante las pruebas

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models import Producto, Rol, Usuario


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sesion = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    sesion.add_all([
        Usuario(nombre="Admin", email="admin@t.com", password_hash=hash_password("Admin12345"), rol=Rol.ADMIN),
        Usuario(nombre="Pos Uno", email="pos1@t.com", password_hash=hash_password("Pos12345"), rol=Rol.EMPLEADO_POS, codigo_empleado="EMP001"),
        Usuario(nombre="Pos Dos", email="pos2@t.com", password_hash=hash_password("Pos12345"), rol=Rol.EMPLEADO_POS, codigo_empleado="EMP002"),
        Usuario(nombre="Cliente", email="cli@t.com", password_hash=hash_password("Cliente12345"), rol=Rol.CLIENTE),
        Producto(marca="Nike", modelo="Air Max", color="Negro", talla=40, precio=100000, stock_disponible=5),
        Producto(marca="Adidas", modelo="Superstar", color="Blanco", talla=38, precio=80000, stock_disponible=2),
        Producto(marca="Puma", modelo="Suede", color="Rojo", talla=41, precio=70000, stock_disponible=0),
    ])
    sesion.commit()
    yield sesion
    sesion.close()
    engine.dispose()


@pytest.fixture()
def client(db):
    def _get_db():
        yield db

    app.dependency_overrides[get_db] = _get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def auth(client):
    """auth('pos1@t.com', 'Pos12345') -> cabecera Authorization lista para usar."""

    def _auth(email, password):
        r = client.post("/api/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    return _auth
