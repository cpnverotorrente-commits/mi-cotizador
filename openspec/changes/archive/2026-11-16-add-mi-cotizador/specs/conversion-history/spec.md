# Spec Delta

## Purpose

Conserva un registro persistente, en un archivo de texto legible, de cada conversión realizada con fecha y hora.

## ADDED Requirements

### Requirement: Registro de cada conversión
La aplicación SHALL agregar una línea a `historial.txt` por cada conversión exitosa, con fecha y hora locales, monto en pesos, cotización y resultado en dólares.

#### Scenario: Conversión exitosa
- **WHEN** el usuario realiza una conversión válida
- **THEN** se agrega al final de `historial.txt` una línea como `2026-11-16 14:32:05 | 100000.00 ARS | cotización 1000.00 | 100.00 USD`

#### Scenario: Conversión inválida
- **WHEN** la validación rechaza las entradas
- **THEN** no se agrega ninguna línea a `historial.txt`

### Requirement: Historial acumulativo
La aplicación SHALL crear `historial.txt` si no existe y conservar las líneas anteriores entre ejecuciones, sin sobrescribirlas.

#### Scenario: Varias ejecuciones
- **WHEN** el usuario cierra la aplicación, la abre de nuevo y hace otra conversión
- **THEN** `historial.txt` contiene las líneas de ambas sesiones en orden cronológico

### Requirement: Ubicación del historial
`historial.txt` SHALL guardarse en la misma carpeta que la aplicación, tanto al ejecutar el script como el ejecutable.

#### Scenario: Ejecución del ejecutable
- **WHEN** el usuario ejecuta `MiCotizador.exe` desde su carpeta y hace una conversión
- **THEN** `historial.txt` aparece junto a `MiCotizador.exe`

### Requirement: Fallo al escribir el historial
Si no se puede escribir en `historial.txt`, la aplicación SHALL mostrar igualmente el resultado y avisar del error de guardado.

#### Scenario: Carpeta sin permisos de escritura
- **WHEN** la carpeta no permite escribir y el usuario convierte un monto válido
- **THEN** se muestra el resultado y un aviso de que no se pudo guardar en el historial
