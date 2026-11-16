# Proposal

## Why

Convertir un monto en pesos a dólares usando una cotización que el usuario define requiere hoy una calculadora o una planilla, y no deja registro de las conversiones. Una aplicación de escritorio simple, que se pueda abrir con doble clic y sin instalar Python, resuelve esto y guarda un historial.

## What Changes

- Nueva aplicación de escritorio en Python llamada **Mi Cotizador** (el proyecto está vacío; es greenfield).
- Ventana con un campo de monto en pesos, un campo de cotización del dólar (pesos por dólar) y un botón **Convertir** que muestra el resultado en dólares.
- Cada conversión exitosa se agrega, con fecha y hora, a un archivo `historial.txt`.
- Se genera un ejecutable para Windows (`MiCotizador.exe`) sin consola.

Supuestos registrados: la cotización es el precio de 1 USD en pesos (resultado = pesos / cotización); la cotización se ingresa a mano, sin consulta a internet; el ejecutable es solo para Windows 10, el sistema del usuario; `historial.txt` se guarda junto al ejecutable.

Fuera de alcance: cotización automática online, conversión inversa (USD a pesos), pantalla para ver o borrar el historial, instalador, otros sistemas operativos.

## Capabilities

### New Capabilities
- `currency-conversion`: ingreso de monto en pesos y cotización, conversión a dólares, validación de entradas y visualización del resultado.
- `conversion-history`: registro persistente de cada conversión, con fecha y hora, en `historial.txt`.
- `desktop-packaging`: distribución de la aplicación como ejecutable de Windows independiente.

### Modified Capabilities

## Impact

- Código nuevo: módulo de la aplicación en Python (interfaz con Tkinter, de la biblioteca estándar).
- Dependencias: Python 3 (no está instalado en esta máquina) y PyInstaller solo para construir el ejecutable.
- Archivos generados: `historial.txt` en tiempo de ejecución; carpeta `dist/` con `MiCotizador.exe`.
