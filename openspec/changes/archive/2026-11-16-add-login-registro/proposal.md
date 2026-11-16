# Proposal

## Why

Hoy cualquiera que abra Mi Cotizador usa el conversor. Se quiere que solo accedan personas con cuenta, usando los usuarios que ya gestiona PocketBase, que está instalado y corriendo en el proyecto.

## What Changes

- Nueva pantalla de **inicio de sesión** (email y contraseña) que se muestra al abrir la aplicación.
- Nueva pantalla de **registro** (email, contraseña y confirmación) accesible desde el inicio de sesión, que crea el usuario en PocketBase.
- El conversor existente solo se abre después de un inicio de sesión exitoso; se agrega una acción para cerrar sesión que vuelve al inicio de sesión.
- La aplicación se comunica con PocketBase por su API REST usando la biblioteca estándar de Python (sin dependencias nuevas).

Supuestos registrados:
- Se usa la colección de usuarios por defecto de PocketBase (`users`), no los superusuarios del panel de administración.
- PocketBase corre en `http://127.0.0.1:8090`; la dirección es configurable con la variable de entorno `COTIZADOR_PB_URL`.
- No se pide verificación de email ni recuperación de contraseña.
- La sesión no se recuerda: se pide iniciar sesión en cada apertura.
- Contraseña mínima de 8 caracteres (regla por defecto de PocketBase).
- `historial.txt` no cambia (no registra al usuario).

Fuera de alcance: verificación de email, restablecer contraseña, inicio de sesión con terceros (Google, etc.), roles, recordar sesión, historial por usuario, alojar PocketBase fuera de esta máquina.

## Capabilities

### New Capabilities
- `user-authentication`: registro e inicio de sesión de usuarios contra PocketBase, cierre de sesión y acceso al conversor condicionado a la sesión iniciada.

### Modified Capabilities

## Impact

- Código: `mi_cotizador/app.py` pasa a abrir primero el inicio de sesión; nuevo módulo de cliente de PocketBase y nuevas pantallas en `mi_cotizador/`.
- Dependencia de ejecución: PocketBase debe estar corriendo; sin él la aplicación avisa y no deja entrar.
- El change `add-mi-cotizador` aún no está archivado, por eso este change no modifica sus specs: el requisito de acceso condicionado queda en `user-authentication`.
- El ejecutable `MiCotizador.exe` debe reconstruirse con `build.bat`.
