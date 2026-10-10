import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ui.widgets.searchbar import Searchbar


class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="white", **kwargs)

        self._build_widgets()
        self._build_layout()

    def abrir_formulario_turno(self):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar turno")
        ventana.geometry("420x420")
        ventana.resizable(False, False)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        frame = tk.Frame(ventana, padx=20, pady=20, bg="white")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Hora", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        hora_entry = tk.Entry(frame, width=30)
        hora_entry.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="Cliente", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        cliente_entry = tk.Entry(frame, width=30)
        cliente_entry.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="Paciente", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        paciente_entry = tk.Entry(frame, width=30)
        paciente_entry.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="Especie", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        especie_entry = tk.Entry(frame, width=30)
        especie_entry.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="Motivo", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        motivo_entry = tk.Entry(frame, width=30)
        motivo_entry.pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="HC", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
        hc_entry = tk.Entry(frame, width=30)
        hc_entry.pack(fill="x", pady=(0, 10))

        def guardar_turno():
            hora = hora_entry.get().strip()
            cliente = cliente_entry.get().strip()
            paciente = paciente_entry.get().strip()
            especie = especie_entry.get().strip()
            motivo = motivo_entry.get().strip()
            hc = hc_entry.get().strip()

            if not all([hora, cliente, paciente, especie, motivo, hc]):
                return

            nuevo_turno = (hora, cliente, paciente, especie, motivo, hc, "Hoy")
            self.appointments.append(nuevo_turno)
            self.appointments_table.insert("", "end", values=nuevo_turno)
            ventana.destroy()

        tk.Button(
            frame,
            text="Guardar",
            bg="#8A2BE2",
            fg="white",
            font=("Arial", 10, "bold"),
            command=guardar_turno,
        ).pack(fill="x", pady=(10, 0))

    def _build_widgets(self):
        self.top_frame = tk.Frame(self, height=80, bg="white")
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
            command=self.abrir_formulario_turno,
        )

        self._build_appointments_table()

    def _build_layout(self):
        self.top_frame.pack(fill="x", padx=40, pady=(0, 10))
        self.searchbar.pack(side="left", fill="both", expand=True)
        self.right_controls.pack(side="right", anchor="nw", pady=(52, 0))
        self.date_stepper.pack(side="left", padx=(0, 20))
        self.previous_button.pack(side="left")
        self.today_button.pack(side="left")
        self.tomorrow_button.pack(side="left")
        self.next_day_button.pack(side="left")
        self.next_button.pack(side="left")
        self.add_appointment_button.pack(side="left", padx=(20, 0))

        self.appointments_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.appointments_table.pack(fill="both", expand=True)