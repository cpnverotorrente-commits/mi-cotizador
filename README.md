# Mi Cotizador

Aplicación de escritorio (Python + Tkinter) que convierte un monto en pesos a dólares con la cotización que ingreses. Cada conversión se guarda con fecha y hora en `historial.txt`, junto a la aplicación.

## Ejecutar desde el código

```
python main.py
```

## Pruebas

```
python -m unittest discover -s mi_cotizador/tests -t .
```

## Generar el ejecutable (Windows)

```
build.bat
```

Crea `dist\MiCotizador.exe`, que funciona sin Python instalado. Algunos antivirus pueden marcar con falsos positivos los ejecutables de PyInstaller.
