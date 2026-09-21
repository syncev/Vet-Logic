from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import tkinter as tk
from tkinter import ttk

# Asumiendo que tenés la barra de búsqueda importada si la usás, 
# aunque en tu código vi que creaste el Entry directo. Podés borrar esto si no lo usás.
from ui.widgets.searchbar import Searchbar 

class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        # Aseguramos el fondo blanco general
        super().__init__(master, bg="white", **kwargs)

        self._build_widgets()
        self._build_layout()

    # LOGICA
    def _build_date_stepper(self):
        # EL ARREGLO ESTÁ ACÁ: Le asignamos self.right_controls como padre
        self.date_stepper = tk.Frame(self.right_controls, bg="white")
        timezone = ZoneInfo("America/Argentina/Buenos_Aires")

        today = datetime.now(timezone)
        tomorrow = today + timedelta(days=1)
        next_day = today + timedelta(days=2)

        fuente_pag = ("Arial", 11, "bold")

        self.previous_button = tk.Button(self.date_stepper, text="<", font=fuente_pag, bg="#F0F0F0", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2")
        self.today_button = tk.Button(self.date_stepper, text=str(today.day), font=fuente_pag, bg="#E6D0F5", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2")
        self.tomorrow_button = tk.Button(self.date_stepper, text=str(tomorrow.day), font=fuente_pag, bg="#F0F0F0", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2")
        self.next_day_button = tk.Button(self.date_stepper, text=str(next_day.day), font=fuente_pag, bg="#F0F0F0", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2")
        self.next_button = tk.Button(self.date_stepper, text=">", font=fuente_pag, bg="#F0F0F0", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2")

    # tabla de turnos
    def _build_appointments_table(self):
        # Aseguramos el fondo blanco detrás de la tabla
        self.appointments_frame = tk.Frame(self, bg="white")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white", rowheight=40, borderwidth=0, font=("Arial", 10))
        style.configure("Treeview.Heading", background="white", font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", "#F0F0F0")], foreground=[("selected", "black")])

        self.appointments_table = ttk.Treeview(
            self.appointments_frame,
            columns=("hora", "cliente", "pacliente", "especie", "motivo", "hc", "ultimo turno"),
            show="headings",
        )
        
        self.appointments_table.heading("hora", text="Hora")
        self.appointments_table.heading("cliente", text="Cliente", anchor="w")
        self.appointments_table.heading("pacliente", text="Paciente", anchor="w")
        self.appointments_table.heading("especie", text="Especie")
        self.appointments_table.heading("motivo", text="Motivo")
        self.appointments_table.heading("hc", text="HC")
        self.appointments_table.heading("ultimo turno", text="Último Turno")
        
        self.appointments_table.column("hora", width=50)
        self.appointments_table.column("cliente", width=150, anchor="w")
        self.appointments_table.column("pacliente", width=100, anchor="w")
        self.appointments_table.column("especie", width=80, anchor="center")
        self.appointments_table.column("motivo", width=100, anchor="center")
        self.appointments_table.column("hc", width=70, anchor="center")
        self.appointments_table.column("ultimo turno", width=150, anchor="center")
        
        appointments = [
            ("08:00", "Juan Perez", "Firulais", "Perro", "Clinica", "12345", "2025-09-01"),
            ("09:00", "Maria Lopez", "Lord Pulgoso", "Perro", "Peluqueria", "67890", "2026-03-02"),
        ]
        for appointment in appointments:
            self.appointments_table.insert("", "end", values=appointment)

    # WIDGETS
    def _build_widgets(self):
        self.top_frame = tk.Frame(self, bg="white")
        self.left_controls = tk.Frame(self.top_frame, bg="white")
        self.right_controls = tk.Frame(self.top_frame, bg="white")

        self.entrada = tk.Entry(
            self.left_controls,
            width=28,
            font=("Arial", 10),
            bd=1,
            relief="solid",
        )
        self.dropdown = ttk.Combobox(
            self.left_controls,
            values=["Todos", "Cliente", "Paciente", "Especie", "Motivo", "HC"],
            state="readonly",
            width=17,
        )
        self.dropdown.set("Todos")

        # Construimos el paginador (ahora se aloja en right_controls)
        self._build_date_stepper()

        self.add_appointment_button = tk.Button(
            self.right_controls,
            text="+ Agregar Turno",
            bg="#A8D5BA",
            fg="#1D3525",
            font=("Arial", 11, "bold"),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            padx=15,
            pady=5,
        )

        self._build_appointments_table()

    # LAYOUT
    def _build_layout(self):
        # 1. Empaquetamos cabecera
        self.top_frame.pack(fill="x", padx=20, pady=(20, 10))

        # 2. Controles izquierdos
        self.left_controls.pack(side="left")
        self.entrada.pack(side="left", padx=(0, 10))
        self.dropdown.pack(side="left")

        # 3. Controles derechos
        self.right_controls.pack(side="right")
        
        # Paginador pegado a la izquierda dentro del bloque derecho
        self.date_stepper.pack(side="left", padx=(0, 20))
        self.previous_button.pack(side="left", padx=2)
        self.today_button.pack(side="left", padx=2)
        self.tomorrow_button.pack(side="left", padx=2)
        self.next_day_button.pack(side="left", padx=2)
        self.next_button.pack(side="left", padx=2)
        
        # Botón verde pegado a la derecha del paginador
        self.add_appointment_button.pack(side="left", ipadx=15, ipady=8)

        # 4. Tabla ocupando el resto
        self.appointments_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.appointments_table.pack(fill="both", expand=True)