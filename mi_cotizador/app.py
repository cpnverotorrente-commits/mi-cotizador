"""Ventana de Mi Cotizador (Tkinter): inicio de sesión, registro, panel de admin y conversor."""
import queue
import threading
import tkinter as tk
from tkinter import ttk

from mi_cotizador import pocketbase
from mi_cotizador.cotizacion import MENSAJE_FALLA, obtener_cotizacion, texto_para_campo
from mi_cotizador.logica import EntradaInvalida, convertir, formato_fecha_local, formato_numero
from mi_cotizador.panel import PanelAdmin
from mi_cotizador.pantalla_historial import PantallaHistorial
from mi_cotizador.pantallas import PantallaLogin, PantallaRegistro

ROJO = "#b00020"
GRIS = "#555555"


class Conversor(ttk.Frame):
    def __init__(self, master, sesion, al_cerrar_sesion, ver_historial, volver_al_panel=None,
                 consultar=obtener_cotizacion):
        super().__init__(master, padding=20)
        self.sesion = sesion
        self._consultar = consultar
        self.consultando = False
        self._cola = None
        self._sondeo = None

        cabecera = ttk.Frame(self)
        cabecera.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(cabecera, text=sesion.email).pack(side="left")
        ttk.Button(cabecera, text="Cerrar sesión", command=al_cerrar_sesion).pack(side="right")
        if volver_al_panel is not None:
            ttk.Button(cabecera, text="Volver al panel", command=volver_al_panel).pack(
                side="right", padx=6
            )

        ttk.Label(self, text="Monto en pesos:").grid(row=1, column=0, sticky="w", pady=4)
        self.monto = ttk.Entry(self, width=20)
        self.monto.grid(row=1, column=1, pady=4, padx=(10, 0))

        ttk.Label(self, text="Cotización del dólar:").grid(row=2, column=0, sticky="w", pady=4)
        self.cotizacion = ttk.Entry(self, width=20)
        self.cotizacion.grid(row=2, column=1, pady=4, padx=(10, 0))

        self.origen = ttk.Label(self, text="", foreground=GRIS, wraplength=320)
        self.origen.grid(row=3, column=0, columnspan=2, sticky="w")

        botones = ttk.Frame(self)
        botones.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(botones, text="Convertir", command=self.convertir).pack(side="left", padx=4)
        self.boton_actualizar = ttk.Button(
            botones, text="Actualizar cotización", command=self.actualizar_cotizacion
        )
        self.boton_actualizar.pack(side="left", padx=4)
        ttk.Button(botones, text="Mi historial", command=ver_historial).pack(side="left", padx=4)

        self.resultado = ttk.Label(self, text="", font=("Segoe UI", 12, "bold"))
        self.resultado.grid(row=5, column=0, columnspan=2)
        self.aviso = ttk.Label(self, text="", foreground=ROJO, wraplength=320)
        self.aviso.grid(row=6, column=0, columnspan=2)

        self.monto.bind("<Return>", lambda _e: self.convertir())
        self.cotizacion.bind("<Return>", lambda _e: self.convertir())
        self.monto.focus()
        self.actualizar_cotizacion()

    # --- cotización automática ---
    def actualizar_cotizacion(self):
        """Consulta la cotización en un hilo de fondo; la ventana sigue respondiendo."""
        if self.consultando:
            return
        self.consultando = True
        self.boton_actualizar.state(["disabled"])
        self.origen.config(text="Actualizando cotización…", foreground=GRIS)
        cola = self._cola = queue.Queue()
        consultar = self._consultar

        def trabajo():
            try:
                cola.put(("ok", consultar()))
            except Exception as e:  # cualquier falla es recuperable: se ingresa a mano
                cola.put(("error", str(e) or MENSAJE_FALLA))

        threading.Thread(target=trabajo, daemon=True).start()
        self._sondeo = self.after(50, self._revisar)

    def _revisar(self):
        try:
            estado, valor = self._cola.get_nowait()
        except queue.Empty:
            self._sondeo = self.after(50, self._revisar)
            return
        self._sondeo = None
        self.consultando = False
        self.boton_actualizar.state(["!disabled"])
        if estado == "ok":
            self.cotizacion.delete(0, "end")
            self.cotizacion.insert(0, texto_para_campo(valor.venta))
            fecha = formato_fecha_local(valor.fecha) if valor.fecha else ""
            texto = "Dólar oficial (venta)" + (f" · actualizado {fecha}" if fecha else "")
            self.origen.config(text=texto, foreground=GRIS)
        else:
            self.origen.config(text=valor, foreground=ROJO)

    def destroy(self):
        # Si la consulta sigue en curso, se cancela el sondeo y su resultado se descarta.
        if self._sondeo is not None:
            try:
                self.after_cancel(self._sondeo)
            except tk.TclError:
                pass
            self._sondeo = None
        super().destroy()

    # --- conversión ---
    def convertir(self):
        self.resultado.config(text="")
        self.aviso.config(text="")
        try:
            monto, cot, usd = convertir(self.monto.get(), self.cotizacion.get())
        except EntradaInvalida as e:
            self.aviso.config(text=str(e))
            return
        self.resultado.config(text=f"{formato_numero(usd)} USD")
        self.update_idletasks()
        try:
            pocketbase.guardar_consulta(self.sesion, monto, cot, usd)
        except pocketbase.ErrorPocketBase:
            self.aviso.config(text="No se pudo guardar la consulta en tu historial.")


class Cotizador(tk.Tk):
    def __init__(self, consultar=obtener_cotizacion):
        super().__init__()
        self.title("Mi Cotizador")
        self.resizable(False, False)
        self.pantalla = None
        self.sesion = None
        self._consultar = consultar
        self.mostrar_login()

    def _mostrar(self, pantalla):
        if self.pantalla is not None:
            self.pantalla.destroy()
        self.pantalla = pantalla
        pantalla.pack()

    def mostrar_login(self, mensaje=""):
        self.sesion = None
        login = PantallaLogin(self, self.entrar, self.mostrar_registro)
        self._mostrar(login)
        login.reiniciar(mensaje)

    def mostrar_registro(self):
        registro = PantallaRegistro(
            self,
            lambda email: self.mostrar_login("Cuenta creada. Ya podés iniciar sesión."),
            self.mostrar_login,
        )
        self._mostrar(registro)
        registro.reiniciar()

    def entrar(self, sesion):
        """Tras iniciar sesión: los admins ven el panel, los demás el conversor."""
        self.sesion = sesion
        if sesion.es_admin:
            self.mostrar_panel()
        else:
            self.mostrar_conversor()

    def mostrar_panel(self):
        self._mostrar(PanelAdmin(self, self.sesion, self.mostrar_conversor, self.mostrar_login))

    def mostrar_conversor(self):
        volver = self.mostrar_panel if self.sesion.es_admin else None
        self._mostrar(
            Conversor(
                self, self.sesion, self.mostrar_login, self.mostrar_historial, volver,
                consultar=self._consultar,
            )
        )

    def mostrar_historial(self):
        self._mostrar(PantallaHistorial(self, self.sesion, self.mostrar_conversor))


def main():
    Cotizador().mainloop()


if __name__ == "__main__":
    main()
