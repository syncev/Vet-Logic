from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import tkinter as tk
from tkinter import ttk

from core.db import conectar
from ui.pages.turnero.new_appointment import NewAppointmentPage
from repositories.turno import (
    obtener_turnos_por_fecha,
    resolver_estado_visual,
)

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

        self.previous_button = tk.Button(
            self.date_stepper,
            text="<",
            font=fuente_pag,
            bg="#F0F0F0",
            fg="#333333",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            width=3,
            cursor="hand2",
            command=lambda: self._change_selected_date(-1),
        )
        self.today_button = tk.Button(
            self.date_stepper,
            text=str(today.day),
            font=fuente_pag,
            bg="#E6D0F5",
            fg="#333333",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            width=3,
            cursor="hand2",
            command=lambda: self._select_date(self.selected_date),
        )
        self.tomorrow_button = tk.Button(
            self.date_stepper,
            text=str(tomorrow.day),
            font=fuente_pag,
            bg="#F0F0F0",
            fg="#333333",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            width=3,
            cursor="hand2",
            command=lambda: self._select_date(self.selected_date + timedelta(days=1)),
        )
        self.next_day_button = tk.Button(
            self.date_stepper,
            text=str(next_day.day),
            font=fuente_pag,
            bg="#F0F0F0",
            fg="#333333",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            width=3,
            cursor="hand2",
            command=lambda: self._select_date(self.selected_date + timedelta(days=2)),
        )
        self.next_button = tk.Button(
            self.date_stepper,
            text=">",
            font=fuente_pag,
            bg="#F0F0F0",
            fg="#333333",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            width=3,
            cursor="hand2",
            command=lambda: self._change_selected_date(1),
        )

    def _change_selected_date(self, days):
        self._select_date(self.selected_date + timedelta(days=days))

    def _select_date(self, fecha):
        self.selected_date = fecha
        self.today_button.configure(text=str(fecha.day), bg="#E6D0F5")
        self.tomorrow_button.configure(
            text=str((fecha + timedelta(days=1)).day), bg="#F0F0F0"
        )
        self.next_day_button.configure(
            text=str((fecha + timedelta(days=2)).day), bg="#F0F0F0"
        )
        self.cargar_turnos_fecha(fecha)

    # tabla de turnos
    def _build_appointments_table(self):
        # Aseguramos el fondo blanco detrás de la tabla
        self.appointments_frame = tk.Frame(self, bg="white")

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
                "estado",
                "hora",
                "cliente",
                "pacliente",
                "especie",
                "motivo",
                "hc",
                "ultimo turno",
            ),
            displaycolumns=(
                "hora",
                "cliente",
                "pacliente",
                "especie",
                "motivo",
                "hc",
                "ultimo turno",
            ),
            show="tree headings",
        )
        self.appointments_table.tag_configure("cirugia", background="#EFE8F8")

        self.appointments_table.heading("#0", text="Estado", anchor="center")
        self.appointments_table.heading("hora", text="Hora")
        self.appointments_table.heading("cliente", text="Cliente", anchor="w")
        self.appointments_table.heading("pacliente", text="Paciente", anchor="w")
        self.appointments_table.heading("especie", text="Especie")
        self.appointments_table.heading("motivo", text="Motivo")
        self.appointments_table.heading("hc", text="HC")
        self.appointments_table.heading("ultimo turno", text="Último Turno")

        self.appointments_table.column("#0", width=70, minwidth=70, stretch=False, anchor="center")
        self.appointments_table.column("estado", width=0, stretch=False)
        self.appointments_table.column("hora", width=50, anchor="center")
        self.appointments_table.column("cliente", width=150, anchor="w")
        self.appointments_table.column("pacliente", width=100, anchor="w")
        self.appointments_table.column("especie", width=80, anchor="center")
        self.appointments_table.column("motivo", width=100, anchor="center")
        self.appointments_table.column("hc", width=70, anchor="center")
        self.appointments_table.column("ultimo turno", width=150, anchor="center")

        self.estado_images = {
            "🟢": self._crear_imagen_estado("#A8DFAE"),
            "🔴": self._crear_imagen_estado("#D16B70"),
            "🟡": self._crear_imagen_estado("#F3DA58"),
            "⚪": self._crear_imagen_estado("#D3D3D3"),
        }

        self.appointments = []

        self.appointments_table.bind("<Double-1>", self._abrir_modal_turno)



    def _crear_imagen_estado(self, color):
        imagen = tk.PhotoImage(master=self, width=24, height=20)
        imagen.put(color, to=(2, 3, 22, 17))
        for x, y in (
            (2, 3),
            (3, 3),
            (20, 3),
            (21, 3),
            (2, 4),
            (21, 4),
            (2, 15),
            (21, 15),
            (2, 16),
            (3, 16),
            (20, 16),
            (21, 16),
        ):
            imagen.transparency_set(x, y, True)
        return imagen

    def cargar_turnos_fecha(self, fecha):
        try:
            with conectar() as conexion:
                filas = obtener_turnos_por_fecha(conexion, fecha)
        except Exception as e:
            print(f"Error al cargar turnos: {e}")
            filas = []

        self.appointments = []
        for turno in filas:
            # turno viene de la BD como:
            # (id_turno, hora, cliente, paciente, especie, motivo, hc, ultimo_turno, estado_bd)
            (
                id_turno,
                hora,
                cliente,
                paciente,
                especie,
                motivo,
                hc,
                ult_turno,
                estado_bd,
            ) = turno

            # Resolvemos el estado visual y el icono
            nombre_estado, icono = resolver_estado_visual(fecha, hora, estado_bd)

            # Formateamos la fila visible para el Treeview
            fila_visible = (
                icono,
                hora,
                cliente,
                paciente,
                especie,
                motivo,
                hc,
                ult_turno,
            )
            self.appointments.append((id_turno, fila_visible))

        for item in self.appointments_table.get_children():
            self.appointments_table.delete(item)

        for id_turno, valores in self.appointments:
            motivo = str(valores[5]).casefold()
            tag = ("cirugia",) if motivo in ("cirugia", "cirugía") else ()
            # Usamos el id_turno como iid de la fila en Treeview
            self.appointments_table.insert(
                "",
                "end",
                iid=str(id_turno),
                text="",
                image=self.estado_images[valores[0]],
                values=valores,
                tags=tag,
            )

    def search_appointments(self, query, selected_filter):
        query = query.lower()

        # Índices relativos a fila_visible: (estado=0, hora=1, cliente=2, paciente=3, especie=4, motivo=5, hc=6, ultimo=7)
        filter_columns = {
            "Cliente": [2],
            "Paciente": [3],
            "Especie": [4],
            "Motivo": [5],
            "HC": [6],
        }

        if selected_filter == "Todos":
            columns_to_search = range(len(self.appointments_table["columns"]))
        else:
            columns_to_search = filter_columns.get(selected_filter, [])

        filtered_appointments = []

        for id_turno, valores in self.appointments:
            if any(
                query in str(valores[column]).lower()
                for column in columns_to_search
            ):
                filtered_appointments.append((id_turno, valores))

        for item in self.appointments_table.get_children():
            self.appointments_table.delete(item)

        for id_turno, valores in filtered_appointments:
            motivo = str(valores[5]).casefold()
            tag = ("cirugia",) if motivo in ("cirugia", "cirugía") else ()
            self.appointments_table.insert(
                "",
                "end",
                iid=str(id_turno),
                text="",
                image=self.estado_images[valores[0]],
                values=valores,
                tags=tag,
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
            command=self._open_new_appointment_type_modal,
        )

        self._build_appointments_table()
        self._select_date(self.selected_date)

    # ventana para elegir el tipo de "registrar un nuevo turno"

    def _open_new_appointment_type_modal(self):
        if (
            hasattr(self, "new_appointment_modal")
            and self.new_appointment_modal.winfo_exists()
        ):
            self.new_appointment_modal.focus_set()
            return

        self.new_appointment_modal = tk.Toplevel(self)
        self.new_appointment_modal.geometry("600x400")
        self.new_appointment_modal.resizable(False, False)
        self.new_appointment_modal.transient(self.winfo_toplevel())
        self.new_appointment_modal.grab_set()  # esto bloquea la interaccion de la app mientras el modal esta abierto
        self._centrar_ventana(self.new_appointment_modal)

        content = tk.Frame(self.new_appointment_modal, bg="white")
        content.pack(fill="both", expand=True, padx=10, pady=10)

        header = tk.Frame(content, bg="white")
        header.pack(fill="x")
