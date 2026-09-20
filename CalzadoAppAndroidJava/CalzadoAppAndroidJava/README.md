# Calzado App - Android Java

Implementación móvil de la evidencia **"APK (desarrollar módulos móviles según requerimientos del proyecto)"**, basada en el documento entregado para el proyecto de gestión de calzado.

## Stack

- Android nativo
- Java 17
- Android Gradle Plugin 8.13.2
- Gradle 8.13
- compileSdk / targetSdk 36 (Android 16)
- SQLite local para ambiente de desarrollo y pruebas
- JUnit 4 para pruebas unitarias de reglas de inventario

Android 16 corresponde al API 36 y la documentación oficial indica `compileSdk = 36` y `targetSdk = 36`. AGP 8.13.x es compatible con API 36 y usa Gradle 8.13 y JDK 17 como configuración de referencia.

## Módulos implementados

### 1. Seguridad / Login

Roles del documento:

- Empleado POS
- Cliente Virtual
- Administrador

Credenciales de demostración:

- `empleado / 1234`
- `cliente / 1234`
- `admin / 1234`

El APK crea un token firmado HMAC-SHA256 con expiración para demostrar la estructura de sesión. **No debe tratarse como un JWT de producción**: la autenticación real debe validarse en el backend y las contraseñas deben almacenarse con bcrypt/Argon2 en el servidor.

### 2. Módulo presencial (Empleado POS)

- Selección de calzado y cantidad.
- Salida temporal.
- Movimiento `stock_available -> stock_test` dentro de una transacción SQLite.
- Consulta de préstamos activos del empleado.
- Devolución: `stock_test -> stock_available`.
- Venta presencial: genera venta/detalle y limpia el stock en prueba.
- Fecha/hora de salida y liquidación.

### 3. Módulo virtual (Cliente)

- Catálogo filtrable por talla y color.
- Solo muestra productos con `stock_available > 0`.
- Carrito de compras.
- Compra virtual transaccional.

### 4. Módulo administrativo

- Auditoría de préstamos.
- Filtro por documento del vendedor y rango de fechas.
- Consulta de fecha/hora de salida y retorno.
- Exportación del reporte a CSV mediante `ACTION_CREATE_DOCUMENT`.

## Arquitectura y paquetes

- `data.model`: entidades del diagrama de clases.
- `data.db`: persistencia SQLite y transacciones ACID locales.
- `domain`: reglas de negocio independientes de Android.
- `domain.service`: servicios `StockTemporalService`, `VentaService` y `AuditoriaService`.
- `security`: sesión, autenticación de demostración y token.
- `presentation.login`: navegación inicial.
- `presentation.pos`: módulo presencial.
- `presentation.catalog`: módulo virtual.
- `presentation.admin`: módulo administrativo.
- `presentation.common`: componentes reutilizables de interfaz.
- `config`: configuración central de API para la futura integración REST.

La estructura sigue la idea del diagrama de paquetes entregado: Presentación -> Servicios/Reglas -> Persistencia, con Seguridad como componente transversal.

## Cómo abrir

1. Abrir la carpeta `CalzadoAppAndroidJava` desde Android Studio.
2. Instalar Android SDK Platform 36.
3. Usar JDK 17 para Gradle.
4. Sincronizar el proyecto.
5. Ejecutar la variante `debug` en un emulador o teléfono.

## Pruebas unitarias

La prueba `InventoryRulesTest` cubre:

- Movimiento a stock en prueba.
- Retorno del stock.
- Rechazo por stock insuficiente.
- Rechazo por stock en prueba insuficiente.
- Cálculo de total de venta.

En Android Studio: `app/src/test` -> ejecutar `InventoryRulesTest`.

## Nota sobre backend y PostgreSQL

El PDF plantea un backend REST y una base SQL transaccional (PostgreSQL/MySQL). Este APK implementa el módulo móvil con una persistencia SQLite local para que pueda ejecutarse y demostrarse de forma autónoma. La clase `DatabaseHelper` concentra el acceso a datos; en una versión integrada, sus operaciones pueden sustituirse por un repositorio HTTP contra la API REST sin cambiar la navegación ni las reglas de negocio.

## Repositorio Git

El proyecto está preparado para control de versiones. Se recomienda inicializarlo con:

```bash
git init
git add .
git commit -m "Implementación inicial de APK Calzado App"
```
