from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import tkinter as tk
from tkinter import ttk

from core.db import conectar
from repositories.turno import obtener_turnos_por_fecha

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
        self.selected_date = today.date()

        fuente_pag = ("Arial", 11, "bold")

        self.previous_button = tk.Button(self.date_stepper, text="<", font=fuente_pag, bg="#F0F0F0", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2", command=lambda: self._change_selected_date(-1))
        self.today_button = tk.Button(self.date_stepper, text=str(today.day), font=fuente_pag, bg="#E6D0F5", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2", command=lambda: self._select_date(self.selected_date))
        self.tomorrow_button = tk.Button(self.date_stepper, text=str(tomorrow.day), font=fuente_pag, bg="#F0F0F0", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2", command=lambda: self._select_date(self.selected_date + timedelta(days=1)))
        self.next_day_button = tk.Button(self.date_stepper, text=str(next_day.day), font=fuente_pag, bg="#F0F0F0", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2", command=lambda: self._select_date(self.selected_date + timedelta(days=2)))
        self.next_button = tk.Button(self.date_stepper, text=">", font=fuente_pag, bg="#F0F0F0", fg="#333333", relief="flat", borderwidth=0, highlightthickness=0, width=3, cursor="hand2", command=lambda: self._change_selected_date(1))

    def _change_selected_date(self, days):
        self._select_date(self.selected_date + timedelta(days=days))

    def _select_date(self, fecha):
        self.selected_date = fecha
        self.today_button.configure(text=str(fecha.day), bg="#E6D0F5")
        self.tomorrow_button.configure(text=str((fecha + timedelta(days=1)).day), bg="#F0F0F0")
        self.next_day_button.configure(text=str((fecha + timedelta(days=2)).day), bg="#F0F0F0")
        self.cargar_turnos_fecha(fecha)

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
        self.appointments_table.tag_configure("cirugia", background="#EFE8F8")

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
        
        self.appointments = []

    def cargar_turnos_fecha(self, fecha):
        try:
            with conectar() as conexion:
                self.appointments = obtener_turnos_por_fecha(conexion, fecha)
        except Exception as e:
            print(f"Error al cargar turnos: {e}")
            self.appointments = []

        for item in self.appointments_table.get_children():
            self.appointments_table.delete(item)

        for appointment in self.appointments:
            motivo = str(appointment[4]).casefold()
            tag = ("cirugia",) if motivo in ("cirugia", "cirugía") else ()
            self.appointments_table.insert("", "end", values=appointment, tags=tag)
    
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
            columns_to_search = range(len(self.appointments_table["columns"]))
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
            motivo = str(appointment[4]).casefold()
            tag = ("cirugia",) if motivo in ("cirugia", "cirugía") else ()
            
            self.appointments_table.insert(
                "",
                "end",
                values=appointment, tags=tag
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
        self._select_date(self.selected_date)

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