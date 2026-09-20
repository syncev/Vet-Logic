import tkinter as tk
from tkinter import ttk


class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="white", **kwargs)

        self._build_widgets()
        self._build_layout()

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
        self._build_appointments_table()

    # LAYOUT
    def _build_layout(self):
        top_frame = tk.Frame(self, bg="white")
        top_frame.pack(fill="x", padx=20, pady=20)

        left_controls = tk.Frame(top_frame, bg="white")
        left_controls.pack(side="left")
        self.entrada = tk.Entry(
            left_controls,
            width=40,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#CCCCCC",
            highlightcolor="#8A2BE2",
        )
        self.dropdown = ttk.Combobox(
            left_controls,
            values=[
                "Todos",
                "Cliente",
                "Paciente",
                "Especie",
                "Motivo",
                "HC",
                "Telefono",
            ],
            state="readonly",
            width=18,
        )
        self.dropdown.set("Todos")
        self.entrada.pack(side="left", padx=(0, 10))
        self.dropdown.pack(side="left")

        right_controls = tk.Frame(top_frame, bg="white")
        right_controls.pack(side="right")
        paginador_frame = tk.Frame(right_controls, bg="white")
        paginador_frame.pack(side="left", padx=(0, 20))

        self.btn_agregar = tk.Button(
            right_controls,
            text="+ Agregar Turno",
            font=("Arial", 11, "bold"),
            bg="#A8D5BA",
            fg="#1D3525",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5,
        )

        fuente_pag = ("Arial", 11, "bold")
        tk.Button(
            paginador_frame,
            text="<",
            font=fuente_pag,
            bg="#F0F0F0",
            relief="flat",
            width=3,
            cursor="hand2",
        ).pack(side="left", padx=2)
        tk.Button(
            paginador_frame,
            text="20",
            font=fuente_pag,
            bg="#F0F0F0",
            relief="flat",
            width=3,
            cursor="hand2",
        ).pack(side="left", padx=2)
        tk.Button(
            paginador_frame,
            text="21",
            font=fuente_pag,
            bg="#E6D0F5",
            relief="flat",
            width=3,
            cursor="hand2",
        ).pack(side="left", padx=2)
        tk.Button(
            paginador_frame,
            text="22",
            font=fuente_pag,
            bg="#F0F0F0",
            relief="flat",
            width=3,
            cursor="hand2",
        ).pack(side="left", padx=2)
        tk.Button(
            paginador_frame,
            text=">",
            font=fuente_pag,
            bg="#F0F0F0",
            relief="flat",
            width=3,
            cursor="hand2",
        ).pack(side="left", padx=2)

        self.btn_agregar.pack(side="left")
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




