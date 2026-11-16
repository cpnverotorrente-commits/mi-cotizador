# Proposal

## Why

Hoy todos los usuarios registrados son iguales y nadie puede administrarlos. Se necesita distinguir administradores de usuarios comunes y darles un panel para listar cuentas, desactivarlas y resetear contraseñas, con reglas en PocketBase que impidan que un usuario común haga lo mismo por la API.

## What Changes

- La colección `users` de PocketBase recibe un campo **`rol`** (`usuario` o `admin`) y un campo **`desactivado`** (sí/no, por defecto no) para poder desactivar cuentas.
- Reglas de acceso de PocketBase: solo un admin puede listar todas las cuentas, cambiar `rol`/`desactivado` y resetear la contraseña de otros; un usuario común solo ve y edita su propio registro y no puede asignarse un rol ni reactivarse; el registro público siempre crea usuarios con rol `usuario` y activo.
- Una cuenta desactivada no puede iniciar sesión.
- Al iniciar sesión un admin, la app muestra un **panel de administración** con la lista de cuentas (email, rol, estado) y acciones para activar/desactivar y resetear la contraseña; desde el panel puede abrir el conversor y volver.
- Los usuarios comunes siguen yendo directo al conversor, sin ver el panel.
- Un script de configuración idempotente aplica el campo, las reglas y el primer admin en PocketBase, para que sea reproducible.

Supuestos registrados:
- "Desactivar" significa bloquear el inicio de sesión (campo `desactivado`); no se borran cuentas.
- "Resetear contraseña" significa que el admin define una contraseña nueva (mínimo 8 caracteres) para la cuenta; PocketBase no tiene correo configurado, así que no se envía mail. Las sesiones abiertas de esa cuenta dejan de ser válidas.
- Los usuarios sin rol (los existentes y los recién registrados) se tratan como `usuario`; el campo `desactivado` en falso significa cuenta activa.
- El primer admin se crea o promueve con el script de configuración usando el superusuario de PocketBase; el panel de la app no cambia roles.
- Un admin no puede desactivarse a sí mismo desde el panel.
- La lista muestra hasta 200 cuentas, sin paginación.

Fuera de alcance: cambiar roles desde la app, borrar cuentas, envío de correos de recuperación, más roles que `usuario` y `admin`, registro de auditoría.

## Capabilities

### New Capabilities
- `user-roles`: campo de rol y de estado activo en los usuarios, reglas de acceso de PocketBase por rol y bloqueo de inicio de sesión a cuentas desactivadas.
- `admin-panel`: panel de la app, visible solo para admins, para listar cuentas, activar/desactivar y resetear contraseñas.

### Modified Capabilities

## Impact

- PocketBase: esquema y reglas de la colección `users`; nuevo script `scripts/configurar_pocketbase.py` (usa credenciales del superusuario por variables de entorno).
- Código: `mi_cotizador/pocketbase.py` (listar, actualizar, resetear; devolver rol), `mi_cotizador/pantallas.py` o módulo nuevo para el panel, `mi_cotizador/app.py` (elegir pantalla según rol).
- Este change se apoya en `user-authentication` de `add-login-registro`, que aún no está archivado; por eso no modifica esa spec y el bloqueo a cuentas desactivadas queda en `user-roles`.
- Hay que reconstruir `MiCotizador.exe` con `build.bat`.
