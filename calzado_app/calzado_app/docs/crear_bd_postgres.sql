-- Ejecutar conectado como superusuario (postgres):  psql -U postgres -f docs/crear_bd_postgres.sql
CREATE USER calzado_user WITH PASSWORD 'CambiaEstaClave';
CREATE DATABASE calzado_db OWNER calzado_user ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE calzado_db TO calzado_user;
-- Las tablas las crea la propia aplicacion al arrancar (SQLAlchemy create_all).
