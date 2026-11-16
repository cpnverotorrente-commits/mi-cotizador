# Design

## Context

El conversor es el frame `Conversor` de `mi_cotizador/app.py`, que ya tiene un campo de cotización vacío y un botón Convertir. La app usa solo la biblioteca estándar. Motivación y alcance: ver proposal.md; requisitos en specs/automatic-exchange-rate y specs/currency-conversion.

La API (`GET https://dolarapi.com/v1/dolares/oficial`) devuelve JSON con `compra`, `venta` (números) y `fechaActualizacion` (ISO 8601 en UTC), verificado con una consulta real.

## Goals / Non-Goals

**Goals:**
- Cliente aislado y probable sin red, y una interfaz que nunca se congele.
- Tratar cualquier respuesta inesperada como falla recuperable.

**Non-Goals:**
- Otras fuentes de datos, otros tipos de dólar, caché o actualización periódica.

## Decisions

- **Módulo `mi_cotizador/cotizacion.py`** con `obtener_cotizacion(abrir=urllib.request.urlopen)`, que devuelve un `Cotizacion(venta: Decimal, fecha: str)` o lanza `CotizacionNoDisponible` con mensaje apto para mostrar. Misma técnica de inyección de `abrir` que `pocketbase.py` para probarlo sin red.
- **URL fija** `https://dolarapi.com/v1/dolares/oficial` como constante, con timeout de 5 s y encabezado `User-Agent: MiCotizador`. Alternativa: URL configurable por variable de entorno; descartada por no ser necesaria (el pedido nombra la dirección). Sin cabeceras de autorización ni cuerpo: no viaja ningún dato del usuario.
- **Validación estricta de la respuesta:** JSON objeto, `venta` presente, convertible con `Decimal(str(valor))`, finito y mayor que cero; si no, falla. Se usa `venta` (supuesto del proposal). La fecha se toma de `fechaActualizacion` y se muestra con `formato_fecha_local` ya existente; si falta o no se puede interpretar, se omite de la etiqueta sin fallar.
- **Consulta en un hilo de fondo.** Un `threading.Thread` ejecuta `obtener_cotizacion` y deja el resultado (cotización o error) en una `queue.Queue`; la interfaz lo revisa con `after(100, ...)`. Tkinter no es seguro entre hilos, por eso el hilo nunca toca widgets. Alternativa: consulta bloqueante con timeout de 5 s; descartada porque congelaría la ventana hasta 5 s al abrir sin internet.
- **Estado de la consulta en `Conversor`:** una bandera `consultando` evita consultas simultáneas y deshabilita el botón "Actualizar cotización"; al terminar se vuelve a habilitar. Si el frame se destruye mientras la consulta sigue en curso, el sondeo con `after` se cancela y el resultado se descarta.
- **Carga del campo:** el valor se escribe con coma decimal solo si tiene decimales (`1575` o `1575,5`), formato que el parser existente ya acepta. Una falla no toca el campo.
- **Etiqueta informativa** bajo el campo con el texto "Dólar oficial (venta) · actualizado dd/mm/aaaa hh:mm"; en falla se muestra el aviso en rojo en su lugar.
- **Se consulta cada vez que se crea el `Conversor`.** Como la app no guarda el valor entre pantallas, volver del historial o del panel lo vuelve a consultar; es una consulta liviana y evita una caché.
- **Para probar la interfaz sin red**, `Conversor` recibe la función de consulta como parámetro con `obtener_cotizacion` por defecto.

## Risks / Trade-offs

- [El servicio externo cae o cambia el formato] → toda anomalía es una falla recuperable y el ingreso manual sigue funcionando.
- [Sin internet cada apertura del conversor espera hasta 5 s por el timeout] → ocurre en segundo plano y la ventana responde; el aviso aparece al terminar.
- [El valor cargado reemplaza lo que el usuario había escrito al pulsar Actualizar] → es el comportamiento pedido y queda documentado en el proposal.
- [El resultado de un hilo llega después de cerrar la pantalla] → se cancela el sondeo y se descarta.
- [Dependencia de un tercero para un dato financiero] → la etiqueta indica origen y fecha para que el usuario pueda juzgar si está desactualizado.
