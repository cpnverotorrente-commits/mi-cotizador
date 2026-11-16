@echo off
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --name MiCotizador main.py
echo.
echo Listo: dist\MiCotizador.exe
