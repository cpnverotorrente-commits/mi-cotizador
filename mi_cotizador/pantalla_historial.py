"""Pantalla "Mi historial": las consultas del propio usuario."""
from tkinter import ttk

from mi_cotizador import pocketbase
from mi_cotizador.logica import formato_fecha_local, formato_numero

ROJO = "#b00020"


class PantallaHistorial(ttk.Frame):
    def __init__(self, master, sesion, volver):
        super().__init__(master, padding=15)
        self.sesion = sesion

        cabecera = ttk.Frame(self)
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(cabecera, text="Mi historial", font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(cabecera, text="Volver", command=volver).pack(side="right")
        ttk.Button(cabecera, text="Actualizar", command=self.cargar).pack(side="right", padx=6)

        self.tabla = ttk.Treeview(
            self, columns=("fecha", "monto", "cotizacion", "resultado"), show="headings", height=12
        )
        for col, texto, ancho, ancla in (
            ("fecha", "Fecha y hora", 150, "w"),
            ("monto", "Monto (ARS)", 120, "e"),
            ("cotizacion", "Cotización", 100, "e"),
            ("resultado", "Resultado (USD)", 120, "e"),
        ):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor=ancla)
        self.tabla.grid(row=1, column=0)

        self.mensaje = ttk.Label(self, text="", wraplength=480)
        self.mensaje.grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.cargar()

    def avisar(self, texto, color=ROJO):
        self.mensaje.config(text=texto, foreground=color)

    def cargar(self):
        try:
            consultas = pocketbase.listar_consultas(self.sesion)
        except pocketbase.ErrorPocketBase as e:
            self.avisar(str(e))
            return
        self.tabla.delete(*self.tabla.get_children())
        for c in consultas:
            self.tabla.insert(
                "", "end",
                values=(
                    formato_fecha_local(c.fecha),
                    formato_numero(c.monto),
                    formato_numero(c.cotizacion),
                    formato_numero(c.resultado),
                ),
            )
        if consultas:
            self.avisar(f"{len(consultas)} conversión(es), la más reciente primero.", "#1b5e20")
        else:
            self.avisar("Todavía no hiciste conversiones.", "#444444")
