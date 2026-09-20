# Sistema de Calzado: POS (calzado en prueba) + Tienda virtual

Backend: Python + FastAPI + SQLAlchemy · Base de datos: SQLite (pruebas) / PostgreSQL (producción)
Seguridad: JWT + RBAC + bcrypt · Frontend: HTML5 + CSS3 + JavaScript

## Puesta en marcha rápida
```bash
python -m venv venv
venv\Scripts\activate            # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # Linux/Mac: cp .env.example .env
python seed.py                   # datos de ejemplo
uvicorn app.main:app --reload    # abrir http://127.0.0.1:8000
```
Documentación interactiva de la API: http://127.0.0.1:8000/docs

## Usuarios de ejemplo
| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@calzado.com | Admin12345 |
| Empleado POS (EMP001) | pos1@calzado.com | Pos12345 |
| Empleado POS (EMP002) | pos2@calzado.com | Pos12345 |
| Cliente | cliente@calzado.com | Cliente12345 |

## Pruebas
```bash
pytest -v
```
