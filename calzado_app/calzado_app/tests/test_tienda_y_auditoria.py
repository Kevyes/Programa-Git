from datetime import datetime, timedelta, timezone

from app.models import Producto


def test_catalogo_solo_muestra_stock_mayor_a_cero(client):  # HU03
    productos = client.get("/api/productos").json()
    assert {p["id"] for p in productos} == {1, 2}  # el producto 3 tiene stock 0


def test_catalogo_filtra_por_talla_marca_color_modelo(client):  # RF04
    assert [p["id"] for p in client.get("/api/productos?talla=40").json()] == [1]
    assert [p["id"] for p in client.get("/api/productos?marca=adi").json()] == [2]
    assert [p["id"] for p in client.get("/api/productos?color=negro").json()] == [1]
    assert [p["id"] for p in client.get("/api/productos?modelo=super").json()] == [2]
    assert client.get("/api/productos?talla=99").json() == []


def test_producto_en_prueba_no_aparece_si_agota_stock_disponible(client, auth):
    h = auth("pos1@t.com", "Pos12345")
    client.post("/api/prestamos", json={"codigo_empleado": "EMP001", "items": [{"producto_id": 2, "cantidad": 2}]}, headers=h)
    assert [p["id"] for p in client.get("/api/productos").json()] == [1]


def test_compra_web_descuenta_stock_y_calcula_total(client, auth, db):  # RF04
    h = auth("cli@t.com", "Cliente12345")
    r = client.post("/api/ventas/web", json={"items": [{"producto_id": 1, "cantidad": 2}, {"producto_id": 2, "cantidad": 1}]}, headers=h)
    assert r.status_code == 201
    assert r.json()["total"] == 2 * 100000 + 80000 and r.json()["canal"] == "WEB"
    db.expire_all()
    assert db.get(Producto, 1).stock_disponible == 3 and db.get(Producto, 2).stock_disponible == 1


def test_compra_web_sin_stock_suficiente_no_modifica_inventario(client, auth, db):  # RNF01
    h = auth("cli@t.com", "Cliente12345")
    r = client.post("/api/ventas/web", json={"items": [{"producto_id": 1, "cantidad": 1}, {"producto_id": 2, "cantidad": 10}]}, headers=h)
    assert r.status_code == 400
    db.expire_all()
    assert db.get(Producto, 1).stock_disponible == 5


def test_no_hay_doble_venta_entre_pos_y_web(client, auth, db):  # RNF01: canal virtual consistente
    pos, cli = auth("pos1@t.com", "Pos12345"), auth("cli@t.com", "Cliente12345")
    client.post("/api/prestamos", json={"codigo_empleado": "EMP001", "items": [{"producto_id": 2, "cantidad": 2}]}, headers=pos)
    r = client.post("/api/ventas/web", json={"items": [{"producto_id": 2, "cantidad": 1}]}, headers=cli)
    assert r.status_code == 400  # ya está todo "en prueba" en tienda


def test_auditoria_lista_filtra_por_empleado_y_fechas(client, auth):  # RF05, HU04
    p1, p2, admin = auth("pos1@t.com", "Pos12345"), auth("pos2@t.com", "Pos12345"), auth("admin@t.com", "Admin12345")
    client.post("/api/prestamos", json={"codigo_empleado": "EMP001", "items": [{"producto_id": 1, "cantidad": 1}]}, headers=p1)
    client.post("/api/prestamos", json={"codigo_empleado": "EMP002", "items": [{"producto_id": 1, "cantidad": 1}]}, headers=p2)

    todo = client.get("/api/auditoria/prestamos", headers=admin).json()
    assert len(todo) == 2 and {f["codigo_empleado"] for f in todo} == {"EMP001", "EMP002"}

    id_emp1 = next(f["empleado_id"] for f in todo if f["codigo_empleado"] == "EMP001")
    assert len(client.get(f"/api/auditoria/prestamos?empleado_id={id_emp1}", headers=admin).json()) == 1

    ahora = datetime.now(timezone.utc)
    futuro = (ahora + timedelta(hours=1)).isoformat()
    pasado = (ahora - timedelta(hours=1)).isoformat()
    assert client.get("/api/auditoria/prestamos", params={"desde": futuro}, headers=admin).json() == []
    assert len(client.get("/api/auditoria/prestamos", params={"desde": pasado, "hasta": futuro}, headers=admin).json()) == 2


def test_auditoria_exporta_csv(client, auth):
    p1, admin = auth("pos1@t.com", "Pos12345"), auth("admin@t.com", "Admin12345")
    client.post("/api/prestamos", json={"codigo_empleado": "EMP001", "items": [{"producto_id": 1, "cantidad": 1}]}, headers=p1)
    r = client.get("/api/auditoria/prestamos/export", headers=admin)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    assert "EMP001" in r.text and r.text.startswith("ID,Empleado")


def test_admin_crea_y_actualiza_productos(client, auth):
    admin = auth("admin@t.com", "Admin12345")
    nuevo = {"marca": "Vans", "modelo": "Old Skool", "color": "Negro", "talla": 39, "precio": 250000, "stock_disponible": 4}
    r = client.post("/api/productos", json=nuevo, headers=admin)
    assert r.status_code == 201
    pid = r.json()["id"]
    nuevo["stock_disponible"] = 9
    assert client.put(f"/api/productos/{pid}", json=nuevo, headers=admin).json()["stock_disponible"] == 9
    assert len(client.get("/api/productos/todos", headers=admin).json()) == 4


def test_validaciones_de_entrada(client, auth):
    h = auth("pos1@t.com", "Pos12345")
    r = client.post("/api/prestamos", json={"codigo_empleado": "EMP001", "items": [{"producto_id": 1, "cantidad": 0}]}, headers=h)
    assert r.status_code == 422
    r = client.post("/api/prestamos", json={"codigo_empleado": "EMP001", "items": []}, headers=h)
    assert r.status_code == 422
