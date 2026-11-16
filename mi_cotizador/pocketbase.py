"""Cliente mínimo de la API REST de PocketBase (colección users)."""
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

URL_POR_DEFECTO = "http://127.0.0.1:8090"
TIMEOUT = 5
ROL_ADMIN = "admin"
ROL_USUARIO = "usuario"


class ErrorPocketBase(Exception):
    """Base de los errores; el mensaje es apto para mostrar."""


class CredencialesInvalidas(ErrorPocketBase):
    pass


class CuentaDesactivada(ErrorPocketBase):
    pass


class EmailEnUso(ErrorPocketBase):
    pass


class ErrorDeRegistro(ErrorPocketBase):
    pass


class NoAutorizado(ErrorPocketBase):
    pass


class ServicioNoDisponible(ErrorPocketBase):
    pass


class _RespuestaHttp(Exception):
    def __init__(self, codigo, cuerpo):
        self.codigo, self.cuerpo = codigo, cuerpo


@dataclass(frozen=True)
class Sesion:
    """Sesión en memoria del usuario autenticado."""
    id: str
    email: str
    rol: str
    token: str

    @property
    def es_admin(self):
        return self.rol == ROL_ADMIN


@dataclass(frozen=True)
class Cuenta:
    id: str
    email: str
    rol: str
    desactivada: bool


@dataclass(frozen=True)
class Consulta:
    id: str
    fecha: str  # fecha y hora en UTC tal como la entrega PocketBase
    monto: float
    cotizacion: float
    resultado: float


def url_base():
    return os.environ.get("COTIZADOR_PB_URL", URL_POR_DEFECTO).rstrip("/")


def _llamar(metodo, ruta, datos, abrir, token=None):
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = token
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    pedido = urllib.request.Request(
        url_base() + ruta, data=cuerpo, headers=cabeceras, method=metodo
    )
    try:
        with abrir(pedido, timeout=TIMEOUT) as r:
            texto = r.read().decode("utf-8")
            return json.loads(texto) if texto else {}
    except urllib.error.HTTPError as e:
        try:
            cuerpo_error = json.loads(e.read().decode("utf-8"))
        except (ValueError, OSError):
            cuerpo_error = {}
        raise _RespuestaHttp(e.code, cuerpo_error) from None
    except (OSError, ValueError):
        raise ServicioNoDisponible(
            "No se pudo conectar con PocketBase. Verificá que esté en marcha e intentá de nuevo."
        ) from None


def _inesperado(e):
    return ServicioNoDisponible(f"PocketBase respondió con un error inesperado ({e.codigo}).")


def iniciar_sesion(email, clave, abrir=urllib.request.urlopen):
    """Devuelve la Sesion del usuario autenticado."""
    try:
        datos = _llamar(
            "POST",
            "/api/collections/users/auth-with-password",
            {"identity": email, "password": clave},
            abrir,
        )
    except _RespuestaHttp as e:
        if e.codigo == 400:
            raise CredencialesInvalidas("Email o contraseña incorrectos.") from None
        if e.codigo == 403:
            raise CuentaDesactivada(
                "Tu cuenta está desactivada. Consultá con un administrador."
            ) from None
        raise _inesperado(e) from None
    registro = datos.get("record", {})
    return Sesion(
        id=registro.get("id", ""),
        email=registro.get("email", email),
        rol=registro.get("rol") or ROL_USUARIO,
        token=datos.get("token", ""),
    )


def registrar(email, clave, abrir=urllib.request.urlopen):
    """Crea el usuario en PocketBase."""
    try:
        _llamar(
            "POST",
            "/api/collections/users/records",
            {"email": email, "password": clave, "passwordConfirm": clave},
            abrir,
        )
    except _RespuestaHttp as e:
        if e.codigo == 400:
            campos = e.cuerpo.get("data", {}) or {}
            if campos.get("email", {}).get("code") == "validation_not_unique":
                raise EmailEnUso("Ese email ya está registrado.") from None
            detalle = next(
                (v.get("message") for v in campos.values() if isinstance(v, dict) and v.get("message")),
                "Los datos no son válidos.",
            )
            raise ErrorDeRegistro(detalle) from None
        if e.codigo in (401, 403):
            raise ErrorDeRegistro("El registro de usuarios no está habilitado.") from None
        raise _inesperado(e) from None


def _con_sesion(metodo, ruta, datos, sesion, abrir):
    try:
        return _llamar(metodo, ruta, datos, abrir, token=sesion.token)
    except _RespuestaHttp as e:
        if e.codigo in (401, 403, 404):
            raise NoAutorizado(
                "No tenés permiso para esa acción. Volvé a iniciar sesión."
            ) from None
        if e.codigo == 400:
            campos = e.cuerpo.get("data", {}) or {}
            detalle = next(
                (v.get("message") for v in campos.values() if isinstance(v, dict) and v.get("message")),
                "Los datos no son válidos.",
            )
            raise ErrorDeRegistro(detalle) from None
        raise _inesperado(e) from None


def listar_usuarios(sesion, abrir=urllib.request.urlopen):
    """Lista de Cuenta (hasta 200), ordenada por email."""
    datos = _con_sesion(
        "GET", "/api/collections/users/records?perPage=200&sort=email", None, sesion, abrir
    )
    return [
        Cuenta(
            id=r.get("id", ""),
            email=r.get("email", ""),
            rol=r.get("rol") or ROL_USUARIO,
            desactivada=bool(r.get("desactivado")),
        )
        for r in datos.get("items", [])
    ]


def cambiar_desactivada(sesion, cuenta_id, desactivada, abrir=urllib.request.urlopen):
    _con_sesion(
        "PATCH",
        f"/api/collections/users/records/{cuenta_id}",
        {"desactivado": bool(desactivada)},
        sesion,
        abrir,
    )


def resetear_clave(sesion, cuenta_id, clave, abrir=urllib.request.urlopen):
    _con_sesion(
        "PATCH",
        f"/api/collections/users/records/{cuenta_id}",
        {"password": clave, "passwordConfirm": clave},
        sesion,
        abrir,
    )


def guardar_consulta(sesion, monto, cotizacion, resultado, abrir=urllib.request.urlopen):
    """Guarda una conversión a nombre del usuario de la sesión (monto, cotización y resultado ya redondeados)."""
    _con_sesion(
        "POST",
        "/api/collections/consultas/records",
        {
            "usuario": sesion.id,
            "monto": float(monto),
            "cotizacion": float(cotizacion),
            "resultado": float(resultado),
        },
        sesion,
        abrir,
    )


def listar_consultas(sesion, abrir=urllib.request.urlopen):
    """Últimas 200 consultas propias, la más reciente primero."""
    datos = _con_sesion(
        "GET", "/api/collections/consultas/records?perPage=200&sort=-fecha", None, sesion, abrir
    )
    return [
        Consulta(
            id=r.get("id", ""),
            fecha=r.get("fecha", ""),
            monto=float(r.get("monto") or 0),
            cotizacion=float(r.get("cotizacion") or 0),
            resultado=float(r.get("resultado") or 0),
        )
        for r in datos.get("items", [])
    ]
