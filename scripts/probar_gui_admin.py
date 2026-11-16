"""Recorre por código la app contra un PocketBase real: admin, usuario común y cuenta desactivada.

Requiere PB_SUPERUSER_EMAIL, PB_SUPERUSER_PASSWORD, PB_ADMIN_EMAIL y PB_ADMIN_PASSWORD.
"""
import os
import sys
import uuid
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verificar_reglas as v  # noqa: E402
from mi_cotizador import panel as panel_mod  # noqa: E402
from mi_cotizador.app import Conversor, Cotizador  # noqa: E402
from mi_cotizador.panel import PanelAdmin  # noqa: E402

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
    l = app.pantalla
    poner(l.email, email)
    poner(l.clave, clave)
    l.entrar()
    return l


def main():
    _, s = v.llamar("POST", "/api/collections/_superusers/auth-with-password",
                    {"identity": os.environ["PB_SUPERUSER_EMAIL"], "password": os.environ["PB_SUPERUSER_PASSWORD"]})
    su = s["token"]
    suf = uuid.uuid4().hex[:6]
    clave = uuid.uuid4().hex
    mail_u, mail_d = f"gu-{suf}@example.com", f"gd-{suf}@example.com"
    creados = []
    for m in (mail_u, mail_d):
        _, r = v.llamar("POST", "/api/collections/users/records",
                        {"email": m, "password": clave, "passwordConfirm": clave})
        creados.append(r["id"])
    id_d = creados[1]

    app = Cotizador()
    app.update()
    try:
        # usuario común -> conversor, sin botón de panel
        entrar(app, mail_u, clave)
        ok("usuario comun va al conversor", tipo(app) == "Conversor")
        textos = [w.cget("text") for w in app.pantalla.winfo_children()[0].winfo_children()]
        ok("usuario comun sin 'Volver al panel'", "Volver al panel" not in textos)

        # admin -> panel
        entrar(app, os.environ["PB_ADMIN_EMAIL"], os.environ["PB_ADMIN_PASSWORD"])
        ok("admin ve el panel", tipo(app) == "PanelAdmin")
        p = app.pantalla
        emails = [p.tabla.item(i, "values")[0] for i in p.tabla.get_children()]
        ok("panel lista las cuentas", {mail_u, mail_d, os.environ["PB_ADMIN_EMAIL"]} <= set(emails))
        ok("acciones deshabilitadas sin seleccion",
           "disabled" in p.boton_estado.state() and "disabled" in p.boton_clave.state())
        p.cambiar_estado()
        ok("sin seleccion pide seleccionar", "Seleccioná" in p.mensaje.cget("text"))

        # no puede desactivarse a sí mismo
        id_admin = app.sesion.id
        p.tabla.selection_set(id_admin)
        p.update()
        ok("no puede desactivarse a si mismo", "disabled" in p.boton_estado.state())

        # desactivar (con confirmación) -> no inicia sesión
        p.tabla.selection_set(id_d)
        p.update()
        messagebox.askyesno = lambda *a, **k: True
        p.cambiar_estado()
        ok("lista refleja cuenta desactivada", p.tabla.item(id_d, "values")[2] == "Desactivada")
        l = entrar(app, mail_d, clave)
        ok("cuenta desactivada no entra", tipo(app) == "PantallaLogin" and "desactivada" in l.mensaje.cget("text"))

        # reactivar + resetear contraseña
        entrar(app, os.environ["PB_ADMIN_EMAIL"], os.environ["PB_ADMIN_PASSWORD"])
        p = app.pantalla
        p.tabla.selection_set(id_d)
        p.update()
        ok("boton dice Activar", p.boton_estado.cget("text") == "Activar")
        p.cambiar_estado()
        ok("cuenta reactivada", p.tabla.item(id_d, "values")[2] == "Activa")
        nueva = uuid.uuid4().hex
        p._pedir_clave = lambda email: nueva
        p.tabla.selection_set(id_d)
        p.update()
        p.resetear()
        ok("reseteo informado", "actualizada" in p.mensaje.cget("text"))
        entrar(app, mail_d, clave)
        ok("clave anterior no entra", tipo(app) == "PantallaLogin")
        entrar(app, mail_d, nueva)
        ok("clave nueva entra", tipo(app) == "Conversor")

        # admin: conversor <-> panel
        entrar(app, os.environ["PB_ADMIN_EMAIL"], os.environ["PB_ADMIN_PASSWORD"])
        app.mostrar_conversor()
        ok("admin abre el conversor", tipo(app) == "Conversor")
        app.mostrar_panel()
        ok("admin vuelve al panel sin re-login", tipo(app) == "PanelAdmin")

        # servidor apagado: el estado de la lista no cambia
        p = app.pantalla
        p.tabla.selection_set(id_d)
        p.update()
        antes = p.tabla.item(id_d, "values")
        os.environ["COTIZADOR_PB_URL"] = "http://127.0.0.1:9"
        p.cambiar_estado()
        ok("servidor apagado: mensaje y lista intacta",
           "PocketBase" in p.mensaje.cget("text") and p.tabla.item(id_d, "values") == antes)
        del os.environ["COTIZADOR_PB_URL"]
    finally:
        app.destroy()
        for i in creados:
            v.llamar("DELETE", f"/api/collections/users/records/{i}", token=su)
    print("\nTodo OK" if not fallos else f"\nFallaron {len(fallos)}: {fallos}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
