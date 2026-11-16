"""Pantallas de inicio de sesión y registro (Tkinter)."""
import tkinter as tk
from tkinter import ttk

from mi_cotizador import pocketbase
from mi_cotizador.logica import EntradaInvalida, validar_login, validar_registro

ROJO = "#b00020"
VERDE = "#1b5e20"


class _Formulario(ttk.Frame):
    def __init__(self, master, titulo):
        super().__init__(master, padding=20)
        ttk.Label(self, text=titulo, font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )
        self._fila = 1
        self.mensaje = ttk.Label(self, text="", wraplength=300)

    def campo(self, etiqueta, oculto=False):
        ttk.Label(self, text=etiqueta).grid(row=self._fila, column=0, sticky="w", pady=4)
        entrada = ttk.Entry(self, width=26, show="*" if oculto else "")
        entrada.grid(row=self._fila, column=1, pady=4, padx=(10, 0))
        self._fila += 1
        return entrada

    def boton(self, texto, comando):
        b = ttk.Button(self, text=texto, command=comando)
        b.grid(row=self._fila, column=0, columnspan=2, pady=(10, 4))
        self._fila += 1
        return b

    def enlace(self, texto, comando):
        e = ttk.Button(self, text=texto, command=comando, style="Toolbutton")
        e.grid(row=self._fila, column=0, columnspan=2)
        self._fila += 1

    def colocar_mensaje(self):
        self.mensaje.grid(row=self._fila, column=0, columnspan=2, pady=(6, 0))

    def avisar(self, texto, color=ROJO):
        self.mensaje.config(text=texto, foreground=color)

    def _con_espera(self, boton, accion):
        """Ejecuta accion con el botón deshabilitado mientras dura la llamada."""
        boton.state(["disabled"])
        self.update_idletasks()
        try:
            return accion()
        finally:
            boton.state(["!disabled"])


class PantallaLogin(_Formulario):
    def __init__(self, master, al_iniciar_sesion, ir_a_registro):
        super().__init__(master, "Iniciar sesión")
        self._al_iniciar = al_iniciar_sesion
        self.email = self.campo("Email:")
        self.clave = self.campo("Contraseña:", oculto=True)
        self.boton_entrar = self.boton("Iniciar sesión", self.entrar)
        self.enlace("¿No tenés cuenta? Registrate", ir_a_registro)
        self.colocar_mensaje()
        self.email.bind("<Return>", lambda _e: self.entrar())
        self.clave.bind("<Return>", lambda _e: self.entrar())

    def reiniciar(self, mensaje="", color=VERDE):
        self.clave.delete(0, "end")
        self.avisar(mensaje, color)
        (self.clave if self.email.get() else self.email).focus()

    def entrar(self):
        self.avisar("")
        try:
            email, clave = validar_login(self.email.get(), self.clave.get())
        except EntradaInvalida as e:
            self.avisar(str(e))
            return
        try:
            usuario = self._con_espera(
                self.boton_entrar, lambda: pocketbase.iniciar_sesion(email, clave)
            )
        except pocketbase.ErrorPocketBase as e:
            self.avisar(str(e))
            return
        self.clave.delete(0, "end")
        self._al_iniciar(usuario)


class PantallaRegistro(_Formulario):
    def __init__(self, master, al_registrar, ir_a_login):
        super().__init__(master, "Crear cuenta")
        self._al_registrar = al_registrar
        self.email = self.campo("Email:")
        self.clave = self.campo("Contraseña:", oculto=True)
        self.confirmacion = self.campo("Repetir contraseña:", oculto=True)
        self.boton_registro = self.boton("Registrarme", self.registrar)
        self.enlace("Ya tengo cuenta", ir_a_login)
        self.colocar_mensaje()
        self.confirmacion.bind("<Return>", lambda _e: self.registrar())

    def reiniciar(self):
        for e in (self.email, self.clave, self.confirmacion):
            e.delete(0, "end")
        self.avisar("")
        self.email.focus()

    def registrar(self):
        self.avisar("")
        try:
            email, clave = validar_registro(
                self.email.get(), self.clave.get(), self.confirmacion.get()
            )
        except EntradaInvalida as e:
            self.avisar(str(e))
            return
        try:
            self._con_espera(self.boton_registro, lambda: pocketbase.registrar(email, clave))
        except pocketbase.ErrorPocketBase as e:
            self.avisar(str(e))
            return
        self._al_registrar(email)
