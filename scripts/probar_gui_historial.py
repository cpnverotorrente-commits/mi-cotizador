"""Recorre por código el guardado y la pantalla "Mi historial" contra un PocketBase real.

Requiere PB_SUPERUSER_EMAIL y PB_SUPERUSER_PASSWORD. Crea cuentas de prueba y las borra al terminar.
"""
import os
import sys
import uuid

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verificar_reglas as v  # noqa: E402
from mi_cotizador.app import Cotizador  # noqa: E402

fallos = []


def ok(nombre, cond):
    print(("OK   " if cond else "FALLA"), nombre)
    if not cond:
        fallos.append(nombre)


def poner(entrada, texto):
    entrada.delete(0, "end")
    entrada.insert(0, texto)


def tipo(app):
    return type(app.pantalla).__name__


def entrar(app, email, clave):
    app.mostrar_login()
    poner(app.pantalla.email, email)
    poner(app.pantalla.clave, clave)
    app.pantalla.entrar()


def convertir(app, monto, cot):
    c = app.pantalla
    poner(c.monto, monto)
    poner(c.cotizacion, cot)
    c.convertir()
    return c


def filas(app):
    t = app.pantalla.tabla
    return [t.item(i, "values") for i in t.get_children()]


def main():
    _, s = v.llamar("POST", "/api/collections/_superusers/auth-with-password",
                    {"identity": os.environ["PB_SUPERUSER_EMAIL"], "password": os.environ["PB_SUPERUSER_PASSWORD"]})
    su = s["token"]
    suf = uuid.uuid4().hex[:6]
    clave = uuid.uuid4().hex
    correos = {n: f"h{n}-{suf}@example.com" for n in "abc"}
    ids = []
    for m in correos.values():
        _, r = v.llamar("POST", "/api/collections/users/records",
                        {"email": m, "password": clave, "passwordConfirm": clave})
        ids.append(r["id"])

    txt = os.path.join(RAIZ, "historial.txt")
    existia = os.path.exists(txt)
    app = Cotizador()
    app.update()
    try:
        entrar(app, correos["a"], clave)
        c = convertir(app, "100000", "1000")
        ok("resultado mostrado", c.resultado.cget("text") == "100,00 USD" and c.aviso.cget("text") == "")
        convertir(app, "1500,50", "1000")
        convertir(app, "abc", "1000")
        ok("conversion invalida no guarda", "número válido" in app.pantalla.aviso.cget("text"))
        ok("no se crea historial.txt", existia or not os.path.exists(txt))

        app.pantalla.winfo_children()  # el botón "Mi historial" abre la pantalla
        app.mostrar_historial()
        ok("abre Mi historial", tipo(app) == "PantallaHistorial")
        f = filas(app)
        ok("A ve sus 2 consultas, la mas reciente primero",
           len(f) == 2 and f[0][1] == "1.500,50" and f[0][3] == "1,50" and f[1][1] == "100.000,00")
        ok("la fecha se muestra en hora local", len(f[0][0]) == 19 and f[0][0][2] == "/")

        entrar(app, correos["b"], clave)
        convertir(app, "2000", "1000")
        app.mostrar_historial()
        f = filas(app)
        ok("B ve solo la suya", len(f) == 1 and f[0][1] == "2.000,00")

        entrar(app, correos["c"], clave)
        app.mostrar_historial()
        ok("sin consultas: mensaje de vacio",
           filas(app) == [] and "Todavía no" in app.pantalla.mensaje.cget("text"))
        app.pantalla.master.mostrar_conversor()
        ok("Volver regresa al conversor", tipo(app) == "Conversor")

        # servidor apagado
        entrar(app, correos["a"], clave)
        os.environ["COTIZADOR_PB_URL"] = "http://127.0.0.1:9"
        c = convertir(app, "100", "10")
        ok("servidor apagado: resultado y aviso",
           c.resultado.cget("text") == "10,00 USD" and "No se pudo guardar" in c.aviso.cget("text"))
        app.mostrar_historial()
        ok("servidor apagado: historial muestra error", "PocketBase" in app.pantalla.mensaje.cget("text"))
        del os.environ["COTIZADOR_PB_URL"]
        app.mostrar_conversor()
        ok("se puede volver al conversor", tipo(app) == "Conversor")
        app.mostrar_historial()
        ok("la consulta fallida no quedó guardada", len(filas(app)) == 2)
    finally:
        app.destroy()
        os.environ.pop("COTIZADOR_PB_URL", None)
        _, rest = v.llamar("GET", "/api/collections/consultas/records?perPage=200", token=su)
        for r in rest.get("items", []):
            if r["usuario"] in ids:
                v.llamar("DELETE", f"/api/collections/consultas/records/{r['id']}", token=su)
        for i in ids:
            v.llamar("DELETE", f"/api/collections/users/records/{i}", token=su)
    print("\nTodo OK" if not fallos else f"\nFallaron {len(fallos)}: {fallos}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
