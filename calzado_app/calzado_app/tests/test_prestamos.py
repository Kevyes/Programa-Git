import pytest

from app.models import EstadoPrestamo, PrestamoTemporal, Producto, Venta


def stock(db, producto_id):
    p = db.get(Producto, producto_id)
    db.refresh(p)
    return p.stock_disponible, p.stock_en_prueba


def salida(client, headers, items, codigo="EMP001"):
    return client.post("/api/prestamos", json={"codigo_empleado": codigo, "items": items}, headers=headers)


def test_salida_temporal_mueve_stock_de_disponible_a_en_prueba(client, auth, db):  # RF01, RF02, HU01
    h = auth("pos1@t.com", "Pos12345")
    r = salida(client, h, [{"producto_id": 1, "cantidad": 2}])
    assert r.status_code == 201
    assert stock(db, 1) == (3, 2)
    prestamo = r.json()[0]
    assert prestamo["estado"] == "EN_PRUEBA" and prestamo["asignacion_activa"] is True
    assert prestamo["fecha_hora_salida"] and prestamo["fecha_hora_retorno"] is None


def test_salida_de_varios_pares_en_una_operacion(client, auth, db):  # RF01
    h = auth("pos1@t.com", "Pos12345")
    r = salida(client, h, [{"producto_id": 1, "cantidad": 1}, {"producto_id": 2, "cantidad": 2}])
    assert r.status_code == 201 and len(r.json()) == 2
    assert stock(db, 1) == (4, 1) and stock(db, 2) == (0, 2)


def test_stock_insuficiente_rechaza_y_no_deja_cambios_parciales(client, auth, db):  # RNF01 (atomicidad)
    h = auth("pos1@t.com", "Pos12345")
    r = salida(client, h, [{"producto_id": 1, "cantidad": 1}, {"producto_id": 2, "cantidad": 40}])
    assert r.status_code == 400
    assert stock(db, 1) == (5, 0)  # el primer ítem se revirtió
    assert db.query(PrestamoTemporal).count() == 0


def test_no_se_puede_retirar_producto_sin_stock(client, auth):
    h = auth("pos1@t.com", "Pos12345")
    assert salida(client, h, [{"producto_id": 3, "cantidad": 1}]).status_code == 400


def test_producto_inexistente_da_404(client, auth):
    h = auth("pos1@t.com", "Pos12345")
    assert salida(client, h, [{"producto_id": 999, "cantidad": 1}]).status_code == 404


def test_codigo_de_empleado_debe_coincidir_con_el_usuario(client, auth, db):
    h = auth("pos1@t.com", "Pos12345")
    assert salida(client, h, [{"producto_id": 1, "cantidad": 1}], codigo="EMP002").status_code == 400
    assert stock(db, 1) == (5, 0)


def test_devolver_regresa_el_par_al_estante(client, auth, db):  # RF03, HU02
    h = auth("pos1@t.com", "Pos12345")
    pid = salida(client, h, [{"producto_id": 1, "cantidad": 2}]).json()[0]["id"]
    r = client.post(f"/api/prestamos/{pid}/liquidar", json={"accion": "DEVOLVER"}, headers=h)
    assert r.status_code == 200
    datos = r.json()["prestamo"]
    assert datos["estado"] == "DEVUELTO" and datos["asignacion_activa"] is False
    assert datos["fecha_hora_retorno"] is not None
    assert stock(db, 1) == (5, 0)
    assert r.json()["venta"] is None


def test_vender_emite_factura_y_limpia_stock_en_prueba(client, auth, db):  # RF03, HU02
    h = auth("pos1@t.com", "Pos12345")
    pid = salida(client, h, [{"producto_id": 1, "cantidad": 2}]).json()[0]["id"]
    r = client.post(f"/api/prestamos/{pid}/liquidar", json={"accion": "VENDER"}, headers=h)
    assert r.status_code == 200
    venta = r.json()["venta"]
    assert venta["numero_factura"].startswith("FAC-") and venta["total"] == 200000 and venta["canal"] == "POS"
    assert r.json()["prestamo"]["estado"] == "VENDIDO"
    assert stock(db, 1) == (3, 0)
    assert db.query(Venta).count() == 1


def test_un_prestamo_no_se_liquida_dos_veces(client, auth, db):
    h = auth("pos1@t.com", "Pos12345")
    pid = salida(client, h, [{"producto_id": 1, "cantidad": 1}]).json()[0]["id"]
    assert client.post(f"/api/prestamos/{pid}/liquidar", json={"accion": "DEVOLVER"}, headers=h).status_code == 200
    assert client.post(f"/api/prestamos/{pid}/liquidar", json={"accion": "DEVOLVER"}, headers=h).status_code == 400
    assert stock(db, 1) == (5, 0)  # no se duplicó la devolución


def test_empleado_no_liquida_prestamo_de_otro(client, auth):
    h1, h2 = auth("pos1@t.com", "Pos12345"), auth("pos2@t.com", "Pos12345")
    pid = salida(client, h1, [{"producto_id": 1, "cantidad": 1}]).json()[0]["id"]
    assert client.post(f"/api/prestamos/{pid}/liquidar", json={"accion": "VENDER"}, headers=h2).status_code == 403


def test_lista_de_prestamos_activos_solo_del_empleado(client, auth):
    h1, h2 = auth("pos1@t.com", "Pos12345"), auth("pos2@t.com", "Pos12345")
    salida(client, h1, [{"producto_id": 1, "cantidad": 1}])
    assert len(client.get("/api/prestamos", headers=h1).json()) == 1
    assert client.get("/api/prestamos", headers=h2).json() == []


def test_marcas_de_tiempo_son_inmutables(db, client, auth):
    h = auth("pos1@t.com", "Pos12345")
    pid = salida(client, h, [{"producto_id": 1, "cantidad": 1}]).json()[0]["id"]
    client.post(f"/api/prestamos/{pid}/liquidar", json={"accion": "DEVOLVER"}, headers=h)
    prestamo = db.get(PrestamoTemporal, pid)
    from datetime import datetime, timezone

    prestamo.fecha_hora_salida = datetime(2000, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        db.commit()
    db.rollback()
    prestamo = db.get(PrestamoTemporal, pid)
    prestamo.fecha_hora_retorno = datetime(2000, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        db.commit()
    db.rollback()
    assert prestamo.estado == EstadoPrestamo.DEVUELTO


def test_respuesta_muestra_el_stock_ya_actualizado(client, auth):
    h = auth("pos1@t.com", "Pos12345")
    creado = salida(client, h, [{"producto_id": 1, "cantidad": 2}]).json()[0]
    assert (creado["producto"]["stock_disponible"], creado["producto"]["stock_en_prueba"]) == (3, 2)
    r = client.post(f"/api/prestamos/{creado['id']}/liquidar", json={"accion": "VENDER"}, headers=h).json()
    assert (r["prestamo"]["producto"]["stock_disponible"], r["prestamo"]["producto"]["stock_en_prueba"]) == (3, 0)
