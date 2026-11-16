# currency-conversion Specification

## Purpose
Permite convertir un monto en pesos a dólares usando una cotización ingresada por el usuario, mostrando el resultado en la ventana de la aplicación.

## Requirements

### Requirement: Ventana de la aplicación
La aplicación SHALL mostrar una ventana titulada "Mi Cotizador" con un campo para el monto en pesos, un campo para la cotización del dólar (pesos por 1 USD), un botón "Convertir" y un área de resultado.

#### Scenario: Apertura de la aplicación
- **WHEN** el usuario abre Mi Cotizador
- **THEN** se muestra la ventana con ambos campos vacíos, el botón "Convertir" y el área de resultado vacía

### Requirement: Conversión de pesos a dólares
Al pulsar "Convertir", la aplicación SHALL calcular el monto en pesos dividido por la cotización y mostrar el resultado en dólares con dos decimales.

#### Scenario: Conversión válida
- **WHEN** el usuario ingresa monto 100000 y cotización 1000 y pulsa "Convertir"
- **THEN** se muestra un resultado de 100,00 USD

#### Scenario: Redondeo a dos decimales
- **WHEN** el usuario ingresa monto 1000 y cotización 3 y pulsa "Convertir"
- **THEN** se muestra un resultado de 333,33 USD

### Requirement: Formato numérico de entrada
Los campos numéricos SHALL aceptar números con punto o coma como separador decimal.

#### Scenario: Coma decimal
- **WHEN** el usuario ingresa monto 1500,50 y cotización 1000 y pulsa "Convertir"
- **THEN** se muestra un resultado de 1,50 USD

### Requirement: Validación de entradas
La aplicación SHALL rechazar entradas vacías, no numéricas, o con monto negativo o cotización menor o igual a cero, mostrando un mensaje de error claro y sin mostrar un resultado.

#### Scenario: Campo vacío o con texto
- **WHEN** el usuario pulsa "Convertir" con un campo vacío o con texto no numérico
- **THEN** se muestra un mensaje de error indicando que ingrese números válidos y no se calcula resultado

#### Scenario: Cotización cero
- **WHEN** el usuario ingresa cotización 0 y pulsa "Convertir"
- **THEN** se muestra un mensaje de error indicando que la cotización debe ser mayor que cero
