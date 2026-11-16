# Design

## Context

Proyecto greenfield, sin código previo. Python no está instalado en esta máquina (Windows 10), por lo que la implementación debe empezar instalándolo. Motivación y alcance: ver proposal.md.

## Goals / Non-Goals

**Goals:**
- Aplicación pequeña, sin dependencias en tiempo de ejecución.
- Lógica de conversión y de historial separada de la interfaz para poder probarla sin abrir ventanas.

**Non-Goals:**
- Aplicación multiplataforma, instalador, firma de código.

## Decisions

- **Tkinter para la interfaz.** Viene con Python, no agrega dependencias y alcanza para dos campos y un botón. Alternativas: PyQt/PySide (pesadas, licencias y tamaño del ejecutable), Flet/Kivy (dependencias extra sin beneficio).
- **Estructura en tres piezas dentro de `mi_cotizador/`:** `logica.py` (parseo, validación y conversión, funciones puras), `historial.py` (escritura de líneas en `historial.txt`) y `app.py` (ventana Tkinter y punto de entrada). Permite pruebas unitarias con `unittest` sin GUI.
- **Dinero con `Decimal`.** Evita errores de coma flotante; redondeo a 2 decimales con `ROUND_HALF_UP`. Alternativa: `float`, descartado por redondeos inexactos.
- **Parseo de números:** se acepta coma o punto como separador decimal reemplazando la coma por punto; no se admiten separadores de miles (se informa como entrada inválida). Se rechazan `NaN` e infinito.
- **Ubicación del historial:** carpeta del ejecutable (`sys.executable` si `sys.frozen`, si no la carpeta del script). Alternativa: carpeta del usuario, descartada porque el pedido es un `historial.txt` visible junto a la app.
- **Formato de línea:** `YYYY-MM-DD HH:MM:SS | <monto> ARS | cotización <cot> | <usd> USD`, codificación UTF-8, modo append.
- **Empaquetado con PyInstaller** (`--onefile --windowed --name MiCotizador`), envuelto en `build.bat`. Alternativas: cx_Freeze y Nuitka (más configuración o requieren compilador C).

## Risks / Trade-offs

- [Python no instalado] → primera tarea: instalar Python 3 con winget.
- [Antivirus marca falsos positivos en ejecutables de PyInstaller `--onefile`] → documentar el aviso; alternativa `--onedir` si ocurre.
- [Arranque lento del `--onefile`, que se descomprime en cada inicio] → aceptable para esta app.
- [Carpeta del ejecutable sin permisos, por ejemplo Archivos de programa] → la app avisa del fallo de guardado sin perder el resultado (ver spec conversion-history).
