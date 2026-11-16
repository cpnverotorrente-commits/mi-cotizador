import unittest
from decimal import Decimal

from mi_cotizador.logica import EntradaInvalida, convertir


class TestConvertir(unittest.TestCase):
    def test_valida(self):
        self.assertEqual(convertir("100000", "1000")[2], Decimal("100.00"))

    def test_redondeo(self):
        self.assertEqual(convertir("1000", "3")[2], Decimal("333.33"))

    def test_coma_decimal(self):
        self.assertEqual(convertir("1500,50", "1000")[2], Decimal("1.50"))

    def test_invalidos(self):
        for monto, cot in [("", "1000"), ("100", ""), ("abc", "1000"),
                           ("100", "x"), ("-5", "1000"), ("100", "0"),
                           ("100", "-3"), ("nan", "1000"), ("inf", "1000")]:
            with self.subTest(monto=monto, cot=cot):
                with self.assertRaises(EntradaInvalida):
                    convertir(monto, cot)


if __name__ == "__main__":
    unittest.main()
