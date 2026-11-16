import io
import json
import unittest
import urllib.error

from mi_cotizador import pocketbase as pb


class RespuestaOk:
    def __init__(self, datos):
        self._d = json.dumps(datos).encode()

    def read(self):
        return self._d

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def abrir_ok(datos):
    return lambda pedido, timeout: RespuestaOk(datos)


def abrir_http(codigo, cuerpo):
    def f(pedido, timeout):
        raise urllib.error.HTTPError(
            pedido.full_url, codigo, "x", {}, io.BytesIO(json.dumps(cuerpo).encode())
        )
    return f


def abrir_caido(pedido, timeout):
    raise urllib.error.URLError("conexion rechazada")


class TestPocketBase(unittest.TestCase):
    def test_login_ok(self):
        r = pb.iniciar_sesion("a@b.com", "x", abrir_ok({"token": "T", "record": {"id": "1", "email": "a@b.com"}}))
        self.assertEqual((r.email, r.rol, r.token, r.es_admin), ("a@b.com", "usuario", "T", False))

    def test_login_admin(self):
        r = pb.iniciar_sesion("a@b.com", "x", abrir_ok({"token": "T", "record": {"id": "1", "email": "a@b.com", "rol": "admin"}}))
        self.assertTrue(r.es_admin)

    def test_login_rol_vacio_es_usuario(self):
        r = pb.iniciar_sesion("a@b.com", "x", abrir_ok({"token": "T", "record": {"id": "1", "email": "a@b.com", "rol": ""}}))
        self.assertEqual(r.rol, "usuario")

    def test_login_cuenta_desactivada(self):
        with self.assertRaises(pb.CuentaDesactivada):
            pb.iniciar_sesion("a@b.com", "x", abrir_http(403, {"message": "no"}))

    def test_listar(self):
        s = pb.Sesion("1", "a@b.com", "admin", "T")
        items = [{"id": "1", "email": "a@b.com", "rol": "admin"},
                 {"id": "2", "email": "c@d.com", "rol": "", "desactivado": True}]
        r = pb.listar_usuarios(s, abrir_ok({"items": items}))
        self.assertEqual([(c.email, c.rol, c.desactivada) for c in r],
                         [("a@b.com", "admin", False), ("c@d.com", "usuario", True)])

    def test_acciones_admin_envian_token_y_cuerpo(self):
        vistos = []

        def abrir(pedido, timeout):
            vistos.append((pedido.get_method(), pedido.full_url, pedido.get_header("Authorization"),
                           json.loads(pedido.data)))
            return RespuestaOk({})
        s = pb.Sesion("1", "a@b.com", "admin", "T")
        pb.cambiar_desactivada(s, "9", True, abrir)
        pb.resetear_clave(s, "9", "12345678", abrir)
        self.assertEqual(vistos[0][0:3], ("PATCH", pb.url_base() + "/api/collections/users/records/9", "T"))
        self.assertEqual(vistos[0][3], {"desactivado": True})
        self.assertEqual(vistos[1][3], {"password": "12345678", "passwordConfirm": "12345678"})

    def test_guardar_consulta(self):
        vistos = []

        def abrir(pedido, timeout):
            vistos.append((pedido.get_method(), pedido.full_url, pedido.get_header("Authorization"),
                           json.loads(pedido.data)))
            return RespuestaOk({"id": "x"})
        s = pb.Sesion("U1", "a@b.com", "usuario", "T")
        from decimal import Decimal
        pb.guardar_consulta(s, Decimal("100000.00"), Decimal("1000.00"), Decimal("100.00"), abrir)
        self.assertEqual(vistos[0][0:3], ("POST", pb.url_base() + "/api/collections/consultas/records", "T"))
        self.assertEqual(vistos[0][3],
                         {"usuario": "U1", "monto": 100000.0, "cotizacion": 1000.0, "resultado": 100.0})

    def test_guardar_consulta_errores(self):
        s = pb.Sesion("U1", "a@b.com", "usuario", "T")
        with self.assertRaises(pb.ServicioNoDisponible):
            pb.guardar_consulta(s, 1, 1, 1, abrir_caido)
        with self.assertRaises(pb.NoAutorizado):
            pb.guardar_consulta(s, 1, 1, 1, abrir_http(403, {}))

    def test_listar_consultas(self):
        s = pb.Sesion("U1", "a@b.com", "usuario", "T")
        items = [{"id": "2", "fecha": "2026-11-16 18:00:00.000Z", "monto": 1500.5, "cotizacion": 1000, "resultado": 1.5},
                 {"id": "1", "fecha": "2026-11-16 17:00:00.000Z", "monto": 100000, "cotizacion": 1000, "resultado": 100}]
        vistos = []

        def abrir(pedido, timeout):
            vistos.append(pedido.full_url)
            return RespuestaOk({"items": items})
        r = pb.listar_consultas(s, abrir)
        self.assertIn("sort=-fecha", vistos[0])
        self.assertEqual([(c.id, c.monto, c.resultado) for c in r], [("2", 1500.5, 1.5), ("1", 100000.0, 100.0)])
        with self.assertRaises(pb.ServicioNoDisponible):
            pb.listar_consultas(s, abrir_caido)

    def test_acciones_admin_errores(self):
        s = pb.Sesion("1", "a@b.com", "usuario", "T")
        for codigo in (401, 403, 404):
            with self.subTest(codigo=codigo), self.assertRaises(pb.NoAutorizado):
                pb.cambiar_desactivada(s, "9", True, abrir_http(codigo, {}))
        with self.assertRaises(pb.ServicioNoDisponible):
            pb.resetear_clave(s, "9", "12345678", abrir_caido)
        with self.assertRaises(pb.ServicioNoDisponible):
            pb.listar_usuarios(s, abrir_http(500, {}))

    def test_login_credenciales(self):
        with self.assertRaises(pb.CredencialesInvalidas):
            pb.iniciar_sesion("a@b.com", "x", abrir_http(400, {"message": "fail"}))

    def test_login_caido(self):
        with self.assertRaises(pb.ServicioNoDisponible):
            pb.iniciar_sesion("a@b.com", "x", abrir_caido)

    def test_login_error_inesperado(self):
        with self.assertRaises(pb.ServicioNoDisponible):
            pb.iniciar_sesion("a@b.com", "x", abrir_http(500, {}))

    def test_registro_ok(self):
        pb.registrar("a@b.com", "12345678", abrir_ok({"id": "1"}))

    def test_registro_email_en_uso(self):
        cuerpo = {"data": {"email": {"code": "validation_not_unique", "message": "x"}}}
        with self.assertRaises(pb.EmailEnUso):
            pb.registrar("a@b.com", "12345678", abrir_http(400, cuerpo))

    def test_registro_otro_error(self):
        cuerpo = {"data": {"password": {"code": "c", "message": "Muy corta."}}}
        with self.assertRaises(pb.ErrorDeRegistro) as c:
            pb.registrar("a@b.com", "1", abrir_http(400, cuerpo))
        self.assertEqual(str(c.exception), "Muy corta.")

    def test_registro_deshabilitado(self):
        with self.assertRaises(pb.ErrorDeRegistro):
            pb.registrar("a@b.com", "12345678", abrir_http(403, {}))

    def test_registro_caido(self):
        with self.assertRaises(pb.ServicioNoDisponible):
            pb.registrar("a@b.com", "12345678", abrir_caido)

    def test_url_configurable(self):
        import os
        os.environ["COTIZADOR_PB_URL"] = "http://otro:1234/"
        try:
            self.assertEqual(pb.url_base(), "http://otro:1234")
        finally:
            del os.environ["COTIZADOR_PB_URL"]


if __name__ == "__main__":
    unittest.main()
