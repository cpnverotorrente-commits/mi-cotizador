# Proposal

## Why

Hoy el usuario tiene que averiguar la cotización del dólar y escribirla a mano cada vez. Una cotización oficial actualizada que se cargue sola ahorra ese paso y reduce errores de tipeo.

## What Changes

- Al abrirse el conversor, la app consulta la cotización del dólar oficial en `https://dolarapi.com/v1/dolares/oficial` y la carga en el campo de cotización.
- Un botón **"Actualizar cotización"** vuelve a consultarla cuando el usuario quiera.
- Junto al campo se muestra de dónde viene el valor y a qué fecha corresponde (por ejemplo "Dólar oficial (venta) al 16/11/2026 15:00").
- La consulta no bloquea la ventana: mientras se espera la respuesta se muestra "Actualizando…" y los botones relevantes quedan deshabilitados.
- Si la consulta falla (sin internet, servicio caído, respuesta inválida), la app avisa, conserva el valor que hubiera en el campo y deja ingresar la cotización a mano, como hasta ahora.
- El campo de cotización sigue siendo editable: el usuario puede cambiar el valor cargado.

Supuestos registrados:
- Se usa el precio de **venta** del dólar oficial, porque es el que paga quien compra dólares con pesos; la etiqueta lo indica.
- "Al abrirse" significa cada vez que se muestra el conversor (después de iniciar sesión y al volver desde el historial o el panel), porque la pantalla inicial es el inicio de sesión y esa consulta es pública y no necesita cuenta.
- Actualizar reemplaza lo que el usuario haya escrito en el campo de cotización.
- No se guarda la cotización entre aperturas ni se consulta periódicamente.
- Se usa una sola fuente (dolarapi.com), sin respaldo con otra.
- La consulta no envía ningún dato del usuario, solo un pedido GET.

Fuera de alcance: elegir otro tipo de dólar (blue, MEP, etc.), usar el precio de compra, actualizar automáticamente cada cierto tiempo, caché local, guardar en el historial de dónde vino la cotización.

## Capabilities

### New Capabilities
- `automatic-exchange-rate`: obtención de la cotización del dólar oficial desde un servicio externo al abrir el conversor y a pedido, con indicación de origen y fecha y manejo de fallas.

### Modified Capabilities
- `currency-conversion`: la ventana del conversor ya no se abre con la cotización vacía, sino con la cotización automática cargada o, si falla, vacía para ingreso manual; agrega el botón de actualizar.

## Impact

- Código: nuevo módulo `mi_cotizador/cotizacion.py` (cliente HTTP con la biblioteca estándar) y cambios en `Conversor` de `mi_cotizador/app.py`.
- Sin dependencias nuevas. La app necesita acceso a internet para esta función; sin él sigue funcionando con ingreso manual.
- Servicio externo: dolarapi.com. Si cambia el formato de su respuesta, la app lo trata como falla y pide ingreso manual.
- Reconstruir `MiCotizador.exe` con `build.bat`.
