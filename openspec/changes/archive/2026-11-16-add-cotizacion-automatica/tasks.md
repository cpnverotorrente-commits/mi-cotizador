# Tasks

## 1. Cliente de la cotización

- [x] 1.1 Crear `mi_cotizador/cotizacion.py` con `obtener_cotizacion`, la validación estricta de la respuesta, timeout de 5 s, `User-Agent` y el error `CotizacionNoDisponible`; verificar con tests unitarios con respuestas simuladas: respuesta válida, `venta` ausente, no numérica, cero o negativa, JSON inválido o no objeto, fecha ausente, HTTP 500 y red caída, y que el pedido es un GET sin cuerpo ni credenciales
- [x] 1.2 Verificar una consulta real a dolarapi.com con el cliente y comprobar que devuelve una `venta` positiva y una fecha interpretable

## 2. Integración en el conversor

- [x] 2.1 Agregar al `Conversor` la consulta en hilo de fondo con cola y sondeo `after`, la etiqueta de origen y fecha, el botón "Actualizar cotización" (deshabilitado durante la consulta), la carga del campo y el manejo de fallas; verificar por código con una función de consulta falsa: carga al abrir, actualizar reemplaza lo escrito, falla conserva el campo y muestra aviso, reintento limpia el aviso, no hay consultas simultáneas y destruir el frame durante la consulta no produce errores
- [x] 2.2 Verificar con la red real y con una dirección imposible de alcanzar (consulta fallida) que la ventana responde durante la espera y que convertir con la cotización cargada sigue guardando la consulta en el historial

## 3. Documentación y ejecutable

- [x] 3.1 Actualizar `README.md` (cotización automática, de dónde viene, botón de actualizar, qué pasa sin internet); verificar que lo documentado coincide con el comportamiento
- [x] 3.2 Reconstruir con `build.bat` (sin instancias de la app abiertas) y verificar que `dist/MiCotizador.exe` abre, que el ejecutable incluye el nuevo módulo y que se ve la cotización cargada

## Workflow follow-up

- Archivar este change tras revisar la implementación; actualiza `currency-conversion` y crea `automatic-exchange-rate`.
