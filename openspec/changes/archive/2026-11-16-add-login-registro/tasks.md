# Tasks

## 1. Validaciones de formulario

- [x] 1.1 Agregar en `mi_cotizador/logica.py` las validaciones de inicio de sesión (campos completos) y de registro (campos completos, formato de email, contraseña de 8 o más caracteres, confirmación igual) con mensajes en español; verificar con tests unitarios nuevos en `mi_cotizador/tests/test_validaciones.py` (`python -m unittest discover -s mi_cotizador/tests -t .` pasa)

## 2. Cliente de PocketBase

- [x] 2.1 Crear `mi_cotizador/pocketbase.py` con `iniciar_sesion` y `registrar` sobre `urllib`, URL desde `COTIZADOR_PB_URL` (por defecto `http://127.0.0.1:8090`), timeout de 5 s y los errores `CredencialesInvalidas`, `EmailEnUso`, `ErrorDeRegistro` y `ServicioNoDisponible`; verificar con tests unitarios que simulan las respuestas HTTP (200, 400 de credenciales, 400 `validation_not_unique`, red caída) sin servidor real
- [x] 2.2 Verificar contra el PocketBase local que la colección `users` permite registro público: registrar un usuario de prueba, iniciar sesión con él y comprobar que un email repetido da `EmailEnUso`; luego borrar el usuario de prueba desde el panel

## 3. Pantallas y navegación

- [x] 3.1 Crear `mi_cotizador/pantallas.py` con los frames de inicio de sesión y registro (mensajes de error, enlace entre ambos, botón deshabilitado durante la llamada) conectados a las validaciones y al cliente; verificar abriendo la app y recorriendo a mano: login vacío, credenciales erróneas, registro con confirmación distinta, registro exitoso que vuelve al login con mensaje
- [x] 3.2 Refactorizar `mi_cotizador/app.py` para que el conversor sea un frame, la app abra primero el inicio de sesión y solo muestre el conversor tras autenticar, con botón "Cerrar sesión"; verificar que el conversor no aparece sin login, que cerrar sesión vuelve al login y que convertir sigue escribiendo `historial.txt`
- [x] 3.3 Verificar con PocketBase apagado que login y registro muestran "servicio no disponible" sin cerrar la app, y que al encenderlo se puede reintentar

## 4. Documentación y ejecutable

- [x] 4.1 Actualizar `README.md` con el requisito de PocketBase corriendo, la variable `COTIZADOR_PB_URL` y cómo registrarse; verificar que los comandos documentados se ejecutan tal cual
- [x] 4.2 Reconstruir con `build.bat` y verificar que `dist/MiCotizador.exe` abre en la pantalla de inicio de sesión, permite iniciar sesión con un usuario real y llegar al conversor

## Workflow follow-up

- Archivar `add-mi-cotizador` antes que este change, para que sus specs pasen a `openspec/specs/`.
- Archivar este change tras revisar la implementación.
