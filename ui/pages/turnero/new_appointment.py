import tkinter as tk
from datetime import datetime
from tkinter import ttk
from zoneinfo import ZoneInfo

from ui.pages.turnero.horarios_selector import HorariosSelector
from ui.widgets.calendar_picker import CalendarPicker

# Desactivado temporalmente mientras la base de datos no esta disponible.
# import psycopg
# from core.db import conectar
# from repositories.turno import obtener_horarios_ocupados


class NewAppointmentPage(tk.Frame):
    REASONS = ("Clinica", "Vacunacion", "Cirugia", "Otros")

    def __init__(self, master, on_save=None, **kwargs):
        super().__init__(master, bg="white", **kwargs)

        self.on_save = on_save
        self.entries = {}
        # Esta fecha se comparte entre el calendario y el selector de horarios.
        self.fecha_seleccionada = datetime.now(
            ZoneInfo("America/Argentina/Buenos_Aires")
        ).date()
        self.horario_seleccionado = None

        self._configure_styles()
        self._build_header()
        self._build_scrollable_body()
        self._build_form()
        self._build_schedule()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.configure(
            "Appointment.TEntry",
            fieldbackground="#EEEEEE",
            padding=8,
        )
        style.configure(
            "Appointment.TCombobox",
            fieldbackground="#EEEEEE",
            padding=6,
        )

    def _build_header(self):
        header = tk.Frame(self, bg="#D2C2ED", height=48)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(
            header,
            text="←",
            font=("Arial", 23, "bold"),
            bg="#D2C2ED",
            fg="#666666",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._close,
        ).pack(side="left", padx=18)

        tk.Label(
            header,
            text="Registrar Paciente nuevo",
            font=("Arial", 16),
            bg="#D2C2ED",
            fg="#111111",
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _build_scrollable_body(self):
        body = tk.Frame(self, bg="white")
        body.pack(fill="both", expand=True)

        # Tkinter Frame no tiene scroll propio: el Canvas desplaza este Frame interno.
        self.canvas = tk.Canvas(
            body,
            bg="white",
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            body,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.form_content = tk.Frame(self.canvas, bg="white", padx=30, pady=24)
        self.form_window = self.canvas.create_window(
            (0, 0),
            window=self.form_content,
            anchor="nw",
        )

        # El scrollregion sigue el tamaño del contenido; el contenido sigue el ancho visible.
        self.form_content.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.form_window,
                width=event.width,
            ),
        )

    def _build_form(self):
        for column in range(3):
            self.form_content.columnconfigure(column, weight=1, uniform="fields")

        self._add_section_title("Datos del Cliente", row=0)
        self._add_field("Nombre", "client_name", row=1, column=0)
        self._add_field("Apellido", "client_lastname", row=1, column=1)
        self._add_field("DNI", "dni", row=1, column=2)
        self._add_field("Telefono", "phone", row=2, column=0)

        self._add_section_title("Datos del Paciente", row=3)
        self._add_field("Nombre", "pet_name", row=4, column=0)
        self._add_field(
            "Especie",
            "species",
            row=4,
            column=1,
            values=("Perro", "Gato", "Otro"),
        )
        self._add_field("Raza", "breed", row=4, column=2)

        tk.Label(
            self.form_content,
            text="Motivo",
            bg="white",
            font=("Arial", 11, "bold"),
        ).grid(row=5, column=0, sticky="w", pady=(28, 8))

        tk.Label(
            self.form_content,
            text="Fecha",
            bg="white",
            font=("Arial", 11, "bold"),
        ).grid(row=5, column=1, columnspan=2, sticky="w", pady=(28, 8))

        self.reason = ttk.Combobox(
            self.form_content,
            values=self.REASONS,
            state="readonly",
            style="Appointment.TCombobox",
        )
        self.reason.set(self.REASONS[0])
        self.reason.grid(row=6, column=0, sticky="ew", padx=(0, 24))

        # El widget notifica la fecha elegida; esta página refresca los horarios disponibles.
        self.calendar_picker = CalendarPicker(
            self.form_content,
            selected_date=self.fecha_seleccionada,
            on_date_selected=self._on_calendar_date_selected,
        )
        self.calendar_picker.grid(
            row=6,
            column=1,
            columnspan=2,
            sticky="w",
        )

    def _add_section_title(self, text, row):
        tk.Label(
            self.form_content,
            text=text,
            bg="white",
            font=("Arial", 11, "bold"),
        ).grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(12, 10),
        )

    def _add_field(self, label, key, row, column, values=None):
        field = tk.Frame(self.form_content, bg="white")
        field.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=(0, 18),
            pady=7,
        )

        tk.Label(
            field,
            text=label,
            bg="white",
            width=9,
            anchor="w",
        ).pack(side="left")

        if values:
            widget = ttk.Combobox(
                field,
                values=values,
                state="readonly",
                style="Appointment.TCombobox",
            )
            widget.set(values[0])
        else:
            widget = ttk.Entry(
                field,
                style="Appointment.TEntry",
            )

        widget.pack(side="left", fill="x", expand=True)
        self.entries[key] = widget

    def _build_schedule(self):
        tk.Label(
            self.form_content,
            text="Horarios disponibles",
            bg="white",
            font=("Arial", 11, "bold"),
        ).grid(row=7, column=0, columnspan=3, sticky="w", pady=(24, 8))

        self.schedule_status = tk.Label(
            self.form_content,
            text="",
            bg="white",
            fg="#A33A3A",
            anchor="w",
        )
        self.schedule_status.grid(
            row=8,
            column=0,
            columnspan=3,
            sticky="ew",
        )

        # El selector dibuja los horarios; la página le pasa ocupación y recibe sus eventos.
        self.horarios_selector = HorariosSelector(
            self.form_content,
            fecha_base=self.fecha_seleccionada,
            horarios_ocupados=self._get_occupied_slots(
                self.fecha_seleccionada
            ),
            on_fecha_base_change=self._on_schedule_date_change,
            on_horario_seleccionado=self._on_time_selected,
        )
        self.horarios_selector.grid(
            row=9,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(4, 20),
        )

        self.confirm_button = tk.Button(
            self.form_content,
            text="Agendar Turno",
            bg="#61D161",
            fg="black",
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            state=tk.DISABLED,
            command=self._confirmar_turno,
        )
        self.confirm_button.grid(
            row=10,
            column=0,
            columnspan=3,
            pady=(12, 24),
        )

    def _get_occupied_slots(self, base_date):
        # Rehabilitar la consulta cuando la base de datos este disponible:
        # try:
        #     with conectar() as connection:
        #         occupied = obtener_horarios_ocupados(connection, base_date)
        #     self.schedule_status.configure(text="")
        #     return occupied
        # except (psycopg.Error, OSError, ValueError, KeyError) as error:
        #     self.schedule_status.configure(
        #         text="No se pudieron consultar los horarios; quedan deshabilitados."
        #     )
        #     print(f"Error al consultar horarios: {error}")
        #     return {
        #         (base_date + timedelta(days=offset), hour)
        #         for offset in range(3)
        #         for hour in HorariosSelector.HORARIOS
        #     }

        self.schedule_status.configure(text="")
        # Sin consulta a la DB, ningún horario se considera ocupado.
        return set()

    def _confirmar_turno(self):
        if self.horario_seleccionado is None:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Confirmar turno")
        dialog.geometry("380x190")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Confirmar Turno",
            font=("Arial", 16, "bold"),
        ).pack(pady=(20, 8))

        tk.Label(
            dialog,
            text="¿Desea confirmar el turno en la fecha y horario seleccionados?",
            font=("Arial", 11),
            wraplength=320,
        ).pack(padx=20, pady=8)

        botones = tk.Frame(dialog)
        botones.pack(pady=12)

        tk.Button(
            botones,
            text="VOLVER",
            command=dialog.destroy,
        ).pack(side="left", padx=10)

        def continuar():
            fecha, hora = self.horario_seleccionado
            datos = {
                "cliente": (
                    f"{self.entries['client_name'].get().strip()} "
                    f"{self.entries['client_lastname'].get().strip()}"
                ).strip(),
                "paciente": self.entries["pet_name"].get().strip(),
                "contacto": self.entries["phone"].get().strip(),
                "fecha": fecha,
                "hora": hora,
                "motivo": self.reason.get(),
            }
            dialog.destroy()
            if self.on_save is not None:
                self.on_save(datos)

        tk.Button(
            botones,
            text="CONTINUAR",
            bg="#61D161",
            command=continuar,
        ).pack(side="left", padx=10)

        self._centrar_dialogo(dialog)

    def _centrar_dialogo(self, dialog):
        parent = self.winfo_toplevel()
        parent.update_idletasks()
        dialog.update_idletasks()

        x = parent.winfo_rootx() + (
            parent.winfo_width() - dialog.winfo_width()
        ) // 2
        y = parent.winfo_rooty() + (
            parent.winfo_height() - dialog.winfo_height()
        ) // 2
        dialog.geometry(f"+{x}+{y}")

    def _on_calendar_date_selected(self, selected_date):
        self.fecha_seleccionada = selected_date
        self.horario_seleccionado = None
        self.confirm_button.configure(state=tk.DISABLED)
        self._refresh_schedule()

    def _refresh_schedule(self):
        # El horario elegido para la fecha anterior ya no es válido.
        self.horarios_selector.horario_seleccionado = None
        self.horarios_selector.actualizar_datos(
            self.fecha_seleccionada,
            self._get_occupied_slots(self.fecha_seleccionada),
        )

    def _on_schedule_date_change(self, new_base_date):
        self.fecha_seleccionada = new_base_date
        self.horario_seleccionado = None
        self.confirm_button.configure(state=tk.DISABLED)
        # La navegación del selector también debe reflejarse en el calendario.
        self.calendar_picker.set_date(new_base_date)
        self._refresh_schedule()

    def _on_time_selected(self, selected_date, selected_time):
        self.fecha_seleccionada = selected_date
        # El selector entrega ambos valores; se conservan juntos para enviar el turno.
        self.horario_seleccionado = (selected_date, selected_time)
        self.confirm_button.configure(state=tk.NORMAL)
        self.calendar_picker.set_date(selected_date)

    def _close(self):
        self.winfo_toplevel().destroy()