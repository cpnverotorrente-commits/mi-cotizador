# Design

## Context

Mi Cotizador es una app Tkinter con `app.py` (ventana `Cotizador` con el conversor), `logica.py` e `historial.py`. PocketBase 0.40.6 corre en `127.0.0.1:8090`, con un superusuario ya creado. Motivación y alcance: ver proposal.md; requisitos en specs/user-authentication.

## Goals / Non-Goals

**Goals:**
- Cliente de PocketBase pequeño y probable sin interfaz ni servidor real.
- Sin dependencias nuevas en tiempo de ejecución ni en el ejecutable.

**Non-Goals:**
- Guardar el token de sesión, renovarlo o usarlo para otras llamadas: el conversor no consulta a PocketBase.

## Decisions

- **API REST con `urllib` (biblioteca estándar).** Endpoints: `POST /api/collections/users/auth-with-password` (campos `identity` y `password`) para iniciar sesión, y `POST /api/collections/users/records` (`email`, `password`, `passwordConfirm`) para registrar. Alternativa: SDK de PocketBase para Python; descartado por sumar una dependencia para dos llamadas.
- **Módulos nuevos:** `pocketbase.py` (cliente: `iniciar_sesion`, `registrar`, errores propios `CredencialesInvalidas`, `EmailEnUso`, `ServicioNoDisponible`, `ErrorDeRegistro`) y `pantallas.py` (frames de inicio de sesión y registro). Validaciones de formulario como funciones puras en `logica.py` para probarlas sin GUI.
- **Navegación con frames en una sola ventana raíz.** `app.py` crea la ventana y alterna entre los frames Login, Registro y Conversor (el conversor actual se extrae a un `Frame`). Alternativa: ventanas `Toplevel` separadas; descartado porque complica el foco y el cierre.
- **Estado de sesión en memoria.** Tras autenticar, la app guarda el email del usuario solo mientras dura la sesión; "Cerrar sesión" lo descarta. Sin archivo de sesión (ver Non-Goals).
- **URL de PocketBase** desde `COTIZADOR_PB_URL`, con valor por defecto `http://127.0.0.1:8090`; timeout de 5 s por llamada.
- **Llamadas bloqueantes en el hilo de la interfaz**, con timeout corto y botón deshabilitado mientras dura la llamada. Alternativa: hilos; innecesario en un servidor local.
- **Mapeo de errores:** HTTP 400 en autenticación → credenciales inválidas; HTTP 400 en registro con error de campo `email` (`validation_not_unique`) → email en uso, cualquier otro 400 → mensaje de validación; falla de red o timeout → servicio no disponible.
- **Colección `users` por defecto.** Su regla de creación por defecto permite registro público; se verifica en la implementación y, si estuviera restringida, se ajusta desde el panel (cambio de configuración de PocketBase, no de código).

## Risks / Trade-offs

- [PocketBase debe estar corriendo para usar la app; el .exe ya no es autosuficiente] → mensaje claro de servicio no disponible y README con el comando para levantarlo.
- [Contraseñas viajan por HTTP en `127.0.0.1`] → aceptable en local; para otra máquina se debería usar HTTPS (fuera de alcance).
- [Cualquiera puede registrarse, porque el registro es público] → es lo pedido; limitar el registro quedaría para otro change.
- [Interfaz bloqueada hasta 5 s si el servidor no responde] → timeout corto y mensaje de reintento.
