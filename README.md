# Mi Cotizador

Aplicación de escritorio (Python + Tkinter) que convierte un monto en pesos a dólares. La cotización del dólar oficial se carga sola al abrir el conversor y se puede cambiar a mano. Cada conversión se guarda con fecha y hora en PocketBase, a nombre del usuario que la hizo, y cada usuario ve solo su historial.

Para usarla hay que iniciar sesión: los usuarios se guardan en PocketBase. Los usuarios con rol `admin` ven además un panel para administrar cuentas.

## Requisito: PocketBase en marcha

```
pocketbase\pocketbase.exe serve
```

Por defecto la app se conecta a `http://127.0.0.1:8090`. Para usar otra dirección, definí la variable de entorno `COTIZADOR_PB_URL` antes de abrir la app.

El primer superusuario del panel de PocketBase (`http://127.0.0.1:8090/_/`) se crea con:

```
pocketbase\pocketbase.exe superuser upsert tu@email.com TuContraseña
```

## Roles y panel de administración

Los usuarios tienen un rol (`usuario` por defecto, o `admin`) y pueden estar desactivados. Los permisos los impone PocketBase con reglas de acceso, no solo la app: un usuario común solo ve y edita su propia cuenta, no puede cambiarse el rol ni el estado, y el registro público no puede crear admins.

Configuración (una vez, con PocketBase en marcha). Agrega los campos `rol` y `desactivado`, crea la colección `consultas` del historial, aplica las reglas y deja a un usuario como admin. Es seguro ejecutarlo varias veces:

```
$env:PB_SUPERUSER_EMAIL = "tu@email.com"
$env:PB_SUPERUSER_PASSWORD = "contraseña-del-superusuario"
python scripts\configurar_pocketbase.py --admin admin@ejemplo.com
```

- Si `admin@ejemplo.com` ya se registró en la app, queda promovido a admin.
- Si no existe, se crea con la contraseña de la variable `PB_ADMIN_PASSWORD` (mínimo 8 caracteres).

Panel (se abre al iniciar sesión un admin): lista las cuentas con email, rol y estado; permite **Desactivar/Activar** (una cuenta desactivada no puede iniciar sesión; un admin no puede desactivarse a sí mismo) y **Resetear contraseña** (el admin escribe una contraseña nueva de al menos 8 caracteres; no se envía mail). Desde el panel se puede abrir el conversor y volver.

Verificación de las reglas contra el PocketBase real (crea cuentas de prueba y las borra): definí además `PB_ADMIN_EMAIL` y `PB_ADMIN_PASSWORD` de un admin y ejecutá `python scripts\verificar_reglas.py`.

## Cotización automática

Al mostrarse el conversor (después de iniciar sesión y al volver del historial o del panel), la app consulta el precio de **venta** del dólar oficial en `https://dolarapi.com/v1/dolares/oficial` y lo carga en el campo de cotización, con una etiqueta que indica el origen y la fecha de actualización. El botón **"Actualizar cotización"** repite la consulta y reemplaza lo que hubiera en el campo.

La consulta se hace en segundo plano (la ventana no se congela) y solo envía un pedido GET: no viaja ningún dato tuyo. Si no hay internet, el servicio no responde o la respuesta no es válida, la app avisa, conserva el valor del campo y podés ingresar la cotización a mano.

Prueba de esta función (con la red real y consultas falsas): `python scripts\probar_gui_cotizacion.py`.

## Historial de conversiones

Cada conversión exitosa se guarda en la colección `consultas` de PocketBase (usuario, monto, cotización, resultado y fecha y hora, esta última fijada por el servidor). Las reglas de PocketBase hacen que cada usuario, también un admin, vea solo sus propias consultas, que solo pueda crearlas a su nombre y que nadie pueda editarlas ni borrarlas (solo un superusuario desde el panel de PocketBase). Se ven en el botón "Mi historial" del conversor (últimas 200, la más reciente primero).

Si PocketBase no responde al convertir, la app muestra igualmente el resultado y avisa que no se guardó; no hay respaldo local. La app ya no escribe `historial.txt`: si tenés uno de versiones anteriores, no se migra y puede borrarse.

Pruebas contra el PocketBase real (crean cuentas de prueba y las borran): `python scripts\verificar_reglas.py` (con `PB_ADMIN_EMAIL` y `PB_ADMIN_PASSWORD` de un admin) y `python scripts\probar_gui_historial.py`.

## Usar la app

1. Abrí la app (`python main.py` o `dist\MiCotizador.exe`).
2. Si no tenés cuenta, pulsá "¿No tenés cuenta? Registrate", completá email y contraseña (mínimo 8 caracteres) y pulsá "Registrarme".
3. Iniciá sesión: se abre el conversor (o el panel, si sos admin). "Mi historial" muestra tus conversiones. "Cerrar sesión" vuelve al inicio de sesión. La sesión no se recuerda al cerrar la app.

## Pruebas

```
python -m unittest discover -s mi_cotizador/tests -t .
```

## Generar el ejecutable (Windows)

```
build.bat
```

Crea `dist\MiCotizador.exe`, que funciona sin Python instalado pero necesita PocketBase en marcha. Algunos antivirus pueden marcar con falsos positivos los ejecutables de PyInstaller.
