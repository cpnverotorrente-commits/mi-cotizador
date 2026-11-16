"""Registro de conversiones en historial.txt."""
import sys
from datetime import datetime
from pathlib import Path

NOMBRE = "historial.txt"


def carpeta_base():
    """Carpeta del ejecutable (congelado) o de la raíz del proyecto."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def guardar(monto, cotizacion, dolares, carpeta=None, ahora=None):
    """Agrega una línea al historial. Lanza OSError si no se puede escribir."""
    ahora = ahora or datetime.now()
    linea = (
        f"{ahora:%Y-%m-%d %H:%M:%S} | {monto} ARS | "
        f"cotización {cotizacion} | {dolares} USD\n"
    )
    ruta = Path(carpeta or carpeta_base()) / NOMBRE
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(linea)
    return ruta
