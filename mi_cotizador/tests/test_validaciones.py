import unittest

from mi_cotizador.logica import EntradaInvalida, validar_login, validar_registro


class TestValidaciones(unittest.TestCase):
    def test_login_ok(self):
        self.assertEqual(validar_login(" a@b.com ", "x"), ("a@b.com", "x"))

    def test_login_vacio(self):
        for e, c in [("", "x"), ("a@b.com", ""), ("  ", "x"), (None, None)]:
            with self.subTest(e=e, c=c), self.assertRaises(EntradaInvalida):
                validar_login(e, c)

    def test_registro_ok(self):
        self.assertEqual(validar_registro("a@b.com", "12345678", "12345678"),
                         ("a@b.com", "12345678"))

    def test_registro_invalido(self):
        casos = [("", "12345678", "12345678"), ("a@b.com", "", ""),
                 ("sin-arroba", "12345678", "12345678"),
                 ("a@b", "12345678", "12345678"),
                 ("a@b.com", "1234567", "1234567"),
                 ("a@b.com", "12345678", "12345679")]
        for caso in casos:
            with self.subTest(caso=caso), self.assertRaises(EntradaInvalida):
                validar_registro(*caso)


if __name__ == "__main__":
    unittest.main()


class TestAdmin(unittest.TestCase):
    def test_clave_nueva(self):
        from mi_cotizador.logica import validar_clave_nueva
        self.assertEqual(validar_clave_nueva("12345678", "12345678"), "12345678")
        for c, k in [("", ""), ("1234567", "1234567"), ("12345678", "12345679")]:
            with self.subTest(c=c, k=k), self.assertRaises(EntradaInvalida):
                validar_clave_nueva(c, k)

    def test_no_desactivarse(self):
        from mi_cotizador.logica import puede_desactivar
        self.assertFalse(puede_desactivar("1", "1"))
        self.assertTrue(puede_desactivar("2", "1"))


class TestFormatos(unittest.TestCase):
    def test_numero(self):
        from mi_cotizador.logica import formato_numero
        self.assertEqual(formato_numero(100), "100,00")
        self.assertEqual(formato_numero(1234567.5), "1.234.567,50")

    def test_fecha_local(self):
        from datetime import datetime, timezone
        from mi_cotizador.logica import formato_fecha_local
        esperado = datetime(2026, 11, 16, 18, 0, 0, tzinfo=timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M:%S")
        self.assertEqual(formato_fecha_local("2026-11-16 18:00:00.000Z"), esperado)
        self.assertEqual(formato_fecha_local("basura"), "basura")
        self.assertEqual(formato_fecha_local(""), "")
