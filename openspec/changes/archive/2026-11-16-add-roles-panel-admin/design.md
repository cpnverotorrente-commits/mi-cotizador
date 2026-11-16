# Design

## Context

La app ya inicia sesión contra la colección `users` por la API REST (`mi_cotizador/pocketbase.py`, solo `urllib`), y hoy descarta el token tras autenticar. PocketBase 0.40.6 corre en local. Motivación y alcance: ver proposal.md; requisitos en specs/user-roles y specs/admin-panel.

## Goals / Non-Goals

**Goals:**
- Que PocketBase sea quien impone los permisos: aunque alguien llame a la API sin usar la app, un usuario común no puede listar ni modificar cuentas ajenas ni escalar privilegios.
- Configuración de PocketBase reproducible desde el repositorio.

**Non-Goals:**
- Auditoría, más roles, envío de mails, borrar cuentas.

## Decisions

- **Campos nuevos en `users`:** `rol` (select, valores `usuario` y `admin`; vacío cuenta como `usuario`) y `desactivado` (bool, falso por defecto). Se eligió `desactivado` y no `activo` porque un bool nuevo vale falso por defecto y el registro público no puede fijar valores: con `activo` todas las cuentas nuevas nacerían desactivadas. Alternativas: colección de roles aparte (excesivo para dos roles); usar superusuarios de PocketBase como admins (no son usuarios de la app y tendrían acceso total al panel de PocketBase).
- **Reglas de la colección `users`** (expresiones de PocketBase; `rol` vacío cuenta como `usuario`):
  - `listRule` y `viewRule`: `id = @request.auth.id || @request.auth.rol = "admin"`.
  - `createRule`: `@request.body.rol:isset = false && @request.body.desactivado:isset = false`.
  - `updateRule`: `(id = @request.auth.id && @request.body.rol:isset = false && @request.body.desactivado:isset = false) || @request.auth.rol = "admin"`.
  - `deleteRule`: `null` (solo superusuarios; la app no borra cuentas).
  - `authRule`: `desactivado = false`, que impide el login de cuentas desactivadas (PocketBase responde 403, que la app muestra como cuenta desactivada).
- **Cambio de contraseña por un admin:** `PATCH /api/collections/users/records/{id}` con `password` y `passwordConfirm`. PocketBase exige la contraseña anterior salvo que se cumpla `manageRule`, por eso se define `manageRule: @request.auth.rol = "admin"`. El cambio invalida los tokens anteriores de esa cuenta.
- **Token de sesión en memoria.** Hasta ahora no se guardaba; el panel lo necesita para el encabezado `Authorization`. Vive solo en el objeto de sesión de la app y se descarta al cerrar sesión (sin archivos).
- **Rol desde la respuesta de autenticación** (`record.rol`), no desde un campo que la app invente. La interfaz oculta el panel a usuarios comunes, pero la protección real son las reglas.
- **Script `scripts/configurar_pocketbase.py`** con `urllib`, autentica como superusuario con `PB_SUPERUSER_EMAIL` y `PB_SUPERUSER_PASSWORD` (variables de entorno, nunca en el repositorio), agrega los campos si faltan (`PATCH` sobre la colección), aplica las reglas y crea o promueve al admin indicado por `--admin email`. Alternativa: migraciones JS en `pocketbase/pb_migrations/`; descartado porque `pocketbase/` está en `.gitignore` y no se versionaría.
- **Panel en Tkinter** (`ttk.Treeview` con columnas email, rol, estado), botones Activar/Desactivar y Resetear contraseña, y un diálogo propio con dos campos enmascarados para la contraseña nueva. `app.py` elige panel o conversor según el rol; el admin navega entre panel y conversor dentro de la misma ventana.
- **Listado:** `GET .../records?perPage=200&sort=email`; sin paginación por ahora.
- **Errores:** se extienden las excepciones de `pocketbase.py` con `NoAutorizado` (401/403/404 en acciones de admin) además de las existentes.

## Risks / Trade-offs

- [Regla mal escrita deja acceso abierto o bloquea al propio admin] → probar cada regla contra el servidor real con usuario común, admin y sin sesión, y que esas pruebas queden como parte de la verificación.
- [Un admin podría quedarse sin acceso al desactivar a todos los admins] → el panel impide desactivarse a uno mismo, y el superusuario de PocketBase siempre puede reactivar cuentas.
- [Cuentas sin valor en `desactivado` fallarían `authRule`] → un bool sin valor cuenta como falso y las cuentas existentes siguen activas (comprobado contra el servidor real).
- [El token en memoria vive mientras la ventana siga abierta] → se descarta al cerrar sesión; sin persistencia en disco.
- [Contraseña nueva viaja por HTTP local] → aceptable en `127.0.0.1`; HTTPS sería necesario fuera de local.
