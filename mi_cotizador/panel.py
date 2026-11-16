"""Panel de administración de cuentas (solo admins)."""
import tkinter as tk
from tkinter import messagebox, ttk

from mi_cotizador import pocketbase
from mi_cotizador.logica import EntradaInvalida, puede_desactivar, validar_clave_nueva

ROJO = "#b00020"
VERDE = "#1b5e20"


class DialogoClave(tk.Toplevel):
    """Pide una contraseña nueva con confirmación. `resultado` queda en None si se cancela."""

    def __init__(self, master, email):
        super().__init__(master)
        self.title("Resetear contraseña")
        self.resizable(False, False)
        self.resultado = None
        marco = ttk.Frame(self, padding=15)
        marco.grid()
        ttk.Label(marco, text=f"Nueva contraseña para {email}").grid(
            row=0, column=0, columnspan=2, pady=(0, 8)
        )
        ttk.Label(marco, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=3)
        self.clave = ttk.Entry(marco, show="*", width=24)
        self.clave.grid(row=1, column=1, pady=3, padx=(8, 0))
        ttk.Label(marco, text="Repetir:").grid(row=2, column=0, sticky="w", pady=3)
        self.confirmacion = ttk.Entry(marco, show="*", width=24)
        self.confirmacion.grid(row=2, column=1, pady=3, padx=(8, 0))
        self.error = ttk.Label(marco, text="", foreground=ROJO, wraplength=260)
        self.error.grid(row=3, column=0, columnspan=2)
        botones = ttk.Frame(marco)
        botones.grid(row=4, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(botones, text="Aceptar", command=self.aceptar).pack(side="left", padx=4)
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="left", padx=4)
        self.bind("<Return>", lambda _e: self.aceptar())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.transient(master)
        self.clave.focus()

    def aceptar(self):
        try:
            self.resultado = validar_clave_nueva(self.clave.get(), self.confirmacion.get())
        except EntradaInvalida as e:
            self.error.config(text=str(e))
            return
        self.destroy()


class PanelAdmin(ttk.Frame):
    def __init__(self, master, sesion, abrir_conversor, cerrar_sesion):
        super().__init__(master, padding=15)
        self.sesion = sesion
        self.cuentas = {}

        cabecera = ttk.Frame(self)
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(cabecera, text="Panel de administración", font=("Segoe UI", 13, "bold")).pack(
            side="left"
        )
        ttk.Button(cabecera, text="Cerrar sesión", command=cerrar_sesion).pack(side="right")
        ttk.Button(cabecera, text="Abrir conversor", command=abrir_conversor).pack(
            side="right", padx=6
        )
        ttk.Label(self, text=f"Sesión: {sesion.email}").grid(row=1, column=0, sticky="w")

        self.tabla = ttk.Treeview(
            self, columns=("email", "rol", "estado"), show="headings", height=10,
            selectmode="browse",
        )
        for col, texto, ancho in (("email", "Email", 260), ("rol", "Rol", 80), ("estado", "Estado", 100)):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="w")
        self.tabla.grid(row=2, column=0, pady=8)
        self.tabla.bind("<<TreeviewSelect>>", lambda _e: self.actualizar_botones())

        botones = ttk.Frame(self)
        botones.grid(row=3, column=0, sticky="w")
        self.boton_estado = ttk.Button(botones, text="Desactivar", command=self.cambiar_estado)
        self.boton_estado.pack(side="left", padx=(0, 6))
        self.boton_clave = ttk.Button(botones, text="Resetear contraseña", command=self.resetear)
        self.boton_clave.pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Actualizar", command=self.cargar).pack(side="left")

        self.mensaje = ttk.Label(self, text="", wraplength=420)
        self.mensaje.grid(row=4, column=0, sticky="w", pady=(8, 0))

        self.actualizar_botones()
        self.cargar()

    # --- utilidades ---
    def avisar(self, texto, color=ROJO):
        self.mensaje.config(text=texto, foreground=color)

    def seleccionada(self):
        sel = self.tabla.selection()
        return self.cuentas.get(sel[0]) if sel else None

    def actualizar_botones(self):
        cuenta = self.seleccionada()
        if cuenta is None:
            self.boton_estado.config(text="Desactivar")
            self.boton_estado.state(["disabled"])
            self.boton_clave.state(["disabled"])
            return
        self.boton_clave.state(["!disabled"])
        self.boton_estado.config(text="Activar" if cuenta.desactivada else "Desactivar")
        if not cuenta.desactivada and not puede_desactivar(cuenta.id, self.sesion.id):
            self.boton_estado.state(["disabled"])
        else:
            self.boton_estado.state(["!disabled"])

    # --- acciones ---
    def cargar(self):
        try:
            cuentas = pocketbase.listar_usuarios(self.sesion)
        except pocketbase.ErrorPocketBase as e:
            self.avisar(str(e))
            return
        seleccion = self.seleccionada()
        self.tabla.delete(*self.tabla.get_children())
        self.cuentas = {c.id: c for c in cuentas}
        for c in cuentas:
            self.tabla.insert(
                "", "end", iid=c.id,
                values=(c.email, c.rol, "Desactivada" if c.desactivada else "Activa"),
            )
        if seleccion is not None and seleccion.id in self.cuentas:
            self.tabla.selection_set(seleccion.id)
        self.actualizar_botones()
        self.avisar(f"{len(cuentas)} cuenta(s).", VERDE)

    def cambiar_estado(self):
        cuenta = self.seleccionada()
        if cuenta is None:
            self.avisar("Seleccioná una cuenta.")
            return
        desactivar = not cuenta.desactivada
        if desactivar:
            if not puede_desactivar(cuenta.id, self.sesion.id):
                self.avisar("No podés desactivar tu propia cuenta.")
                return
            if not messagebox.askyesno(
                "Desactivar cuenta",
                f"¿Desactivar la cuenta {cuenta.email}? No podrá iniciar sesión.",
                parent=self,
            ):
                return
        try:
            pocketbase.cambiar_desactivada(self.sesion, cuenta.id, desactivar)
        except pocketbase.ErrorPocketBase as e:
            self.avisar(str(e))
            return
        self.cargar()
        self.avisar(
            f"Cuenta {cuenta.email} {'desactivada' if desactivar else 'activada'}.", VERDE
        )

    def _pedir_clave(self, email):
        dialogo = DialogoClave(self, email)
        self.wait_window(dialogo)
        return dialogo.resultado

    def resetear(self):
        cuenta = self.seleccionada()
        if cuenta is None:
            self.avisar("Seleccioná una cuenta.")
            return
        clave = self._pedir_clave(cuenta.email)
        if clave is None:
            return
        try:
            pocketbase.resetear_clave(self.sesion, cuenta.id, clave)
        except pocketbase.ErrorPocketBase as e:
            self.avisar(str(e))
            return
        self.avisar(f"Contraseña de {cuenta.email} actualizada.", VERDE)
