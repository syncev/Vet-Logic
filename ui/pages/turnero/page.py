from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import tkinter as tk
from tkinter import ttk

from ui.widgets.searchbar import Searchbar


class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._build_widgets()
        self._build_layout()

    # LOGICA
    # date stepper es el widget que permite cambiar de dia de 1 en 1 en el turnero
    def _build_date_stepper(self):
        self.date_stepper = tk.Frame(self)
        timezone = ZoneInfo("America/Argentina/Buenos_Aires")

        # logca para que los dias se sumen sin pasar de 31 a 32
        today = datetime.now(timezone)
        tomorrow = today + timedelta(days=1)
        next_day = today + timedelta(days=2)

        self.previous_button = tk.Button(
            self.date_stepper,
            text="<",
        )
        self.today_button = tk.Button(
            self.date_stepper,
            text=str(today.day),
        )
        self.tomorrow_button = tk.Button(
            self.date_stepper,
            text=str(tomorrow.day),
        )
        self.next_day_button = tk.Button(
            self.date_stepper,
            text=str(next_day.day),
        )
        self.next_button = tk.Button(
            self.date_stepper,
            text=">",
        )

    # tabla de turnos
    def _build_appointments_table(self):
        self.appointments_frame = tk.Frame(self)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            rowheight=40,
            borderwidth=0,
            font=("Arial", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="white",
            font=("Arial", 10, "bold"),
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", "#F0F0F0")],
            foreground=[("selected", "black")],
        )

        self.appointments_table = ttk.Treeview(
            self.appointments_frame,
            columns=(
                "hora",
                "cliente",
                "pacliente",
                "especie",
                "motivo",
                "hc",
                "ultimo turno",
            ),
            show="headings",
        )
        # esto ata el encabezado de la tabla con el nombre de la columna
        self.appointments_table.heading("hora", text="Hora")
        self.appointments_table.heading("cliente", text="Cliente", anchor="w")
        self.appointments_table.heading("pacliente", text="Paciente", anchor="w")
        self.appointments_table.heading("especie", text="Especie")
        self.appointments_table.heading("motivo", text="Motivo")
        self.appointments_table.heading("hc", text="HC")
        self.appointments_table.heading("ultimo turno", text="Último Turno")
        # config de las columnas
        self.appointments_table.column(
            "hora",
            width=50,
        )
        self.appointments_table.column(
            "cliente",
            width=150,
            anchor="w",
        )
        self.appointments_table.column(
            "pacliente",
            width=100,
            anchor="w",
        )
        self.appointments_table.column(
            "especie",
            width=80,
            anchor="center",

        )
        self.appointments_table.column(
            "motivo",
            width=100,
            anchor="center",
        )
        self.appointments_table.column(
            "hc",
            width=70,
            anchor="center",
        )
        self.appointments_table.column(
            "ultimo turno",
            width=150,
            anchor="center",
        )
        # citas harcodeadadas TODO reemplazar por acceso a la base de datos
        appointments = [
            (
                "08:00",
                "Juan Perez",
                "Firulais",
                "Perro",
                "Clinica",
                "12345",
                "2025-09-01",
            ),
            (
                "09:00",
                "Maria Lopez",
                "Lord Pulgoso",
                "Perro",
                "Peluqueria",
                "67890",
                "2026-03-02",
            ),
        ]
        for appointment in appointments:
            self.appointments_table.insert(
                "",
                "end",
                values=appointment,
            )

    # WIDGETS
    def _build_widgets(self):
        # importa el searchbar que es un widget reciclable
        self.searchbar = Searchbar(self)

        self._build_date_stepper()

        # boton de agregar turno
        self.add_appointment_button = tk.Button(
            self,
            text="+ Agregar Turno",
        )

        self._build_appointments_table()

    # LAYOUT
    def _build_layout(self):
        self.searchbar.pack(
            fill="x",
            padx=40,
            pady=30,
        )
        self.date_stepper.pack()
        self.previous_button.pack(side="left")
        self.today_button.pack(side="left")
        self.tomorrow_button.pack(side="left")
        self.next_day_button.pack(side="left")
        self.next_button.pack(side="left")
        self.add_appointment_button.pack()
        self.appointments_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )
        self.appointments_table.pack(
            fill="both",
            expand=True,
        )
