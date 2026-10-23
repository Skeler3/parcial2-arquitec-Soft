"""
Publicador (Python + Tkinter)
"""
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pika

RABBIT_URL = "amqp://guest:guest@localhost:5672"
EXCHANGE = "ropa_exchange"
MARCAS = ["adidas", "nike"]
PRODUCTOS = ["camiseta", "pantaloneta", "sudadera", "gorra", "medias"]


def publicar(pedido: dict) -> None:
    """Abre una conexión, declara el exchange y publica el mensaje JSON con la marca como routing key."""
    conexion = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
    try:
        canal = conexion.channel()
        canal.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
        canal.basic_publish(
            exchange=EXCHANGE,
            routing_key=pedido["marca"],  # decide a qué suscriptor llega
            body=json.dumps(pedido, ensure_ascii=False).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  # mensaje persistente
            ),
        )
    finally:
        conexion.close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Publicidad de ropa - Publicador")
        self.geometry("460x460")
        self.resizable(False, False)

        estilo = ttk.Style(self)
        estilo.configure("TLabel", font=("Segoe UI", 10))
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 14, "bold"))
        estilo.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

        marco = ttk.Frame(self, padding=20)
        marco.pack(fill="both", expand=True)

        ttk.Label(marco, text="Nueva publicación", style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 15), sticky="w"
        )

        ttk.Label(marco, text="Marca:").grid(row=1, column=0, sticky="w", pady=5)
        self.marca = ttk.Combobox(marco, values=MARCAS, state="readonly", width=28)
        self.marca.current(0)
        self.marca.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(marco, text="Producto:").grid(row=2, column=0, sticky="w", pady=5)
        self.producto = ttk.Combobox(marco, values=PRODUCTOS, width=28)
        self.producto.grid(row=2, column=1, sticky="ew", pady=5)
        self.producto.focus()

        ttk.Label(marco, text="Cantidad:").grid(row=3, column=0, sticky="w", pady=5)
        self.cantidad = ttk.Spinbox(marco, from_=1, to=1000, width=10)
        self.cantidad.set(1)
        self.cantidad.grid(row=3, column=1, sticky="w", pady=5)

        ttk.Button(marco, text="Publicar", command=self.enviar).grid(
            row=4, column=0, columnspan=2, pady=15, sticky="ew"
        )

        ttk.Label(marco, text="Mensajes enviados:").grid(row=5, column=0, columnspan=2, sticky="w")
        self.historial = tk.Listbox(marco, height=9, font=("Consolas", 9))
        self.historial.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(5, 0))

        marco.columnconfigure(1, weight=1)
        self.bind("<Return>", lambda _e: self.enviar())

    def enviar(self):
        marca = self.marca.get()
        producto = self.producto.get().strip()
        cantidad_txt = self.cantidad.get().strip()

        if not producto:
            messagebox.showwarning("Dato faltante", "Escribe o selecciona un producto.")
            return
        if not cantidad_txt.isdigit() or int(cantidad_txt) <= 0:
            messagebox.showwarning("Dato inválido", "La cantidad debe ser un número entero mayor que 0.")
            return

        pedido = {"marca": marca, "producto": producto, "cantidad": int(cantidad_txt)}

        try:
            publicar(pedido)
        except pika.exceptions.AMQPConnectionError:
            messagebox.showerror(
                "Sin conexión",
                "No se pudo conectar a RabbitMQ.\nRevisa RABBIT_URL y que el servidor esté activo.",
            )
            return

        hora = datetime.now().strftime("%H:%M:%S")
        self.historial.insert(0, f"[{hora}] -> {marca}: {producto} x{pedido['cantidad']}")
        self.producto.set("")
        self.cantidad.set(1)
        self.producto.focus()

if __name__ == "__main__":
    App().mainloop()
