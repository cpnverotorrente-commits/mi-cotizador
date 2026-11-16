# Proposal

## Why

El historial de conversiones vive hoy en un `historial.txt` junto al programa: lo comparten todos los usuarios de esa computadora, no sabe quién hizo cada conversión y cualquiera puede leerlo o editarlo. Ahora que existen cuentas en PocketBase, el historial debe guardarse allí y ser privado para cada usuario.

## What Changes

- Nueva colección **`consultas`** en PocketBase con: usuario (relación con `users`), monto, cotización, resultado y fecha y hora.
- Cada conversión exitosa se guarda en `consultas` a nombre del usuario con sesión iniciada. **Se deja de escribir `historial.txt`** (**BREAKING** para quien lea ese archivo).
- Reglas de acceso de PocketBase: cada usuario lista y ve solo sus propias consultas, solo puede crearlas a su nombre y no puede modificarlas ni borrarlas. Esto rige también para los admins: nadie ve las consultas de otro por la API de la app.
- Pantalla **"Mi historial"** en la app, accesible desde el conversor, con la lista de las consultas del usuario (más recientes primero).
- El script de configuración de PocketBase crea la colección y sus reglas, de forma idempotente.

Supuestos registrados:
- La fecha y hora la fija PocketBase al crear el registro (no el reloj de la computadora del usuario) y se muestra en hora local.
- Monto, cotización y resultado se guardan como números con 2 decimales, los mismos valores que muestra la app.
- Si no se puede guardar en PocketBase, la app igual muestra el resultado y avisa que la consulta no se guardó; no hay respaldo en `historial.txt` ni reintento posterior.
- Las consultas no se pueden editar ni borrar desde la app; solo un superusuario de PocketBase puede hacerlo desde su panel.
- Las líneas ya existentes en `historial.txt` no se migran; el archivo queda como está, sin uso.
- El historial muestra hasta las últimas 200 consultas, sin paginación.

Fuera de alcance: migrar el `historial.txt` anterior, exportar el historial, borrar o editar consultas, que un admin vea las consultas de otros, paginación y filtros.

## Capabilities

### New Capabilities
- `conversion-records`: guardado de cada conversión en PocketBase a nombre del usuario, privacidad por usuario impuesta por reglas del servidor y pantalla para ver el propio historial.

### Modified Capabilities

## Impact

- PocketBase: nueva colección `consultas` con reglas; el script `scripts/configurar_pocketbase.py` y `scripts/verificar_reglas.py` se extienden.
- Código: `mi_cotizador/pocketbase.py` (guardar y listar consultas), `mi_cotizador/app.py` (guardar en PocketBase y botón de historial), nueva pantalla de historial; se elimina `mi_cotizador/historial.py` y sus tests.
- Este change reemplaza el comportamiento de la capacidad `conversion-history` de `add-mi-cotizador`, que aún no está archivada, por lo que no se puede modificar con un delta todavía. Al archivar, esa capacidad debe retirarse (ver Workflow follow-up en tasks.md).
- Reconstruir `MiCotizador.exe` con `build.bat`; el `.exe` ya no escribe `historial.txt`.
