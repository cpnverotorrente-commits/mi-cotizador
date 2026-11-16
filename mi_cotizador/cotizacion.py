"""Cotización del dólar oficial desde dolarapi.com (precio de venta)."""
import json
import urllib.request
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

URL = "https://dolarapi.com/v1/dolares/oficial"
TIMEOUT = 5
MENSAJE_FALLA = "No se pudo obtener la cotización automática. Ingresala a mano o probá de nuevo."


class CotizacionNoDisponible(Exception):
    """No se pudo obtener una cotización válida; el mensaje es apto para mostrar."""


@dataclass(frozen=True)
class Cotizacion:
    venta: Decimal
    fecha: str  # fecha y hora de actualización en UTC, tal como la informa el servicio ('' si no vino)


def obtener_cotizacion(abrir=urllib.request.urlopen):
    """Consulta el precio de venta del dólar oficial. Solo envía un GET, sin datos del usuario."""
    pedido = urllib.request.Request(
        URL,
        headers={"User-Agent": "MiCotizador", "Accept": "application/json"},
        method="GET",
    )
    try:
        with abrir(pedido, timeout=TIMEOUT) as r:
            datos = json.loads(r.read().decode("utf-8"))
    except (OSError, ValueError):
        raise CotizacionNoDisponible(MENSAJE_FALLA) from None
    if not isinstance(datos, dict):
        raise CotizacionNoDisponible(MENSAJE_FALLA)
    bruto = datos.get("venta")
    if isinstance(bruto, bool) or not isinstance(bruto, (int, float, str)):
        raise CotizacionNoDisponible(MENSAJE_FALLA)
    try:
        venta = Decimal(str(bruto))
    except InvalidOperation:
        raise CotizacionNoDisponible(MENSAJE_FALLA) from None
    if not venta.is_finite() or venta <= 0:
        raise CotizacionNoDisponible(MENSAJE_FALLA)
    fecha = datos.get("fechaActualizacion")
    return Cotizacion(venta, fecha if isinstance(fecha, str) else "")


def texto_para_campo(venta):
    """1575 -> '1575'; 1575.5 -> '1575,5' (coma decimal, que el conversor ya acepta)."""
    redondeado = venta.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    texto = format(redondeado, "f")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto.replace(".", ",")
