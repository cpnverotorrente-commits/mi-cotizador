# Tasks

## 1. Entorno

- [x] 1.1 Instalar Python 3 con winget (`winget install Python.Python.3.12`) y verificar que `python --version` responde en una terminal nueva
- [x] 1.2 Crear la carpeta `mi_cotizador/` con `__init__.py` y `tests/`, e instalar PyInstaller (`pip install pyinstaller`); verificar con `pyinstaller --version`

## 2. Lógica de conversión

- [x] 2.1 Implementar en `mi_cotizador/logica.py` el parseo (coma o punto), la validación y la conversión con `Decimal`, y verificar con tests unitarios (`python -m unittest`) que cubren 100000/1000 = 100,00, 1000/3 = 333,33, coma decimal, campo vacío, texto, monto negativo y cotización 0

## 3. Historial

- [x] 3.1 Implementar en `mi_cotizador/historial.py` el guardado en modo append, UTF-8, en la carpeta del script o del ejecutable, con el formato de línea del diseño; verificar con tests unitarios sobre una carpeta temporal: creación del archivo, acumulación entre llamadas y error controlado si no se puede escribir

## 4. Interfaz

- [x] 4.1 Implementar en `mi_cotizador/app.py` la ventana Tkinter "Mi Cotizador" con los dos campos, el botón "Convertir", el área de resultado y los mensajes de error, conectada a la lógica y al historial (no registra en caso de error, avisa si falla el guardado); verificar ejecutando `python -m mi_cotizador.app` y haciendo una conversión válida y una inválida a mano, comprobando `historial.txt`
- [x] 4.2 Documentar el uso y la construcción en `README.md`; verificar que los comandos documentados se ejecutan tal cual

## 5. Ejecutable

- [x] 5.1 Crear `build.bat` con `pyinstaller --onefile --windowed --name MiCotizador` y ejecutarlo; verificar que existe `dist/MiCotizador.exe`
- [x] 5.2 Ejecutar `dist/MiCotizador.exe` desde otra carpeta: verificar que abre sin consola, que convierte y que `historial.txt` aparece junto al `.exe`

## Workflow follow-up

- Archivar el change (`openspec-archive-change`) una vez revisada la implementación.
