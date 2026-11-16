# Tasks

## 1. Configuración de PocketBase

- [x] 1.1 Crear `scripts/configurar_pocketbase.py` (credenciales del superusuario por `PB_SUPERUSER_EMAIL` y `PB_SUPERUSER_PASSWORD`) que agregue los campos `rol` y `desactivado` a `users`, cree o promueva a admin el email dado con `--admin`; verificar ejecutándolo contra el PocketBase local y consultando la colección con el superusuario
- [x] 1.2 Aplicar en el mismo script las reglas de `listRule`, `viewRule`, `createRule`, `updateRule`, `deleteRule`, `authRule` y `manageRule` del diseño, en ese orden después de los campos; verificar que ejecutarlo dos veces seguidas termina sin errores y deja la misma configuración
- [x] 1.3 Verificar las reglas contra el servidor real con usuario común, admin y sin sesión: la lista sin sesión no devuelve cuentas, el usuario común ve solo la suya y no puede cambiar su rol ni estado ni tocar otra cuenta, el registro con `rol` forzado es rechazado, el admin lista y modifica todas y la cuenta desactivada no inicia sesión; confirmar también que el admin puede cambiar la contraseña de otra cuenta sin `oldPassword`, y borrar las cuentas de prueba al terminar

## 2. Cliente de PocketBase

- [x] 2.1 Extender `mi_cotizador/pocketbase.py` para que `iniciar_sesion` devuelva email, rol (vacío como `usuario`) y token en una sesión en memoria, y para que una cuenta desactivada se reporte con mensaje claro; verificar con tests unitarios con respuestas HTTP simuladas (admin, usuario, rol vacío, cuenta desactivada) y los tests existentes siguen pasando
- [x] 2.2 Agregar `listar_usuarios`, `cambiar_desactivada` y `resetear_clave` con el token de la sesión y el error `NoAutorizado`; verificar con tests unitarios simulados (lista, cambio de estado, reseteo, 403, servidor caído)

## 3. Validaciones

- [x] 3.1 Agregar en `mi_cotizador/logica.py` la validación de contraseña nueva con confirmación (mínimo 8) y la regla de que un admin no puede desactivarse a sí mismo; verificar con tests unitarios

## 4. Panel y navegación

- [x] 4.1 Crear el panel de administración (lista con email, rol y estado, actualizar, Activar/Desactivar con confirmación, diálogo de contraseña nueva, acciones deshabilitadas sin selección, mensajes de error) conectado al cliente y a las validaciones; verificar recorriéndolo contra el PocketBase real: listar, desactivar y reactivar una cuenta de prueba, resetear su contraseña y comprobar que la anterior ya no entra
- [x] 4.2 Hacer que `mi_cotizador/app.py` muestre el panel a admins y el conversor a usuarios comunes, con "Abrir conversor", "Volver al panel" y "Cerrar sesión"; verificar los tres recorridos (admin, usuario, cuenta desactivada) y que PocketBase apagado muestra el error sin cerrar la app

## 5. Documentación y ejecutable

- [x] 5.1 Documentar en `README.md` el script de configuración, las variables de entorno, cómo crear el primer admin y el comportamiento del panel; verificar que los comandos documentados se ejecutan tal cual
- [x] 5.2 Reconstruir con `build.bat` y verificar que `dist/MiCotizador.exe` abre, que un admin ve el panel y que un usuario común va al conversor

## Workflow follow-up

- Archivar `add-mi-cotizador` y `add-login-registro`, en ese orden, antes de este change.
- Archivar este change tras revisar la implementación.
