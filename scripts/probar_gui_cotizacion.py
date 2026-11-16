"""Recorre por código la cotización automática del conversor (con consulta falsa y con la red real).

No necesita PocketBase para las comprobaciones de la cotización; la de guardado en el historial sí
(PB_SUPERUSER_EMAIL y PB_SUPERUSER_PASSWORD) y crea una cuenta de prueba que borra al terminar.
"""
import os
import sys
import threading
import time
import uuid
from decimal import Decimal

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verificar_reglas as v  # noqa: E402
from mi_cotizador import cotizacion as cot  # noqa: E402
from mi_cotizador import pocketbase  # noqa: E402
from mi_cotizador.app import Conversor, Cotizador  # noqa: E402

fallos = []


def ok(nombre, cond):
    print(("OK   " if cond else "FALLA"), nombre)
    if not cond:
        fallos.append(nombre)


def esperar(app, cond, segundos=8):
    fin = time.time() + segundos
    while time.time() < fin:
        app.update()
        if cond():
            return True
        time.sleep(0.02)
    return False


def poner(entrada, texto):
    entrada.delete(0, "end")
    entrada.insert(0, texto)


def main():
    sesion = pocketbase.Sesion("x", "prueba@example.com", "usuario", "t")
    app = Cotizador()
    app.update()
    try:
        # 1) carga al abrir, con etiqueta de origen y fecha
        app._consultar = lambda: cot.Cotizacion(Decimal("1575"), "2026-11-16T18:00:00.000Z")
        app.sesion = sesion
        app.mostrar_conversor()
        c = app.pantalla
        ok("carga la cotizacion al abrir", esperar(app, lambda: c.cotizacion.get() == "1575"))
        ok("etiqueta de origen y fecha",
           "Dólar oficial (venta)" in c.origen.cget("text") and "actualizado" in c.origen.cget("text"))
        ok("boton habilitado al terminar", "disabled" not in c.boton_actualizar.state() and not c.consultando)

        # 2) actualizar reemplaza lo escrito
        poner(c.cotizacion, "999")
        c.actualizar_cotizacion()
        ok("actualizar reemplaza lo escrito", esperar(app, lambda: c.cotizacion.get() == "1575"))

        # 3) sin consultas simultaneas + ventana responde mientras espera
        llamadas = []
        liberar = threading.Event()

        def lenta():
            llamadas.append(1)
            liberar.wait(5)
            return cot.Cotizacion(Decimal("1600.5"), "")
        c._consultar = lenta
        c.actualizar_cotizacion()
        app.update()
        ok("durante la consulta: indicador y boton deshabilitado",
           "Actualizando" in c.origen.cget("text") and "disabled" in c.boton_actualizar.state())
        c.actualizar_cotizacion()
        c.actualizar_cotizacion()
        t0 = time.time()
        for _ in range(20):
            app.update()
        ok("la ventana responde mientras espera", time.time() - t0 < 1)
        liberar.set()
        ok("termina y completa el campo (coma decimal, sin fecha)",
           esperar(app, lambda: c.cotizacion.get() == "1600,5"))
        ok("una sola consulta pese a pulsar varias veces", len(llamadas) == 1)
        ok("sin fecha la etiqueta no la muestra", c.origen.cget("text") == "Dólar oficial (venta)")

        # 4) falla: conserva el campo, avisa, y reintento limpia el aviso
        poner(c.cotizacion, "1234")

        def falla():
            raise cot.CotizacionNoDisponible(cot.MENSAJE_FALLA)
        c._consultar = falla
        c.actualizar_cotizacion()
        ok("falla: conserva el valor y avisa",
           esperar(app, lambda: not c.consultando) and c.cotizacion.get() == "1234"
           and "No se pudo obtener" in c.origen.cget("text"))
        c._consultar = lambda: cot.Cotizacion(Decimal("1575"), "")
        c.actualizar_cotizacion()
        ok("reintento: completa y quita el aviso",
           esperar(app, lambda: c.cotizacion.get() == "1575") and "No se pudo" not in c.origen.cget("text"))

        # 5) excepcion inesperada tambien es falla recuperable
        def rara():
            raise RuntimeError("boom")
        c._consultar = rara
        c.actualizar_cotizacion()
        ok("excepcion inesperada: no se cuelga", esperar(app, lambda: not c.consultando)
           and "boom" in c.origen.cget("text"))

        # 6) destruir el frame con la consulta en curso no da errores
        liberar2 = threading.Event()
        app._consultar = lambda: (liberar2.wait(5), cot.Cotizacion(Decimal("1"), ""))[1]
        app.mostrar_conversor()
        app.update()
        app.mostrar_login()           # destruye el Conversor con la consulta en curso
        liberar2.set()
        for _ in range(30):
            app.update()
            time.sleep(0.02)
        ok("destruir durante la consulta no produce errores", True)

        # 7) convertir con la cotizacion cargada (la consulta de historial se prueba abajo)
        app._consultar = lambda: cot.Cotizacion(Decimal("1000"), "")
        app.sesion = sesion
        app.mostrar_conversor()
        c = app.pantalla
        esperar(app, lambda: c.cotizacion.get() == "1000")
        poner(c.monto, "100000")
        c.convertir()
        ok("convertir usa la cotizacion cargada", c.resultado.cget("text") == "100,00 USD")

        # 8) red real
        app._consultar = cot.obtener_cotizacion
        app.mostrar_conversor()
        c = app.pantalla
        real = esperar(app, lambda: not c.consultando, 12)
        ok("red real: carga una cotizacion positiva",
           real and c.cotizacion.get() not in ("", "0") and "Dólar oficial" in c.origen.cget("text"))
        print("      valor real cargado:", c.cotizacion.get(), "|", c.origen.cget("text"))

        # 9) falla real de red (direccion inalcanzable) sin congelar
        original = cot.URL
        cot.URL = "http://127.0.0.1:9/no-existe"
        try:
            c.actualizar_cotizacion()
            t0 = time.time()
            ok("falla real: avisa y la ventana responde",
               esperar(app, lambda: not c.consultando, 12) and "No se pudo obtener" in c.origen.cget("text")
               and c.cotizacion.get() not in ("",))
        finally:
            cot.URL = original

        # 10) guardado en el historial con la cotizacion automatica (PocketBase real)
        if os.environ.get("PB_SUPERUSER_EMAIL"):
            _, s = v.llamar("POST", "/api/collections/_superusers/auth-with-password",
                            {"identity": os.environ["PB_SUPERUSER_EMAIL"],
                             "password": os.environ["PB_SUPERUSER_PASSWORD"]})
            su = s["token"]
            clave = uuid.uuid4().hex
            correo = f"cz-{uuid.uuid4().hex[:6]}@example.com"
            _, r = v.llamar("POST", "/api/collections/users/records",
                            {"email": correo, "password": clave, "passwordConfirm": clave})
            try:
                real_ses = pocketbase.iniciar_sesion(correo, clave)
                app._consultar = lambda: cot.Cotizacion(Decimal("1575"), "")
                app.sesion = real_ses
                app.mostrar_conversor()
                c = app.pantalla
                esperar(app, lambda: c.cotizacion.get() == "1575")
                poner(c.monto, "157500")
                c.convertir()
                lista = pocketbase.listar_consultas(real_ses)
                ok("la conversion con cotizacion automatica queda en el historial",
                   len(lista) == 1 and lista[0].cotizacion == 1575 and lista[0].resultado == 100)
            finally:
                _, rest = v.llamar("GET", "/api/collections/consultas/records?perPage=200", token=su)
                for it in rest.get("items", []):
                    if it["usuario"] == r["id"]:
                        v.llamar("DELETE", f"/api/collections/consultas/records/{it['id']}", token=su)
                v.llamar("DELETE", f"/api/collections/users/records/{r['id']}", token=su)
        else:
            print("      (se omite la comprobacion del historial: faltan PB_SUPERUSER_*)")
    finally:
        app.destroy()
    print("\nTodo OK" if not fallos else f"\nFallaron {len(fallos)}: {fallos}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
