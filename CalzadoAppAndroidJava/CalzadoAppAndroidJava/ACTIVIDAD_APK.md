# Evidencia: APK - desarrollar módulos móviles según requerimientos

## Base del desarrollo

El documento de requisitos entregado define cinco requisitos funcionales: salida temporal presencial, gestión de estados de inventario, liquidación del préstamo temporal, venta/carrito web y auditoría histórica. También establece requisitos no funcionales de consistencia ACID, autenticación/autorización con RBAC y JWT, y desempeño/disponibilidad para la plataforma web.

El diagrama de clases identifica las entidades `Empleado`, `Zapato`, `Inventario`, `PrestamoTemporalEmpleado`, `Venta` y `DetalleVenta`. El diagrama de paquetes separa presentación, seguridad, controladores, servicios y persistencia. El diagrama de componentes conecta el cliente con el servidor de aplicación, la base de datos y la pasarela de pagos. El mapa de navegación separa los flujos presencial, virtual y administrativo.

## Implementación móvil realizada

### Presentación

Se implementaron cuatro Activities:

- `LoginActivity`: autenticación y selección de rol.
- `PosActivity`: salida temporal, consulta de préstamos, devolución y venta presencial.
- `CatalogActivity`: catálogo, filtros, carrito y compra virtual.
- `AdminActivity`: auditoría, filtros y exportación CSV.

### Dominio / servicios

- `StockTemporalService`: orquesta el flujo de préstamo temporal.
- `VentaService`: orquesta la compra virtual.
- `AuditoriaService`: orquesta consulta y exportación del histórico.
- `InventoryRules`: contiene reglas unitarias puras para movimientos y cálculos.

### Persistencia

`DatabaseHelper` utiliza SQLite para el ambiente local de desarrollo y pruebas. Las operaciones de salida, devolución, venta presencial y compra virtual se ejecutan dentro de transacciones `beginTransaction / setTransactionSuccessful / endTransaction`.

La estructura de tablas refleja el modelo de clases principal y conserva `date_exit`, `date_return`, `quantity` y `state` para el histórico de préstamos.

### Seguridad

El APK tiene RBAC a nivel de navegación y una sesión con token firmado HMAC-SHA256 y expiración. La contraseña de demostración es local y únicamente sirve para el ambiente académico. La implementación de producción debe validar credenciales y JWT en el servidor y aplicar bcrypt/Argon2 para contraseñas.

### Ambiente de pruebas

- API Android: 36.
- Java: 17.
- Android Gradle Plugin: 8.13.2.
- Gradle: 8.13.
- Base local: SQLite.
- Pruebas unitarias: JUnit 4.

## Casos de prueba considerados

1. Registrar salida temporal con stock suficiente.
2. Rechazar salida temporal con stock insuficiente.
3. Devolver un préstamo reservado y restaurar el stock disponible.
4. Vender un préstamo reservado y registrar venta/detalle.
5. Consultar catálogo mostrando solo `stock_available > 0`.
6. Procesar un carrito completo dentro de una transacción.
7. Consultar auditoría por vendedor y rango de fechas.
8. Exportar la auditoría en CSV.

## Relación con Git

El proyecto contiene `.gitignore` y queda listo para inicializar un repositorio con `git init`, registrar cambios y asociarlo a GitHub.
