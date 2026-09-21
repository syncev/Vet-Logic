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
        
        # Citas hardcodeadas sacadas del diseño de Figma
        self.appointments = [
            ("09:00", "Silvia Moreno", "Luna", "Gato", "Clinica", "12651", "08/08/2024"),
            ("09:30", "Martin Sanchez", "Milo", "Gato", "Clinica", "15644", "04/05/2023"),
            ("10:00", "Calvin Klein", "Thor", "Perro", "Clinica", "65111", "20/05/2026"),
            ("10:30", "Clark Kent", "Homero", "Perro", "Peluqueria", "32155", "27/08/2026"),
            ("10:30", "Maria del Barrio", "Otto", "Gato", "Clinica", "75465", "07/12/2023"),
            ("11:00", "Esteban Caracas", "Rafa", "Perro", "Clinica", "84223", "30/02/2026"),
            ("11:30", "Philomena Cunk", "Ara", "Gato", "Clinica", "51511", "01/02/2025"),
            ("11:30", "Lydia Deetz", "Uma", "Perro", "Peluqueria", "21578", "05/11/2025"),
            ("12:00", "Sabrina Carpintero", "Corcho", "Perro", "Clinica", "35698", "06/07/2025"),
            ("12:30", "Britney Lanzas", "Simba", "Gato", "Clinica", "32151", "29/07/2026"),
            ("13:00", "Martin Pescador", "Max", "Perro", "Clinica", "35169", "15/07/2025"),
            ("13:15", "Alberto Cazador", "Sasha", "Perro", "Peluqueria", "32169", "21/04/2025"),
            ("13:30", "Dustin Henderson", "Rocky", "Gato", "Clinica", "11458", "19/10/2025")
        ]
        for appointment in self.appointments:
            self.appointments_table.insert("", "end", values=appointment)
    
    def search_appointments(self, query, selected_filter):
        query = query.lower()

        filter_columns = {
            "Cliente": [1],
            "Paciente": [2],
            "Especie": [3],
            "Motivo": [4],
            "HC": [5]   
        }

        if selected_filter == "Todos":
            columns_to_search = range(len(self.appointments[0]))
        else:
            columns_to_search = filter_columns.get(selected_filter, [])

        filtered_appointments = []

        for appointment in self.appointments:
            if any(
                query in str(appointment[column]).lower()
                for column in columns_to_search
            ):
                filtered_appointments.append(appointment)

        for item in self.appointments_table.get_children():
            self.appointments_table.delete(item) 

        for appointment in filtered_appointments:
            self.appointments_table.insert(
                "",
                "end",
                values=appointment,
        )           

    # WIDGETS
    def _build_widgets(self):
        self.top_frame = tk.Frame(
            self,
            height=80,
            bg="white",
            )
        self.top_frame.pack_propagate(False)
        self.searchbar = Searchbar(
            self.top_frame,
            on_search=self.search_appointments,
            )
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
        self.top_frame.pack(
            fill="x",
            padx=40,
            pady=(0, 10),
        )

        self.searchbar.pack(
            side="left",
            fill="both",
            expand=True,
        )

        self.right_controls.pack(
            side="right",
            anchor="nw",
            pady=(52, 0),
            )

        self.date_stepper.pack(side="left", padx=(0, 20))

        self.previous_button.pack(side="left")
        self.today_button.pack(side="left")
        self.tomorrow_button.pack(side="left")
        self.next_day_button.pack(side="left")
        self.next_button.pack(side="left")

        self.add_appointment_button.pack(side="left", padx=(20, 0))

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