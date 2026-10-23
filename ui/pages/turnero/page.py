from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import tkinter as tk
from tkinter import messagebox, ttk

from core.db import conectar
from ui.pages.turnero.new_appointment import NewAppointmentPage
from repositories.turno import (
    obtener_turnos_por_fecha,
    resolver_estado_visual,
    cancelar_turno,
    buscar_turnos,
    encontrar_fecha_de_turno,
    buscar_pacientes_para_turno,
    registrar_turno_paciente_existente,
    ClienteInhabilitadoError,
)

from ui.widgets.searchbar import Searchbar


class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        # Aseguramos el fondo blanco general
        super().__init__(master, bg="white", **kwargs)

        self.on_date_changed = None
        self._build_widgets()
        self._build_layout()

        self._iniciar_auto_refresco() # esto es opcional, pero lo quise agregar para que la tabla se refresque automaticamente cada cierto tiempo, por si se hacen cambios. pruebenlo

    def _iniciar_auto_refresco(self):
        self.cargar_turnos_fecha(self.selected_date)
        # Se programa para volver a ejecutarse en 2 minutos, por las dudas en tkinter el .after mide en milisegundos hagan las matematicas  
        self.after(120000, self._iniciar_auto_refresco)

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
            command=lambda: self.select_date(self.selected_date),
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
            command=lambda: self.select_date(self.selected_date + timedelta(days=1)),
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
            command=lambda: self.select_date(self.selected_date + timedelta(days=2)),
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
        self.select_date(self.selected_date + timedelta(days=days))

    def select_date(self, fecha):
        self.selected_date = fecha
        self.today_button.configure(text=str(fecha.day), bg="#E6D0F5")
        self.tomorrow_button.configure(
            text=str((fecha + timedelta(days=1)).day), bg="#F0F0F0"
        )
        self.next_day_button.configure(
            text=str((fecha + timedelta(days=2)).day), bg="#F0F0F0"
        )
        if self.on_date_changed is not None:
            self.on_date_changed(fecha)
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
                "accion",
            ),
            displaycolumns=(
                "hora",
                "cliente",
                "pacliente",
                "especie",
                "motivo",
                "hc",
                "ultimo turno",
                "accion",
            ),
            show="tree headings",
        )
        self.appointments_table.tag_configure(
            "cancelado",
            foreground="black",
            font=("Arial", 10, "overstrike"),
        )
        self.appointments_table.tag_configure("cirugia", background="#EFE8F8")
        self.appointments_table.tag_configure(
            "cliente_inactivo",
            foreground="#888888",
        )

        self.appointments_table.heading("#0", text="Estado", anchor="center")
        self.appointments_table.heading("hora", text="Hora")
        self.appointments_table.heading("cliente", text="Cliente", anchor="w")
        self.appointments_table.heading("pacliente", text="Paciente", anchor="w")
        self.appointments_table.heading("especie", text="Especie")
        self.appointments_table.heading("motivo", text="Motivo")
        self.appointments_table.heading("hc", text="HC")
        self.appointments_table.heading("ultimo turno", text="Último Turno")
        self.appointments_table.heading("accion", text="")

        self.appointments_table.column("#0", width=70, minwidth=70, stretch=False, anchor="center")
        self.appointments_table.column("estado", width=0, stretch=False)
        self.appointments_table.column("hora", width=50, anchor="center")
        self.appointments_table.column("cliente", width=150, anchor="w")
        self.appointments_table.column("pacliente", width=100, anchor="w")
        self.appointments_table.column("especie", width=80, anchor="center")
        self.appointments_table.column("motivo", width=100, anchor="center")
        self.appointments_table.column("hc", width=70, anchor="center")
        self.appointments_table.column("ultimo turno", width=150, anchor="center")
        self.appointments_table.column("accion", width=45, minwidth=45, stretch=False, anchor="center")

        self.estado_images = {
            "🟢": self._crear_imagen_estado("#A8DFAE"),
            "🔴": self._crear_imagen_estado("#D16B70"),
            "🟡": self._crear_imagen_estado("#F3DA58"),
            "⚪": self._crear_imagen_estado("#D3D3D3"),
            "⚫": self._crear_imagen_estado("#000000"),
        }

        self.appointments = []
        self.turnos_cancelables = set()

        self.appointments_table.bind("<Double-1>", self._abrir_modal_turno)
        self.appointments_table.bind("<Button-1>", self._on_table_click)



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

        self._poblar_tabla_turnos(filas)

    def _poblar_tabla_turnos(self, filas):
        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        self.appointments = []
        self.turnos_cancelables.clear()

        for turno in filas:
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
                estado_cliente,
            ) = turno

            estado_normalizado = (estado_bd or "").strip().upper()
            nombre_estado, icono = resolver_estado_visual(self.selected_date, hora, estado_bd)

            es_cancelable = False
            if estado_normalizado == "PENDIENTE":
                try:
                    hora_dt = datetime.strptime(hora, "%H:%M").time()
                    dt_turno = datetime.combine(self.selected_date, hora_dt).replace(
                        tzinfo=now.tzinfo
                    )
                    es_cancelable = dt_turno > now
                except ValueError:
                    pass

            accion_icono = "❌" if es_cancelable else ""
            if es_cancelable:
                self.turnos_cancelables.add(id_turno)

            fila_visible = (
                icono,
                hora,
                cliente,
                paciente,
                especie,
                motivo,
                hc,
                ult_turno,
                accion_icono,
            )
            es_cancelado = estado_normalizado == "CANCELADO"
            self.appointments.append(
                (id_turno, fila_visible, es_cancelado, estado_cliente)
            )

        for item in self.appointments_table.get_children():
            self.appointments_table.delete(item)

        for id_turno, valores, es_cancelado, estado_cliente in self.appointments:
            motivo = str(valores[5]).casefold()
            tags = []
            if motivo in ("cirugia", "cirugía"):
                tags.append("cirugia")
            if es_cancelado:
                tags.append("cancelado")
            if (estado_cliente or "").strip().upper() == "INACTIVO":
                tags.append("cliente_inactivo")

            self.appointments_table.insert(
                "",
                "end",
                iid=str(id_turno),
                text="",
                image=self.estado_images[valores[0]],
                values=valores,
                tags=tuple(tags),
            )

    def _on_table_click(self, event):
        region = self.appointments_table.identify_region(event.x, event.y)
        if region != "cell":
            return

        columna = self.appointments_table.identify_column(event.x)
        if self.appointments_table.column(columna, "id") != "accion":
            return

        item_id = self.appointments_table.identify_row(event.y)
        if not item_id:
            return

        id_turno = int(item_id)
        if id_turno in self.turnos_cancelables:
            self._confirmar_cancelacion_turno(id_turno)

    def _confirmar_cancelacion_turno(self, id_turno):
        valores = self.appointments_table.item(str(id_turno), "values")
        hora = valores[1]
        paciente = valores[3]

        respuesta = messagebox.askyesno(
            "Cancelar Turno",
            f"¿Desea cancelar el turno de las {hora} hs para {paciente}?\n\n"
            "El horario volverá a quedar disponible para asignación.",
            parent=self,
        )
        if not respuesta:
            return

        try:
            with conectar() as conexion:
                exito = cancelar_turno(conexion, id_turno)
            if exito:
                messagebox.showinfo(
                    "Turno Cancelado",
                    "El turno fue cancelado y el horario quedó liberado.",
                    parent=self,
                )
            else:
                messagebox.showwarning(
                    "No se pudo cancelar",
                    "El turno ya no se encuentra pendiente o su horario ya ha pasado.",
                    parent=self,
                )
            self.cargar_turnos_fecha(self.selected_date)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al cancelar turno en la base de datos:\n{e}",
                parent=self,
            )

    def search_appointments(self, query, selected_filter):
        query_limpia = (query or "").strip()

        # Si borran la búsqueda y está en Todos, recargamos la fecha normal
        if not query_limpia and selected_filter == "Todos":
            self.cargar_turnos_fecha(self.selected_date)
            return

        filas = []
        try:
            with conectar() as conexion:
                filas = buscar_turnos(
                    conexion=conexion,
                    fecha_consulta=self.selected_date,
                    termino=query_limpia,
                    filtro=selected_filter,
                )

                if not filas and query_limpia:
                    fecha_destino = encontrar_fecha_de_turno(
                        conexion=conexion,
                        termino=query_limpia,
                        filtro=selected_filter,
                    )
                    if fecha_destino and fecha_destino != self.selected_date:
                        self.select_date(fecha_destino)
                        # Buscamos nuevamente en esa fecha de destino
                        filas = buscar_turnos(
                            conexion=conexion,
                            fecha_consulta=fecha_destino,
                            termino=query_limpia,
                            filtro=selected_filter,
                        )
        except Exception as e:
            print(f"Error en la búsqueda de turnos: {e}")
            filas = []

        self._poblar_tabla_turnos(filas)

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
        self.select_date(self.selected_date)

    # ventana para elegir el tipo de "registrar un nuevo turno"

    def _open_new_appointment_type_modal(self):
        if (
            hasattr(self, "new_appointment_modal")
            and self.new_appointment_modal.winfo_exists()
        ):
            self.new_appointment_modal.focus_set()
            return

        self.new_appointment_modal = tk.Toplevel(self)
        self.new_appointment_modal.geometry("640x520")
        self.new_appointment_modal.resizable(False, False)
        self.new_appointment_modal.transient(self.winfo_toplevel())
        self.new_appointment_modal.grab_set()
        self._centrar_ventana(self.new_appointment_modal)

        content = tk.Frame(self.new_appointment_modal, bg="white")
        content.pack(fill="both", expand=True, padx=16, pady=16)

        header = tk.Frame(content, bg="white")
        header.pack(fill="x")

        tk.Button(
            header,
            text="←",
            font=("Arial", 22, "bold"),
            bg="white",
            fg="#666666",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.new_appointment_modal.destroy,
        ).pack(side="left", padx=(10, 0), pady=(4, 0))

        # Botón para paciente nuevo
        tk.Button(
            content,
            text="Registrar paciente nuevo",
            font=("Arial", 14, "bold"),
            bg="#D2C2ED",
            fg="#111111",
            activebackground="#C7B2E8",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._show_new_patient_form,
        ).pack(fill="x", padx=40, pady=(12, 20), ipady=10)

        # Contenedor verde del buscador de HC según Figma
        search_area = tk.Frame(content, bg="#A8E5A8", padx=16, pady=16)
        search_area.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        search_box = tk.Frame(search_area, bg="white", height=38)
        search_box.pack(fill="x", pady=(0, 10))
        search_box.pack_propagate(False)

        self.patient_search_entry = tk.Entry(
            search_box,
            font=("Arial", 11),
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
        # Búsqueda dinámica al presionar Enter o mientras se escribe
        self.patient_search_entry.bind(
            "<KeyRelease>",
            lambda event: self._buscar_pacientes_existentes(),
        )
        self.patient_search_entry.bind(
            "<Return>",
            lambda event: self._buscar_pacientes_existentes(),
        )

        search_btn = tk.Button(
            search_box,
            text="🔍",
            font=("Arial", 12),
            bg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._buscar_pacientes_existentes,
        )
        search_btn.pack(side="right", padx=(0, 6))

        # Tabla de resultados desplegable (Figma: Cliente, Paciente, Especie, HC)
        table_frame = tk.Frame(search_area, bg="white")
        table_frame.pack(fill="both", expand=True)

        columnas = ("cliente", "paciente", "especie", "hc")
        self.patient_results_table = ttk.Treeview(
            table_frame,
            columns=columnas,
            show="headings",
            height=6,
        )

        self.patient_results_table.heading("cliente", text="Cliente", anchor="w")
        self.patient_results_table.heading("paciente", text="Paciente", anchor="w")
        self.patient_results_table.heading("especie", text="Especie", anchor="center")
        self.patient_results_table.heading("hc", text="HC", anchor="center")

        self.patient_results_table.column("cliente", width=160, anchor="w")
        self.patient_results_table.column("paciente", width=120, anchor="w")
        self.patient_results_table.column("especie", width=80, anchor="center")
        self.patient_results_table.column("hc", width=60, anchor="center")

        self.patient_results_table.pack(fill="both", expand=True)
        self.patient_results_table.bind(
            "<Double-1>",
            self._seleccionar_paciente_existente,
        )
        self.pacientes_encontrados_cache = {}

    def _buscar_pacientes_existentes(self):
        termino = self.patient_search_entry.get().strip()
        if termino == "Buscar por paciente, cliente, HC,...":
            termino = ""

        for item in self.patient_results_table.get_children():
            self.patient_results_table.delete(item)
        self.pacientes_encontrados_cache.clear()

        if not termino:
            return

        try:
            with conectar() as conexion:
                pacientes = buscar_pacientes_para_turno(conexion, termino)
        except Exception as error:
            messagebox.showerror(
                "Error al buscar pacientes",
                f"No se pudieron buscar pacientes existentes:\n{error}",
                parent=self.new_appointment_modal,
            )
            return

        for paciente_data in pacientes:
            (
                id_paciente,
                cliente,
                paciente,
                especie,
                contacto,
                dni,
                estado_cliente,
            ) = paciente_data
            hc_str = str(id_paciente)
            self.pacientes_encontrados_cache[hc_str] = {
                "id_paciente": id_paciente,
                "cliente": cliente,
                "paciente": paciente,
                "especie": especie,
                "contacto": contacto or "No informado",
                "dni": dni,
                "estado_cliente": estado_cliente,
            }
            self.patient_results_table.insert(
                "",
                "end",
                iid=hc_str,
                values=(cliente, paciente, especie, hc_str),
            )

    def _seleccionar_paciente_existente(self, event):
        seleccion = self.patient_results_table.selection()
        if not seleccion:
            return

        hc_str = seleccion[0]
        datos_paciente = self.pacientes_encontrados_cache.get(hc_str)
        if not datos_paciente:
            return

        if datos_paciente["estado_cliente"] == "INACTIVO":
            messagebox.showwarning(
                "Cliente inhabilitado",
                "No se puede crear el turno porque el cliente está inhabilitado.",
                parent=self.new_appointment_modal,
            )
            return

        self._mostrar_selector_turno_paciente_existente(datos_paciente)

    def _mostrar_selector_turno_paciente_existente(self, datos_paciente):
        for widget in self.new_appointment_modal.winfo_children():
            widget.destroy()

        self.new_appointment_modal.title(f"Turno: {datos_paciente['paciente']}")
        self.new_appointment_modal.geometry("780x640")
        self._centrar_ventana(self.new_appointment_modal)

        # Cabecera con datos del paciente
        header = tk.Frame(self.new_appointment_modal, bg="#D2C2ED", height=48)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(
            header,
            text="←",
            font=("Arial", 20, "bold"),
            bg="#D2C2ED",
            fg="#666666",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._volver_al_buscador_pacientes,
        ).pack(side="left", padx=16)

        tk.Label(
            header,
            text=f"Turno: {datos_paciente['paciente']} (HC: {datos_paciente['id_paciente']}) - Cliente: {datos_paciente['cliente']}",
            font=("Arial", 13, "bold"),
            bg="#D2C2ED",
            fg="#111111",
        ).pack(side="left", padx=10)

        cuerpo = tk.Frame(self.new_appointment_modal, bg="white", padx=24, pady=16)
        cuerpo.pack(fill="both", expand=True)

        # Motivo y Calendario
        top_row = tk.Frame(cuerpo, bg="white")
        top_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            top_row,
            text="Motivo:",
            font=("Arial", 11, "bold"),
            bg="white",
        ).pack(side="left", padx=(0, 6))
        motivo_var = tk.StringVar(value="Clinica")
        motivo_cb = ttk.Combobox(
            top_row,
            textvariable=motivo_var,
            values=("Clinica", "Vacunacion", "Cirugia", "Otros"),
            state="readonly",
            width=16,
        )
        motivo_cb.pack(side="left", padx=(0, 30))

        fecha_sel = [datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()]
        horario_sel = [None]

        # Selector de Horarios
        tk.Label(
            cuerpo,
            text="Horarios disponibles:",
            font=("Arial", 11, "bold"),
            bg="white",
        ).pack(anchor="w", pady=(8, 4))

        from ui.pages.turnero.horarios_selector import HorariosSelector

        selector_horarios = HorariosSelector(
            cuerpo,
            fecha_base=fecha_sel[0],
            horarios_ocupados=set(),
        )
        selector_horarios.pack(fill="both", expand=True, pady=(0, 10))

        def on_horario(dia, hora):
            horario_sel[0] = (dia, hora)
            btn_agendar.config(state="normal")

        selector_horarios.on_horario_seleccionado = on_horario

        def confirmar_y_guardar():
            if not horario_sel[0]:
                return

            dia, hora = horario_sel[0]
            datos_turno = {
                "id_paciente": datos_paciente["id_paciente"],
                "paciente": datos_paciente["paciente"],
                "cliente": datos_paciente["cliente"],
                "contacto": datos_paciente["contacto"],
                "hc": datos_paciente["id_paciente"],
                "fecha": dia,
                "hora": hora,
                "motivo": motivo_var.get(),
            }

            try:
                with conectar() as conexion:
                    id_turno = registrar_turno_paciente_existente(
                        conexion,
                        datos_turno,
                    )
                    datos_turno["id_turno"] = id_turno
            except ClienteInhabilitadoError as error:
                messagebox.showwarning(
                    "Cliente inhabilitado",
                    str(error),
                    parent=self.new_appointment_modal,
                )
                return
            except Exception as error:
                messagebox.showerror(
                    "Error al registrar turno",
                    f"No se pudo guardar el turno:\n{error}",
                    parent=self.new_appointment_modal,
                )
                return

            self._mostrar_datos_turno_nuevo(datos_turno)

        btn_agendar = tk.Button(
            cuerpo,
            text="Agendar Turno",
            bg="#61D161",
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            state="disabled",
            padx=20,
            pady=8,
            command=confirmar_y_guardar,
        )
        btn_agendar.pack(pady=10)

    def _volver_al_buscador_pacientes(self):
        self.new_appointment_modal.destroy()
        self._open_new_appointment_type_modal()

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

        def cerrar_y_recargar():
            modal.destroy()
            self.select_date(self.selected_date)

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
        tk.Label(
            card_cliente,
            text=f"Nº Historia Clínica (HC): {datos.get('hc', '-')}",
            font=("Arial", 11, "bold"),
            bg="#D2C2ED",
            fg="#6200EE",
        ).pack(anchor="w", pady=(6, 0))

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
            command=cerrar_y_recargar,
        ).pack(pady=10)

    def _abrir_modal_turno(self, event):
        column = self.appointments_table.identify_column(event.x)
        if self.appointments_table.column(column, "id") == "accion":
            return

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
        estado_cliente = next(
            (
                estado
                for id_turno, _, estado in self.appointments
                if str(id_turno) == iid
            ),
            None,
        )
        color_hc = (
            "#888888"
            if (estado_cliente or "").upper() == "INACTIVO"
            else "#111111"
        )

        modal = tk.Toplevel(self)
        modal.geometry("700x400")
        modal.resizable(False, False)
        modal.transient(self.winfo_toplevel())
        self._centrar_ventana(modal)
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
        tk.Label(
            card_hc,
            text="Datos de HC",
            font=("Arial", 13, "bold"),
            bg="#D2C2ED",
            fg=color_hc,
        ).pack(pady=(0, 10))
        tk.Label(
            card_hc,
            text=f"Paciente: {paciente}",
            font=("Arial", 11),
            bg="#D2C2ED",
            fg=color_hc,
        ).pack(anchor="w")
        tk.Label(
            card_hc,
            text=f"Cliente: {cliente}",
            font=("Arial", 11),
            bg="#D2C2ED",
            fg=color_hc,
        ).pack(anchor="w")
        tk.Label(
            card_hc,
            text=f"\nHC: {hc}",
            font=("Arial", 12, "bold"),
            bg="#D2C2ED",
            fg=color_hc,
        ).pack(anchor="w")

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
