"""Verifica contra un PocketBase real que las reglas por rol funcionan.

Requiere PB_SUPERUSER_EMAIL, PB_SUPERUSER_PASSWORD y PB_ADMIN_EMAIL / PB_ADMIN_PASSWORD de un admin.
Crea cuentas de prueba y las borra al terminar.
"""
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

URL = os.environ.get("COTIZADOR_PB_URL", "http://127.0.0.1:8090").rstrip("/")


def llamar(metodo, ruta, datos=None, token=None):
    cab = {"Content-Type": "application/json"}
    if token:
        cab["Authorization"] = token
    cuerpo = json.dumps(datos).encode() if datos is not None else None
    p = urllib.request.Request(URL + ruta, data=cuerpo, headers=cab, method=metodo)
    try:
        with urllib.request.urlopen(p, timeout=10) as r:
            t = r.read().decode()
            return r.status, (json.loads(t) if t else {})
    except urllib.error.HTTPError as e:
        t = e.read().decode()
        try:
            return e.code, json.loads(t)
        except ValueError:
            return e.code, {}


fallos = []


def comprobar(nombre, condicion):
    print(("OK   " if condicion else "FALLA"), nombre)
    if not condicion:
        fallos.append(nombre)


def login(email, clave):
    return llamar("POST", "/api/collections/users/auth-with-password",
                  {"identity": email, "password": clave})


