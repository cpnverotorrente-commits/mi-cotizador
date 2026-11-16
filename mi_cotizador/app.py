"""Ventana de Mi Cotizador (Tkinter)."""
import tkinter as tk
from tkinter import ttk

from mi_cotizador import historial
from mi_cotizador.logica import EntradaInvalida, convertir


def formato_usd(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class Cotizador(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mi Cotizador")
        self.resizable(False, False)

        marco = ttk.Frame(self, padding=20)
        marco.grid()

        ttk.Label(marco, text="Monto en pesos:").grid(row=0, column=0, sticky="w", pady=4)
        self.monto = ttk.Entry(marco, width=20)
        self.monto.grid(row=0, column=1, pady=4, padx=(10, 0))

        ttk.Label(marco, text="Cotización del dólar:").grid(row=1, column=0, sticky="w", pady=4)
        self.cotizacion = ttk.Entry(marco, width=20)
        self.cotizacion.grid(row=1, column=1, pady=4, padx=(10, 0))

        ttk.Button(marco, text="Convertir", command=self.convertir).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        self.resultado = ttk.Label(marco, text="", font=("Segoe UI", 12, "bold"))
        self.resultado.grid(row=3, column=0, columnspan=2)
        self.aviso = ttk.Label(marco, text="", foreground="#b00020", wraplength=300)
        self.aviso.grid(row=4, column=0, columnspan=2)

        self.bind("<Return>", lambda _e: self.convertir())
        self.monto.focus()

    def convertir(self):
        self.resultado.config(text="")
        self.aviso.config(text="")
        try:
            monto, cot, usd = convertir(self.monto.get(), self.cotizacion.get())
        except EntradaInvalida as e:
            self.aviso.config(text=str(e))
            return
        self.resultado.config(text=f"{formato_usd(usd)} USD")
        try:
            historial.guardar(monto, cot, usd)
        except OSError:
            self.aviso.config(text="No se pudo guardar en historial.txt.")


def main():
    Cotizador().mainloop()


if __name__ == "__main__":
    main()
