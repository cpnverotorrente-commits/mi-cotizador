# Spec Delta

## MODIFIED Requirements

### Requirement: Ventana de la aplicación
La aplicación SHALL mostrar una ventana titulada "Mi Cotizador" con un campo para el monto en pesos, un campo para la cotización del dólar (pesos por 1 USD) que se carga con la cotización automática cuando está disponible, un botón "Actualizar cotización", un botón "Convertir" y un área de resultado.

#### Scenario: Apertura de la aplicación
- **WHEN** el usuario abre Mi Cotizador
- **THEN** se muestra la ventana con el campo de monto vacío, el campo de cotización cargado con la cotización automática (o vacío si no se pudo obtener), los botones "Actualizar cotización" y "Convertir" y el área de resultado vacía
