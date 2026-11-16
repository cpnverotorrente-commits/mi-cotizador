"""Configura PocketBase para Mi Cotizador: campos rol y desactivado, reglas por rol y admin.

Uso:
    PB_SUPERUSER_EMAIL / PB_SUPERUSER_PASSWORD  (variables de entorno, superusuario de PocketBase)
    python scripts/configurar_pocketbase.py --admin correo@ejemplo.com

Si el admin no existe se crea con la contraseña de PB_ADMIN_PASSWORD (variable de entorno).
Es idempotente: se puede ejecutar varias veces.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

URL = os.environ.get("COTIZADOR_PB_URL", "http://127.0.0.1:8090").rstrip("/")

CAMPOS = [
    {"name": "rol", "type": "select", "maxSelect": 1, "values": ["usuario", "admin"]},
    {"name": "desactivado", "type": "bool"},
]

ES_ADMIN = '@request.auth.rol = "admin"'
SIN_PRIVILEGIOS = '@request.body.rol:isset = false && @request.body.desactivado:isset = false'
REGLAS = {
    "listRule": f'id = @request.auth.id || {ES_ADMIN}',
    "viewRule": f'id = @request.auth.id || {ES_ADMIN}',
    "createRule": SIN_PRIVILEGIOS,
    "updateRule": f'(id = @request.auth.id && {SIN_PRIVILEGIOS}) || {ES_ADMIN}',
    "deleteRule": None,
    "authRule": "desactivado = false",
    # manageRule permite al admin cambiar email y contraseña de otras cuentas sin la contraseña anterior
    "manageRule": ES_ADMIN,
}


REGLAS_CONSULTAS = {
    "listRule": "usuario = @request.auth.id",
    "viewRule": "usuario = @request.auth.id",
    "createRule": '@request.auth.id != "" && @request.body.usuario = @request.auth.id',
    "updateRule": None,  # inmutables: solo superusuarios
    "deleteRule": None,
}


def configurar_consultas(token, id_users):
    """Crea la colección consultas si falta y reaplica siempre sus reglas."""
    try:
        existente = pedir("GET", "/api/collections/consultas", token=token, tolerar_404=True)
    except LookupError:
        existente = None
    if existente is None:
        pedir("POST", "/api/collections", {
            "name": "consultas",
            "type": "base",
            "fields": [
                {"name": "usuario", "type": "relation", "collectionId": id_users,
                 "maxSelect": 1, "required": True, "cascadeDelete": False},
                {"name": "monto", "type": "number"},
                {"name": "cotizacion", "type": "number"},
                {"name": "resultado", "type": "number"},
                {"name": "fecha", "type": "autodate", "onCreate": True, "onUpdate": False},
            ],
            **REGLAS_CONSULTAS,
        }, token)
        print("Colección consultas: creada.")
    else:
        pedir("PATCH", "/api/collections/consultas", REGLAS_CONSULTAS, token)
        print("Colección consultas: ya existía, reglas reaplicadas.")


def pedir(metodo, ruta, datos=None, token=None, tolerar_404=False):
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = token
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    pedido = urllib.request.Request(URL + ruta, data=cuerpo, headers=cabeceras, method=metodo)
    try:
        with urllib.request.urlopen(pedido, timeout=10) as r:
            texto = r.read().decode("utf-8")
            return json.loads(texto) if texto else {}
    except urllib.error.HTTPError as e:
        if e.code == 404 and tolerar_404:
            raise LookupError(ruta) from None
        sys.exit(f"Error {e.code} en {metodo} {ruta}: {e.read().decode('utf-8', 'replace')}")
    except OSError as e:
        sys.exit(f"No se pudo contactar con PocketBase en {URL}: {e}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--admin", required=True, help="email del usuario que será admin")
    args = ap.parse_args()

    email = os.environ.get("PB_SUPERUSER_EMAIL")
    clave = os.environ.get("PB_SUPERUSER_PASSWORD")
    if not email or not clave:
        sys.exit("Definí PB_SUPERUSER_EMAIL y PB_SUPERUSER_PASSWORD.")

    token = pedir("POST", "/api/collections/_superusers/auth-with-password",
                  {"identity": email, "password": clave})["token"]

    # 1) Campos (se conservan los existentes y se agregan los que faltan)
    coleccion = pedir("GET", "/api/collections/users", token=token)
    existentes = {f["name"] for f in coleccion["fields"]}
    faltan = [c for c in CAMPOS if c["name"] not in existentes]
    if faltan:
        pedir("PATCH", "/api/collections/users", {"fields": coleccion["fields"] + faltan}, token)
        print("Campos agregados:", ", ".join(c["name"] for c in faltan))
    else:
        print("Campos: ya existían.")

    # 2) Reglas (después de los campos, porque las reglas los usan)
    pedir("PATCH", "/api/collections/users", REGLAS, token)
    print("Reglas aplicadas.")

    # 2b) Colección de consultas (historial de conversiones)
    configurar_consultas(token, coleccion["id"])

    # 3) Admin: se crea o se promueve
    filtro = urllib.request.quote(f'email="{args.admin}"')
    encontrados = pedir("GET", f"/api/collections/users/records?filter={filtro}", token=token)["items"]
    if encontrados:
        pedir("PATCH", f"/api/collections/users/records/{encontrados[0]['id']}",
              {"rol": "admin", "desactivado": False}, token)
        print(f"{args.admin}: promovido a admin.")
    else:
        clave_admin = os.environ.get("PB_ADMIN_PASSWORD")
        if not clave_admin or len(clave_admin) < 8:
            sys.exit(f"{args.admin} no existe: definí PB_ADMIN_PASSWORD (mínimo 8 caracteres) para crearlo.")
        pedir("POST", "/api/collections/users/records",
              {"email": args.admin, "password": clave_admin, "passwordConfirm": clave_admin,
               "rol": "admin"}, token)
        print(f"{args.admin}: creado como admin.")


if __name__ == "__main__":
    main()
