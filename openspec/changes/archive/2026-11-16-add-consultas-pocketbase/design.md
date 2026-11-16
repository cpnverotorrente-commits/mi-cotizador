# Design

## Context

Hoy `app.py` guarda cada conversión con `mi_cotizador/historial.py` en `historial.txt`. La app ya tiene una `Sesion` en memoria (id, email, rol, token) y un cliente de PocketBase con `urllib` (`mi_cotizador/pocketbase.py`); `scripts/configurar_pocketbase.py` configura la colección `users`. Motivación y alcance: ver proposal.md; requisitos en specs/conversion-records.

## Goals / Non-Goals

**Goals:**
- Privacidad por usuario impuesta por PocketBase, no por la app.
- Historial a prueba de manipulación: fecha del servidor, usuario atado a la sesión y registros inmutables.

**Non-Goals:**
- Migración del TXT, exportación, edición o borrado, vista de admin sobre consultas ajenas.

## Decisions

- **Colección `consultas` (tipo base)** con campos: `usuario` (relación a `users`, obligatoria, un solo valor), `monto`, `cotizacion` y `resultado` (number, obligatorios), y `fecha` (autodate, solo al crear). Un campo `fecha` de tipo autodate (solo al crear) evita que el cliente falsee la hora y deja un nombre claro para ordenar y mostrar.
- **Reglas:**
  - `listRule` y `viewRule`: `usuario = @request.auth.id`.
  - `createRule`: `@request.auth.id != "" && @request.body.usuario = @request.auth.id`.
  - `updateRule` y `deleteRule`: `null` (solo superusuarios).
  Con `listRule` por usuario, un admin tampoco ve consultas ajenas por esta API, tal como se pidió.
- **Números con 2 decimales como `number` (float).** Para montos de esta app basta; se envían los `Decimal` ya redondeados convertidos a `float`. Alternativa: texto para conservar exactitud decimal, descartada porque no permite ordenar ni sumar en PocketBase.
- **Cliente:** `guardar_consulta(sesion, monto, cotizacion, resultado)` y `listar_consultas(sesion)` en `pocketbase.py`, con las mismas excepciones del resto; el listado pide `sort=-fecha&perPage=200`. Fecha en UTC de PocketBase convertida a hora local para mostrar.
- **Guardado desde la interfaz sin bloquear el resultado:** el resultado se muestra primero y luego se guarda; si falla, se agrega el aviso. Sin reintentos ni cola local, para no introducir un segundo almacenamiento.
- **Pantalla "Mi historial":** `ttk.Treeview` con columnas fecha, monto, cotización y resultado, botón "Volver" y mensaje de vacío o de error. Se abre desde un botón nuevo del conversor, también disponible para admins.
- **Se elimina `historial.py` y sus tests.** `historial.txt` ya generado queda intacto; la entrada de `.gitignore` se conserva por si existe.
- **Script de configuración:** `configurar_pocketbase.py` crea `consultas` si no existe (obteniendo el id de `users`) y siempre reaplica las reglas; si la colección existe, no toca los registros. `verificar_reglas.py` suma las comprobaciones de consultas.

## Risks / Trade-offs

- [Sin PocketBase no se guarda el historial] → aviso claro; el resultado igual se muestra. Es el costo de no tener un respaldo local.
- [Regla mal escrita expone consultas de otros] → pruebas contra el servidor real con dos usuarios, un admin y sin sesión, incluidas en la verificación.
- [Se pierde el historial viejo del TXT] → documentado como fuera de alcance; el archivo no se borra.
- [Float puede representar mal algunos decimales] → se redondea a 2 decimales antes de enviar; aceptable para mostrar y listar.
- [Un superusuario de PocketBase ve y puede editar todo] → inherente a PocketBase; fuera de alcance.
