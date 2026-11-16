import io
import json
import unittest
import urllib.error
from decimal import Decimal

from mi_cotizador import cotizacion as cot


class Resp:
    def __init__(self, texto):
        self._t = texto if isinstance(texto, bytes) else texto.encode()

    def read(self):
        return self._t

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def abrir_json(datos):
    return lambda pedido, timeout: Resp(json.dumps(datos))


class TestObtener(unittest.TestCase):
    def test_valida(self):
        r = cot.obtener_cotizacion(abrir_json({"compra": 1525, "venta": 1575, "fechaActualizacion": "2026-11-16T18:00:00.000Z"}))
        self.assertEqual((r.venta, r.fecha), (Decimal("1575"), "2026-11-16T18:00:00.000Z"))

    def test_venta_decimal_y_texto(self):
        self.assertEqual(cot.obtener_cotizacion(abrir_json({"venta": 1575.5})).venta, Decimal("1575.5"))
        self.assertEqual(cot.obtener_cotizacion(abrir_json({"venta": "1575.25"})).venta, Decimal("1575.25"))

    def test_sin_fecha_no_falla(self):
        self.assertEqual(cot.obtener_cotizacion(abrir_json({"venta": 10})).fecha, "")

    def test_respuestas_invalidas(self):
        for datos in ({}, {"venta": None}, {"venta": "abc"}, {"venta": 0}, {"venta": -5},
                      {"venta": True}, {"venta": [1]}, {"venta": "NaN"}, {"venta": "Infinity"},
                      [1, 2], "texto", 5):
            with self.subTest(datos=datos), self.assertRaises(cot.CotizacionNoDisponible):
                cot.obtener_cotizacion(abrir_json(datos))

    def test_json_invalido(self):
        with self.assertRaises(cot.CotizacionNoDisponible):
            cot.obtener_cotizacion(lambda p, timeout: Resp("<html>no es json"))

    def test_http_y_red(self):
        def http500(p, timeout):
            raise urllib.error.HTTPError(p.full_url, 500, "x", {}, io.BytesIO(b""))

        def caido(p, timeout):
            raise urllib.error.URLError("sin red")

        def lento(p, timeout):
            raise TimeoutError()

        for abrir in (http500, caido, lento):
            with self.subTest(abrir=abrir.__name__), self.assertRaises(cot.CotizacionNoDisponible):
                cot.obtener_cotizacion(abrir)

    def test_pedido_es_get_sin_datos(self):
        vistos = []

        def abrir(pedido, timeout):
            vistos.append(pedido)
            return Resp(json.dumps({"venta": 10}))
        cot.obtener_cotizacion(abrir)
        p = vistos[0]
        self.assertEqual((p.get_method(), p.full_url, p.data), ("GET", cot.URL, None))
        self.assertFalse(p.has_header("Authorization"))
        self.assertEqual(sorted(k.lower() for k in p.headers), ["accept", "user-agent"])


class TestTexto(unittest.TestCase):
    def test_texto_para_campo(self):
        self.assertEqual(cot.texto_para_campo(Decimal("1575")), "1575")
        self.assertEqual(cot.texto_para_campo(Decimal("1575.50")), "1575,5")
        self.assertEqual(cot.texto_para_campo(Decimal("1575.255")), "1575,26")
        self.assertEqual(cot.texto_para_campo(Decimal("0.5")), "0,5")


if __name__ == "__main__":
    unittest.main()
