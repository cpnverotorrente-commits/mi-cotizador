# Spec Delta

## Purpose

Carga automáticamente la cotización del dólar oficial en el conversor y permite actualizarla a pedido, sin impedir el ingreso manual cuando el servicio no está disponible.

## ADDED Requirements

### Requirement: Cotización automática al abrir el conversor
Al mostrarse el conversor, la aplicación SHALL consultar la cotización de venta del dólar oficial en `https://dolarapi.com/v1/dolares/oficial` y cargarla en el campo de cotización.

#### Scenario: Consulta exitosa
- **WHEN** el usuario abre el conversor y el servicio responde con un precio de venta de 1575
- **THEN** el campo de cotización muestra 1575 sin que el usuario escriba nada

### Requirement: Botón de actualización
El conversor SHALL ofrecer un botón "Actualizar cotización" que repite la consulta y reemplaza el valor del campo de cotización por el obtenido.

#### Scenario: Actualizar
- **WHEN** el usuario cambia el campo de cotización a mano y pulsa "Actualizar cotización"
- **THEN** el campo vuelve a mostrar la cotización obtenida del servicio

### Requirement: Origen y fecha de la cotización
Tras una consulta exitosa, el conversor SHALL indicar que el valor es el precio de venta del dólar oficial y la fecha y hora de actualización informadas por el servicio, en hora local.

#### Scenario: Etiqueta informativa
- **WHEN** la consulta termina bien
- **THEN** junto al campo se lee que es el dólar oficial (venta) con su fecha y hora de actualización

### Requirement: Consulta sin bloquear la ventana
La aplicación SHALL realizar la consulta sin congelar la ventana, mostrando un indicador de actualización y evitando consultas simultáneas.

#### Scenario: Consulta en curso
- **WHEN** hay una consulta en curso
- **THEN** se muestra un indicador de actualización, el botón "Actualizar cotización" está deshabilitado y la ventana sigue respondiendo

### Requirement: Falla de la consulta
Si el servicio no responde, no hay internet o la respuesta no trae un precio de venta numérico positivo, la aplicación SHALL avisar con un mensaje claro, conservar el valor que hubiera en el campo de cotización y permitir ingresarlo a mano.

#### Scenario: Sin conexión
- **WHEN** el usuario abre el conversor sin acceso al servicio
- **THEN** se muestra un aviso de que no se pudo obtener la cotización, el campo queda editable y el usuario puede convertir ingresando la cotización a mano

#### Scenario: Respuesta inválida
- **WHEN** el servicio responde con un precio de venta ausente, no numérico o menor o igual a cero
- **THEN** se trata como una falla y no se modifica el campo de cotización

#### Scenario: Reintento
- **WHEN** una consulta falló y el usuario pulsa "Actualizar cotización" con el servicio ya disponible
- **THEN** el campo se completa con la cotización obtenida y el aviso de error desaparece

### Requirement: Datos del usuario protegidos
La consulta de la cotización SHALL NOT enviar al servicio externo ningún dato de la cuenta ni de las conversiones del usuario.

#### Scenario: Contenido del pedido
- **WHEN** la aplicación consulta la cotización
- **THEN** envía únicamente un pedido GET a la dirección del servicio, sin credenciales ni datos del usuario