def main():
    _, s = llamar("POST", "/api/collections/_superusers/auth-with-password",
                  {"identity": os.environ["PB_SUPERUSER_EMAIL"], "password": os.environ["PB_SUPERUSER_PASSWORD"]})
    su = s["token"]
    c, a = login(os.environ["PB_ADMIN_EMAIL"], os.environ["PB_ADMIN_PASSWORD"])
    comprobar("admin inicia sesion", c == 200 and a["record"].get("rol") == "admin")
    tok_admin = a["token"]

    sufijo = uuid.uuid4().hex[:8]
    clave = uuid.uuid4().hex
    mail_u, mail_v = f"u-{sufijo}@example.com", f"v-{sufijo}@example.com"
    creados = []
    consultas = []
    try:
        c, u = llamar("POST", "/api/collections/users/records",
                      {"email": mail_u, "password": clave, "passwordConfirm": clave})
        comprobar("registro publico normal", c == 200); creados.append(u["id"])
        comprobar("usuario nuevo sin rol de admin", u.get("rol") in ("", "usuario", None))
        c, v = llamar("POST", "/api/collections/users/records",
                      {"email": mail_v, "password": clave, "passwordConfirm": clave})
        creados.append(v["id"])

        c, _ = llamar("POST", "/api/collections/users/records",
                      {"email": f"x-{sufijo}@example.com", "password": clave, "passwordConfirm": clave, "rol": "admin"})
        comprobar("registro con rol=admin rechazado", c in (400, 403))
        c, _ = llamar("POST", "/api/collections/users/records",
                      {"email": f"y-{sufijo}@example.com", "password": clave, "passwordConfirm": clave, "desactivado": True})
        comprobar("registro con desactivado forzado rechazado", c in (400, 403))

        c, d = llamar("GET", "/api/collections/users/records")
        comprobar("lista sin sesion no devuelve cuentas", c == 200 and d["totalItems"] == 0)

        c, du = login(mail_u, clave)
        comprobar("usuario comun inicia sesion", c == 200); tok_u = du["token"]
        c, d = llamar("GET", "/api/collections/users/records", token=tok_u)
        comprobar("usuario comun ve solo su cuenta", c == 200 and [i["id"] for i in d["items"]] == [u["id"]])
        c, _ = llamar("PATCH", f"/api/collections/users/records/{u['id']}", {"rol": "admin"}, tok_u)
        comprobar("usuario no puede auto-promoverse", c in (400, 403, 404))
        c, _ = llamar("PATCH", f"/api/collections/users/records/{u['id']}", {"desactivado": False}, tok_u)
        comprobar("usuario no puede tocar su estado", c in (400, 403, 404))
        c, _ = llamar("PATCH", f"/api/collections/users/records/{v['id']}", {"desactivado": True}, tok_u)
        comprobar("usuario no puede desactivar a otro", c in (400, 403, 404))
        nueva = uuid.uuid4().hex
        c, _ = llamar("PATCH", f"/api/collections/users/records/{v['id']}",
                      {"password": nueva, "passwordConfirm": nueva}, tok_u)
        comprobar("usuario no puede resetear la clave de otro", c in (400, 403, 404))
        c, _ = llamar("DELETE", f"/api/collections/users/records/{u['id']}", token=tok_u)
        comprobar("usuario no puede borrarse", c in (400, 403, 404))

        c, d = llamar("GET", "/api/collections/users/records?perPage=200", token=tok_admin)
        ids = {i["id"] for i in d.get("items", [])}
        comprobar("admin lista todas las cuentas", c == 200 and {u["id"], v["id"]} <= ids)

        c, _ = llamar("PATCH", f"/api/collections/users/records/{v['id']}", {"desactivado": True}, tok_admin)
        comprobar("admin desactiva una cuenta", c == 200)
        c, _ = login(mail_v, clave)
        comprobar("cuenta desactivada no inicia sesion (403)", c == 403)
        c, _ = llamar("PATCH", f"/api/collections/users/records/{v['id']}", {"desactivado": False}, tok_admin)
        c, _ = login(mail_v, clave)
        comprobar("cuenta reactivada vuelve a entrar", c == 200)

        c, _ = llamar("PATCH", f"/api/collections/users/records/{v['id']}",
                      {"password": nueva, "passwordConfirm": nueva}, tok_admin)
        comprobar("admin resetea clave sin la anterior", c == 200)
        c, _ = login(mail_v, clave)
        comprobar("la clave anterior ya no entra", c == 400)
        c, _ = login(mail_v, nueva)
        comprobar("la clave nueva entra", c == 200)

        # --- consultas (historial) ---
        datos_c = {"monto": 100000, "cotizacion": 1000, "resultado": 100}
        c, _ = llamar("POST", "/api/collections/consultas/records", {**datos_c, "usuario": u["id"]})
        comprobar("sin sesion no crea consultas", c in (400, 403))
        c, ca = llamar("POST", "/api/collections/consultas/records", {**datos_c, "usuario": u["id"]}, tok_u)
        comprobar("usuario crea una consulta propia", c == 200); consultas.append(ca["id"])
        c, cv = llamar("POST", "/api/collections/consultas/records", {**datos_c, "usuario": v["id"]}, tok_u)
        comprobar("usuario no crea consultas a nombre de otro", c in (400, 403))
        c, cf = llamar("POST", "/api/collections/consultas/records",
                       {**datos_c, "usuario": u["id"], "fecha": "2000-01-01 00:00:00.000Z"}, tok_u)
        if c == 200:
            consultas.append(cf["id"])
        comprobar("la fecha la fija el servidor", c in (400, 403) or (c == 200 and not cf["fecha"].startswith("2000")))
        c, d = login(mail_v, nueva)
        tok_v = d["token"]
        c, _ = llamar("POST", "/api/collections/consultas/records", {**datos_c, "usuario": v["id"]}, tok_v)
        comprobar("otro usuario crea la suya", c == 200)
        _, lst = llamar("GET", "/api/collections/consultas/records?perPage=200", token=tok_v)
        _, lst_u = llamar("GET", "/api/collections/consultas/records?perPage=200", token=tok_u)
        comprobar("cada usuario ve solo sus consultas",
                  all(i["usuario"] == v["id"] for i in lst["items"]) and lst["totalItems"] == 1
                  and all(i["usuario"] == u["id"] for i in lst_u["items"]) and lst_u["totalItems"] >= 1)
        c, _ = llamar("GET", f"/api/collections/consultas/records/{ca['id']}", token=tok_v)
        comprobar("no se ve la consulta de otro por id", c in (403, 404))
        c, d = llamar("GET", "/api/collections/consultas/records")
        comprobar("sin sesion no lista consultas", c == 200 and d["totalItems"] == 0)
        c, d = llamar("GET", "/api/collections/consultas/records?perPage=200", token=tok_admin)
        comprobar("el admin tampoco ve consultas ajenas",
                  c == 200 and all(i["usuario"] == a["record"]["id"] for i in d["items"]))
        c, _ = llamar("PATCH", f"/api/collections/consultas/records/{ca['id']}", {"monto": 1}, tok_u)
        comprobar("la consulta propia no se edita", c in (400, 403, 404))
        c, _ = llamar("DELETE", f"/api/collections/consultas/records/{ca['id']}", token=tok_u)
        comprobar("la consulta propia no se borra", c in (400, 403, 404))
        c, _ = llamar("DELETE", f"/api/collections/consultas/records/{ca['id']}", token=tok_admin)
        comprobar("el admin no borra consultas", c in (400, 403, 404))
    finally:
        for i in consultas:
            llamar("DELETE", f"/api/collections/consultas/records/{i}", token=su)
        # las consultas de v se borran por filtro
        _, restantes = llamar("GET", "/api/collections/consultas/records?perPage=200", token=su)
        for r in restantes.get("items", []):
            if r["usuario"] in creados:
                llamar("DELETE", f"/api/collections/consultas/records/{r['id']}", token=su)
        for i in creados:
            llamar("DELETE", f"/api/collections/users/records/{i}", token=su)
    print("\nTodo OK" if not fallos else f"\nFallaron {len(fallos)}: {fallos}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
