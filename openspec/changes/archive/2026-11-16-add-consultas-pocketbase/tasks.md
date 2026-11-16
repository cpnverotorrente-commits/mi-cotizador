# Tasks

## 1. Colección en PocketBase

- [x] 1.1 Extender `scripts/configurar_pocketbase.py` para crear la colección `consultas` (usuario, monto, cotización, resultado y fecha autodate) con las reglas del diseño, de forma idempotente; verificar ejecutándolo dos veces contra el PocketBase local y consultando la colección con el superusuario
- [x] 1.2 Extender `scripts/verificar_reglas.py` con las comprobaciones de consultas: sin sesión no lista ni crea; un usuario crea la suya y no a nombre de otro; ve solo las suyas (también el admin); no puede editar ni borrar; la fecha la fija el servidor aunque el cliente envíe otra; ejecutarlo y verificar que todo pasa, borrando las cuentas y consultas de prueba al terminar

## 2. Cliente de PocketBase

- [x] 2.1 Agregar `guardar_consulta` y `listar_consultas` en `mi_cotizador/pocketbase.py`, con el token de la sesión y los errores existentes; verificar con tests unitarios simulados (cuerpo y encabezado enviados, lista ordenada y convertida, 403, servidor caído)

## 3. Guardado en lugar del TXT

- [x] 3.1 Hacer que `mi_cotizador/app.py` guarde cada conversión exitosa con `guardar_consulta` en lugar de `historial.txt`, mostrando el resultado primero y avisando si el guardado falla; eliminar `mi_cotizador/historial.py` y sus tests; verificar con una conversión real que aparece la consulta en PocketBase, que no se crea `historial.txt` y que con PocketBase apagado se muestra resultado y aviso

## 4. Pantalla de historial

- [x] 4.1 Crear la pantalla "Mi historial" (fecha local, monto, cotización y resultado, más recientes primero, mensaje de vacío y de error, botón Volver) y el botón de acceso desde el conversor, también para admins; verificar por código contra PocketBase real con dos usuarios que cada uno ve solo lo suyo, que un usuario sin consultas ve el mensaje de vacío y que con el servidor apagado aparece el error

## 5. Documentación y ejecutable

- [x] 5.1 Actualizar `README.md` (historial en PocketBase, colección `consultas`, cómo crearla con el script, fin de `historial.txt`); verificar que los comandos documentados se ejecutan tal cual
- [x] 5.2 Reconstruir con `build.bat` y verificar que `dist/MiCotizador.exe` abre y no genera `historial.txt`

## Workflow follow-up

- Archivar `add-mi-cotizador`, `add-login-registro` y `add-roles-panel-admin`, en ese orden, antes de este change.
- Al archivar este change, retirar la capacidad `conversion-history` que dejó `add-mi-cotizador`, porque este change la reemplaza.
