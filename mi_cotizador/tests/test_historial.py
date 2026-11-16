import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from mi_cotizador import historial


class TestHistorial(unittest.TestCase):
    def test_crea_y_acumula(self):
        with tempfile.TemporaryDirectory() as d:
            t = datetime(2026, 11, 16, 14, 32, 5)
            historial.guardar(Decimal("100000.00"), Decimal("1000.00"), Decimal("100.00"), d, t)
            historial.guardar(Decimal("1000.00"), Decimal("3.00"), Decimal("333.33"), d, t)
            lineas = (Path(d) / "historial.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lineas), 2)
            self.assertEqual(
                lineas[0],
                "2026-11-16 14:32:05 | 100000.00 ARS | cotización 1000.00 | 100.00 USD",
            )

    def test_error_de_escritura(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(OSError):
                historial.guardar(Decimal(1), Decimal(1), Decimal(1), Path(d) / "no_existe")


if __name__ == "__main__":
    unittest.main()