#boton del modal de crear turno
        tk.Button(
            header,
            text="←",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#666666",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.new_appointment_modal.destroy,
        ).pack(side="left", padx=(24, 0), pady=(18, 0))

        tk.Button(
            content,
            text="Registrar paciente nuevo",
            font=("Arial", 16),
            bg="#D2C2ED",
            fg="#111111",
            activebackground="#C7B2E8",
            relief="raised",
            bd=2,
            cursor="hand2",
            command=self._show_new_patient_form,
        ).pack(fill="x", padx=85, pady=(16, 65), ipady=14)
#buscador del modal de crear turno
        search_area = tk.Frame(content, bg="#A8E5A8", height=105)
        search_area.pack(fill="x", padx=85)
        search_area.pack_propagate(False)

        search_box = tk.Frame(search_area, bg="white", height=42)
        search_box.place(relx=0.11, rely=0.29, relwidth=0.78, relheight=0.42)

        self.patient_search_entry = tk.Entry(
            search_box,
            font=("Arial", 12),
            bd=0,
            fg="#888888",
            relief="flat",
        )
        self.patient_search_entry.insert(
            0,
            "Buscar por paciente, cliente, HC,...",
        )

        self.patient_search_entry.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(12, 4),
        )
        self.patient_search_entry.bind(
            "<FocusIn>",
            self._clear_patient_search_placeholder,
        )
        self.patient_search_entry.bind(
            "<FocusOut>",
            self._restore_patient_search_placeholder,
        )
        search_icon = tk.Canvas(
            search_box,
            width=38,
            height=38,
            bg="white",
            highlightthickness=0,
        )
        search_icon.pack(side="right", padx=(0, 8), pady=2)
        search_icon.create_oval(
            8,
            7,
            22,
            21,
            outline="#888888",
            width=2,
        )
        search_icon.create_line(
            19,
            19,
            27,
            27,
            fill="#888888",
            width=2,
        )

    def _clear_patient_search_placeholder(self, event):
        if self.patient_search_entry.get() == "Buscar por paciente, cliente, HC,...":
            self.patient_search_entry.delete(0, tk.END)
            self.patient_search_entry.configure(fg="#333333")

    def _restore_patient_search_placeholder(self, event):
        if not self.patient_search_entry.get().strip():
            self.patient_search_entry.insert(
                0,
                "Buscar por paciente, cliente, HC,...",
            )
            self.patient_search_entry.configure(fg="#888888")

    def _show_new_patient_form(self):
        for widget in self.new_appointment_modal.winfo_children():
            widget.destroy()

        self.new_appointment_modal.title("Registrar paciente nuevo")
        self.new_appointment_modal.geometry("980x700")
        self._centrar_ventana(self.new_appointment_modal)

        form = NewAppointmentPage(
            self.new_appointment_modal,
            on_save=self._mostrar_datos_turno_nuevo,
        )
        form.pack(fill="both", expand=True)

    def _centrar_ventana(self, ventana):
        ventana_principal = self.winfo_toplevel()
        ventana_principal.update_idletasks()
        ventana.update_idletasks()

        x = ventana_principal.winfo_rootx() + (
            ventana_principal.winfo_width() - ventana.winfo_width()
        ) // 2
        y = ventana_principal.winfo_rooty() + (
            ventana_principal.winfo_height() - ventana.winfo_height()
        ) // 2
        ventana.geometry(f"+{x}+{y}")

    def _mostrar_datos_turno_nuevo(self, datos):
        self.new_appointment_modal.destroy()

        modal = tk.Toplevel(self)
        modal.geometry("700x400")
        modal.resizable(False, False)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        self._centrar_ventana(modal)

        fondo = tk.Frame(modal, bg="white")
        fondo.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(
            fondo,
            text="←",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#666666",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=modal.destroy,
        ).pack(anchor="w", padx=10, pady=(10, 0))

        tarjetas = tk.Frame(fondo, bg="white")
        tarjetas.pack(fill="x", padx=10, pady=10)

        card_cliente = tk.Frame(tarjetas, bg="#D2C2ED", padx=20, pady=20)
        card_cliente.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(
            card_cliente,
            text="Datos del Cliente y Paciente",
            font=("Arial", 13, "bold"),
            bg="#D2C2ED",
        ).pack(pady=(0, 10))
        tk.Label(
            card_cliente,
            text=f"Paciente: {datos['paciente']}",
            font=("Arial", 11),
            bg="#D2C2ED",
        ).pack(anchor="w")
        tk.Label(
            card_cliente,
            text=f"Cliente: {datos['cliente']}",
            font=("Arial", 11),
            bg="#D2C2ED",
        ).pack(anchor="w")
        tk.Label(
            card_cliente,
            text=f"Contacto: {datos['contacto']}",
            font=("Arial", 11),
            bg="#D2C2ED",
        ).pack(anchor="w")

        card_turno = tk.Frame(tarjetas, bg="#F0C8A0", padx=20, pady=20)
        card_turno.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(
            card_turno,
            text="Datos de Turno",
            font=("Arial", 13, "bold"),
            bg="#F0C8A0",
        ).pack(pady=(0, 10))
        tk.Label(
            card_turno,
            text=f"Día: {datos['fecha'].strftime('%d/%m/%Y')}",
            font=("Arial", 11),
            bg="#F0C8A0",
        ).pack(anchor="w")
        tk.Label(
            card_turno,
            text=f"Hora: {datos['hora']} hs",
            font=("Arial", 11),
            bg="#F0C8A0",
        ).pack(anchor="w")
        tk.Label(
            card_turno,
            text=f"Motivo: {datos['motivo']}",
            font=("Arial", 11),
            bg="#F0C8A0",
        ).pack(anchor="w")

        tk.Label(
            fondo,
            text="Datos del turno confirmados",
            font=("Arial", 12),
            bg="#A8E5A8",
            pady=10,
        ).pack(fill="x", padx=10, pady=(10, 5))

        tk.Button(
            fondo,
            text="Cerrar",
            font=("Arial", 11),
            bg="#D0EBF0",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=5,
            command=modal.destroy,
        ).pack(pady=10)

    def _abrir_modal_turno(self, event):
        seleccion = self.appointments_table.selection()
        if not seleccion:
            return

        iid = seleccion[0]
        valores = self.appointments_table.item(iid, "values")
        hora     = valores[1]
        cliente  = valores[2]
        paciente = valores[3]
        motivo   = valores[5]
        hc       = valores[6]
        fecha    = self.selected_date.strftime("%d/%m/%Y")

        modal = tk.Toplevel(self)
        modal.geometry("700x400")
        modal.resizable(False, False)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        fondo = tk.Frame(modal, bg="white")
        fondo.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(
            fondo,
            text="←",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#666666",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=modal.destroy,
        ).pack(anchor="w", padx=10, pady=(10, 0))

        tarjetas = tk.Frame(fondo, bg="white")
        tarjetas.pack(fill="x", padx=10, pady=10)

        card_hc = tk.Frame(tarjetas, bg="#D2C2ED", padx=20, pady=20)
        card_hc.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(card_hc, text="Datos de HC", font=("Arial", 13, "bold"), bg="#D2C2ED").pack(pady=(0, 10))
        tk.Label(card_hc, text=f"Paciente: {paciente}", font=("Arial", 11), bg="#D2C2ED").pack(anchor="w")
        tk.Label(card_hc, text=f"Cliente: {cliente}", font=("Arial", 11), bg="#D2C2ED").pack(anchor="w")
        tk.Label(card_hc, text=f"\nHC: {hc}", font=("Arial", 12, "bold"), bg="#D2C2ED").pack(anchor="w")

        card_turno = tk.Frame(tarjetas, bg="#F0C8A0", padx=20, pady=20)
        card_turno.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(card_turno, text="Datos de Turno", font=("Arial", 13, "bold"), bg="#F0C8A0").pack(pady=(0, 10))
        tk.Label(card_turno, text=f"Dia: {fecha}", font=("Arial", 11), bg="#F0C8A0").pack(anchor="w")
        tk.Label(card_turno, text=f"Hora: {hora}hs", font=("Arial", 11), bg="#F0C8A0").pack(anchor="w")
        tk.Label(card_turno, text=f"Motivo: {motivo}", font=("Arial", 11), bg="#F0C8A0").pack(anchor="w")

        tk.Label(
            fondo,
            text="Turno registrado con exito!",
            font=("Arial", 12),
            bg="#A8E5A8",
            pady=10,
        ).pack(fill="x", padx=10, pady=(10, 5))

        tk.Button(
            fondo,
            text="Cerrar",
            font=("Arial", 11),
            bg="#D0EBF0",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=5,
            command=modal.destroy,
        ).pack(pady=10)




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
