"""Parseo, validación y conversión de pesos a dólares."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


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
