from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.security import hash_password, verify_password


def test_hash_bcrypt_no_guarda_texto_plano_y_usa_salt():
    h1, h2 = hash_password("Clave12345"), hash_password("Clave12345")
    assert h1 != "Clave12345" and h1.startswith("$2")
    assert h1 != h2  # salt distinto en cada hash
    assert verify_password("Clave12345", h1)
    assert not verify_password("otra", h1)


def test_login_correcto_devuelve_jwt_con_rol(client):
    r = client.post("/api/auth/login", json={"email": "pos1@t.com", "password": "Pos12345"})
    assert r.status_code == 200
    payload = jwt.decode(r.json()["access_token"], settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["rol"] == "EMPLEADO_POS" and "exp" in payload


def test_login_incorrecto_rechazado(client):
    r = client.post("/api/auth/login", json={"email": "pos1@t.com", "password": "mala"})
    assert r.status_code == 400


def test_endpoint_protegido_sin_token_da_401(client):
    assert client.get("/api/prestamos").status_code == 401


def test_token_vencido_da_401(client):
    vencido = jwt.encode(
        {"sub": "1", "rol": "ADMIN", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.SECRET_KEY, algorithm="HS256",
    )
    r = client.get("/api/prestamos", headers={"Authorization": f"Bearer {vencido}"})
    assert r.status_code == 401


def test_rbac_cliente_no_puede_usar_pos_ni_auditoria(client, auth):
    h = auth("cli@t.com", "Cliente12345")
    body = {"codigo_empleado": "EMP001", "items": [{"producto_id": 1, "cantidad": 1}]}
    assert client.post("/api/prestamos", json=body, headers=h).status_code == 403
    assert client.get("/api/auditoria/prestamos", headers=h).status_code == 403


def test_rbac_empleado_no_puede_comprar_en_web_ni_crear_productos(client, auth):
    h = auth("pos1@t.com", "Pos12345")
    assert client.post("/api/ventas/web", json={"items": [{"producto_id": 1, "cantidad": 1}]}, headers=h).status_code == 403
    nuevo = {"marca": "X", "modelo": "Y", "color": "Z", "talla": 40, "precio": 1000, "stock_disponible": 1}
    assert client.post("/api/productos", json=nuevo, headers=h).status_code == 403


def test_registro_publico_siempre_crea_cliente(client):
    r = client.post("/api/auth/registro", json={"nombre": "Ana", "email": "ana@t.com", "password": "Clave12345"})
    assert r.status_code == 201 and r.json()["rol"] == "CLIENTE"
