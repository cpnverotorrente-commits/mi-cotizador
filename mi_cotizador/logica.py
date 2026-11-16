"""Parseo, validación y conversión de pesos a dólares."""
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")
MIN_CLAVE = 8
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EntradaInvalida(ValueError):
    """Entrada del usuario no válida; el mensaje es apto para mostrar."""


def parsear_numero(texto, nombre):
    limpio = (texto or "").strip().replace(",", ".")
    if not limpio:
        raise EntradaInvalida(f"Ingresá un número válido en {nombre}.")
    try:
        valor = Decimal(limpio)
    except InvalidOperation:
        raise EntradaInvalida(f"Ingresá un número válido en {nombre}.") from None
    if not valor.is_finite():
        raise EntradaInvalida(f"Ingresá un número válido en {nombre}.")
    return valor


def convertir(monto_texto, cotizacion_texto):
    """Devuelve (monto, cotización, dólares) como Decimal redondeados a 2 decimales."""
    monto = parsear_numero(monto_texto, "el monto")
    cotizacion = parsear_numero(cotizacion_texto, "la cotización")
    if monto < 0:
        raise EntradaInvalida("El monto no puede ser negativo.")
    if cotizacion <= 0:
        raise EntradaInvalida("La cotización debe ser mayor que cero.")
    dolares = (monto / cotizacion).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    return (
        monto.quantize(CENTAVOS, rounding=ROUND_HALF_UP),
        cotizacion.quantize(CENTAVOS, rounding=ROUND_HALF_UP),
        dolares,
    )


def validar_login(email, clave):
    """Devuelve (email, clave) limpios o lanza EntradaInvalida."""
    email = (email or "").strip()
    if not email or not clave:
        raise EntradaInvalida("Completá el email y la contraseña.")
    return email, clave


def validar_registro(email, clave, confirmacion):
    """Devuelve (email, clave) limpios o lanza EntradaInvalida."""
    email = (email or "").strip()
    if not email or not clave or not confirmacion:
        raise EntradaInvalida("Completá todos los campos.")
    if not _EMAIL.match(email):
        raise EntradaInvalida("Ingresá un email válido.")
    if len(clave) < MIN_CLAVE:
        raise EntradaInvalida(f"La contraseña debe tener al menos {MIN_CLAVE} caracteres.")
    if clave != confirmacion:
        raise EntradaInvalida("La contraseña y su confirmación no coinciden.")
    return email, clave


def validar_clave_nueva(clave, confirmacion):
    """Valida la contraseña que un admin asigna a otra cuenta; devuelve la contraseña."""
    if not clave or not confirmacion:
        raise EntradaInvalida("Completá la contraseña y su confirmación.")
    if len(clave) < MIN_CLAVE:
        raise EntradaInvalida(f"La contraseña debe tener al menos {MIN_CLAVE} caracteres.")
    if clave != confirmacion:
        raise EntradaInvalida("La contraseña y su confirmación no coinciden.")
    return clave


def puede_desactivar(id_cuenta, id_admin):
    """Un admin no puede desactivar su propia cuenta."""
    return id_cuenta != id_admin


def formato_numero(valor):
    """1234.5 -> '1.234,50' (separador de miles con punto, decimal con coma)."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formato_fecha_local(fecha_utc):
    """'2026-11-16 18:00:00.000Z' (UTC, como la entrega PocketBase) -> 'dd/mm/aaaa hh:mm:ss' en hora local."""
    from datetime import datetime

    try:
        momento = datetime.fromisoformat(fecha_utc.strip().replace(" ", "T").replace("Z", "+00:00"))
        if momento.tzinfo is None:
            raise ValueError
        return momento.astimezone().strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, AttributeError):
        return fecha_utc or ""
