import tkinter as tk
from tkinter import messagebox, ttk
from ui.widgets.searchbar import Searchbar
from core.db import conectar
from repositories.historias import (
    obtener_consultas_paciente,
    obtener_historias,
    obtener_veterinarios_activos,
    registrar_consulta
)

class HistoriasPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", **kwargs)

        self.search_view = tk.Frame(self, bg="white")
        self.add_hc_view = tk.Frame(self, bg="white")

        self._build_historia_clinica_card()
        self._build_consulta_panels()
        self._build_search_view()
        self._build_add_hc_view()

        self.show_section("buscar_hc")

    def show_section(self, section):
        if section == "eliminar_hc":
            self._abrir_modal_eliminar_hc()
            return
        elif section == "eliminar_cliente":
            self._abrir_modal_eliminar_cliente()
            return    

        self.search_view.pack_forget()
        self.add_hc_view.pack_forget()

        if section == "buscar_hc":
            if self.historia_clinica_frame.winfo_manager():
                self._cerrar_historia_clinica()
            self.search_view.pack(fill="both", expand=True)
        elif section == "nueva_hc":
            self.add_hc_view.pack(fill="both", expand=True)
        else:
            raise ValueError(f"Sección de Historias desconocida: {section}")

    def _build_search_view(self):
        self.searchbar = Searchbar(
            self.search_view,
            controls_relwidth=1.0,
            title_text="Búsqueda de Historia Clínica",
        )
        self.searchbar.pack(pady=(0, 10), padx=40, fill="x")

        separador = tk.Frame(self.search_view, height=1, bg="#E0E0E0")
        separador.pack(fill="x", padx=20, pady=(0, 15))

        # Contenedor de la lista principal de historias clínicas.
        self.hc_table_frame = tk.Frame(
            self.search_view,
            bg="white",
            highlightbackground="#E0E0E0",
            highlightthickness=1,
        )
        self.hc_table_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=(25, 10),
        )

        columnas = (
            "cliente",
            "paciente",
            "especie",
            "hc",
            "contacto",
            "creado",
            "ultima_visita",
        )

        self.hc_table = ttk.Treeview(
            self.hc_table_frame,
            columns=columnas,
            show="headings",
            height=10,
        )

        encabezados = (
            ("cliente", "Cliente", 130, "w"),
            ("paciente", "Paciente", 100, "w"),
            ("especie", "Especie", 80, "center"),
            ("hc", "HC", 80, "center"),
            ("contacto", "Contacto", 110, "w"),
            ("creado", "Primera visita", 100, "center"),
            ("ultima_visita", "Última visita", 120, "center"),
        )

        for columna, titulo, ancho, alineacion in encabezados:
            self.hc_table.heading(
                columna,
                text=titulo,
                anchor=alineacion,
            )
            self.hc_table.column(
                columna,
                width=ancho,
                anchor=alineacion,
                stretch=True,
            )

        self._cargar_historias()

        self.hc_table.pack(fill="both", expand=True, padx=1, pady=1)
        self.hc_table.bind("<Double-1>", self._abrir_historia_clinica)

    def _cargar_historias(self):
        conexion = conectar()
        try:
            filas = obtener_historias(conexion)
        finally:
            conexion.close()

        for fila in filas:
            self.hc_table.insert("", "end", values=fila)

    def _cargar_veterinarios_activos(self):
        with conectar() as conexion:
            veterinarios = obtener_veterinarios_activos(conexion)

        self.veterinarios_por_opcion = {}
        opciones = []

        for matricula, nombre, apellido in veterinarios:
            opcion = f"{apellido}, {nombre} - {matricula}"
            opciones.append(opcion)
            self.veterinarios_por_opcion[opcion] = matricula

        self.veterinario_selector["values"] = opciones
        self.veterinario_selector.set("")

    def _abrir_historia_clinica(self, event):
        item_id = self.hc_table.identify_row(event.y)
        if not item_id:
            return "break"

        valores = self.hc_table.item(item_id, "values")
        if not valores:
            return "break"

        self.HC_client_label.config(text=f"Cliente: {valores[0]}")
        self.patient_name_label.config(text=f"Paciente: {valores[1]}")
        self.patient_species_label.config(text=f"Especie: {valores[2]}")
        self.HC_number_label.config(text=str(valores[3]))
        self.id_paciente_seleccionado = int(valores[3])

        with conectar() as conexion:
            self.consultas_historial = obtener_consultas_paciente(
                conexion,
                self.id_paciente_seleccionado,
            )

        self._cargar_veterinarios_activos()
        self._cargar_textos_historial()
        self._limpiar_consulta_actual()

        self.historial_listbox.delete(0, "end")
        for consulta in self.consultas_historial:
            fecha = consulta[1].strftime("%d-%m-%y")
            veterinario = consulta[6]
            self.historial_listbox.insert(
                "end",
                f"{fecha} {veterinario}",
            )

        self.hc_table_frame.pack_forget()
        self.historia_clinica_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=(25, 10),
        )
        return "break"

    def _cargar_textos_historial(self):
        indices = {
            "Notas": 2,
            "Observaciones": 3,
            "Tratamiento": 4,
        }

        for titulo, indice in indices.items():
            partes = []

            for consulta in self.consultas_historial:
                contenido = consulta[indice]
                if contenido and contenido.strip():
                    fecha = consulta[1].strftime("%d-%m-%Y")
                    partes.append(
                        f"Visita {fecha}:\n{contenido.strip()}"
                    )

            campo = self.consulta_historial_textos[titulo]
            campo.configure(state="normal")
            campo.delete("1.0", "end")
            if partes:
                campo.insert("1.0", "\n\n".join(partes))
            campo.configure(state="disabled")

    def _limpiar_consulta_actual(self):
        for campo in self.consulta_textos.values():
            campo.delete("1.0", "end")

    def _finalizar_consulta(self):
        opcion_veterinario = self.veterinario_var.get().strip()
        matricula = self.veterinarios_por_opcion.get(opcion_veterinario)

        if not matricula:
            messagebox.showwarning(
                "Falta seleccionar veterinario",
                "Seleccioná el veterinario que realizó la consulta.",
                parent=self,
            )
            return

        notas = self.consulta_textos["Notas"].get(
            "1.0", "end-1c"
        ).strip()
        observaciones = self.consulta_textos["Observaciones"].get(
            "1.0", "end-1c"
        ).strip()
        tratamiento = self.consulta_textos["Tratamiento"].get(
            "1.0", "end-1c"
        ).strip()

        if not any((notas, observaciones, tratamiento)):
            messagebox.showwarning(
                "Consulta vacía",
                "Escribí información en al menos uno de los campos.",
                parent=self,
            )
            return

        if len(notas) > 200:
            messagebox.showwarning(
                "Notas demasiado largas",
                "El campo Notas admite hasta 200 caracteres.",
                parent=self,
            )
            return

        try:
            with conectar() as conexion:
                registrar_consulta(
                    conexion,
                    self.id_paciente_seleccionado,
                    matricula,
                    notas,
                    observaciones,
                    tratamiento,
                )
                consultas = obtener_consultas_paciente(
                    conexion,
                    self.id_paciente_seleccionado,
                )
                historias = obtener_historias(conexion)
        except Exception as error:
            messagebox.showerror(
                "Error al guardar la consulta",
                f"No se pudo guardar la consulta en la base de datos:\n{error}",
                parent=self,
            )
            return

        self.consultas_historial = consultas
        self._cargar_textos_historial()
        self._limpiar_consulta_actual()

        self.historial_listbox.delete(0, "end")
        for consulta in self.consultas_historial:
            fecha = consulta[1].strftime("%d-%m-%y")
            veterinario = consulta[6]
            self.historial_listbox.insert(
                "end",
                f"{fecha} {veterinario}",
            )

        self.veterinario_selector.set("")

        for item_id in self.hc_table.get_children():
            self.hc_table.delete(item_id)
        for historia in historias:
            self.hc_table.insert("", "end", values=historia)

        messagebox.showinfo(
            "Consulta guardada",
            "La consulta se guardó correctamente.",
            parent=self,
        )

    def _cerrar_historia_clinica(self):
        self._limpiar_consulta_actual()
        self.historia_clinica_frame.pack_forget()
        self.hc_table_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=(25, 10),
        )

    def _build_historia_clinica_card(self):
        self.historia_clinica_frame = tk.Frame(
            self.search_view,
            bg="white",
            highlightbackground="#E0E0E0",
            highlightthickness=1

        )
#contiene el numero y cliente de HC
        self.hc_header_frame = tk.Frame(self.historia_clinica_frame, bg="white")

        self.HC_title_label = tk.Label(
            self.hc_header_frame,
            text="Historia Clínica Nº",
            font=("Inter", -24, "bold"),
            bg="white"
        )
        self.HC_number_label = tk.Label(
            self.hc_header_frame,
            text="123456",
            font=("Inter", -24),
            bg="white"
        )
        self.btn_cerrar_historia = tk.Button(
            self.hc_header_frame,
            text="x",
            font=("Arial", 20, "bold"),
            bg="white",
            relief="flat",
            cursor="hand2",
            command=self._cerrar_historia_clinica,
        )

        self.btn_finalizar_consulta = tk.Button(
            self.hc_header_frame,
            text="✓ Finalizar consulta",
            font=("Arial", 10, "bold"),
            bg="#8FD694",
            fg="#1F1F1F",
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._finalizar_consulta,
        )

        self.HC_client_label = tk.Label(
            self.hc_header_frame,
            text="Cliente: Juan Pérez",
            font=("Inter", -16),
            bg="white"
        )

        self.client_contact_frame = tk.Frame(
            self.historia_clinica_frame,
            bg="white",
        )

        self.client_phone_label = tk.Label(
            self.client_contact_frame,
            text="Teléfono: 3518292929",
            font=("Arial", 9),
            bg="white",
        )

        self.client_address_label = tk.Label(
            self.client_contact_frame,
            text="Domicilio: Sobremonte 2011",
            font=("Arial", 9),
            bg="white",
        )

        self.client_dni_label = tk.Label(
            self.client_contact_frame,
            text="DNI: 98555888",
            font=("Arial", 9),
            bg="white",
        )

#contiene datos principales del paciente
        self.hc_patient_info_frame = tk.Frame(self.historia_clinica_frame, bg="white")

        self.patient_name_label = tk.Label(
            self.hc_patient_info_frame,
            text="Paciente: Fido",
            font=("Inter", -16),
            bg="white"
        )
        self.patient_species_label = tk.Label(
            self.hc_patient_info_frame,
            text="Especie: Canino",
            font=("Inter", -16),
            bg="white"
        )
        self.patient_age_label = tk.Label(
            self.hc_patient_info_frame,
            text="Edad: 5 años",
            font=("Inter", -16),
            bg="white"
        )
        self.patient_sex_label = tk.Label(
            self.hc_patient_info_frame,
            text="Sexo: Macho",
            font=("Inter", -16),
            bg="white"
        )   
        self.patient_neutered_label = tk.Label(
            self.hc_patient_info_frame,
            text="Castrado: Sí",
            font=("Inter", -16),
            bg="white"
        )
        self.patient_weight_label = tk.Label(
            self.hc_patient_info_frame,
            text="Peso: 20 kg",
            font=("Inter", -16),
            bg="white"
        )

        self.hc_header_frame.pack(fill="x", padx=12, pady=(10, 6))

        self.client_contact_frame.pack(fill="x", padx=12, pady=(0, 6))
        self.client_phone_label.pack(side="left", padx=6)
        self.client_address_label.pack(side="left", padx=6)
        self.client_dni_label.pack(side="left", padx=6)

        self.btn_finalizar_consulta.pack(side="right")
        self.btn_cerrar_historia.pack(side="left", padx=(0, 8))
        self.HC_title_label.pack(side="left")
        self.HC_number_label.pack(side="left", padx=(6, 20))
        self.HC_client_label.pack(side="left")

        self.hc_patient_info_frame.pack(fill="x", padx=12, pady=6)
        self.patient_name_label.pack(side="left", padx=6)
        self.patient_species_label.pack(side="left", padx=6)
        self.patient_age_label.pack(side="left", padx=6)
        self.patient_sex_label.pack(side="left", padx=6)
        self.patient_neutered_label.pack(side="left", padx=6)
        self.patient_weight_label.pack(side="left", padx=6)

        self.veterinario_selector_frame = tk.Frame(
            self.historia_clinica_frame,
            bg="white",
        )

        tk.Label(
            self.veterinario_selector_frame,
            text="Veterinario de la consulta:",
            bg="white",
        ).pack(side="left", padx=(6, 4))

        self.veterinario_var = tk.StringVar()
        self.veterinario_selector = ttk.Combobox(
            self.veterinario_selector_frame,
            textvariable=self.veterinario_var,
            state="readonly",
            width=35,
        )
        self.veterinario_selector.pack(side="left")
        self.veterinario_selector_frame.pack(
            fill="x",
            padx=12,
            pady=(0, 6),
        )

    def _build_consulta_panels(self):
        self.consulta_panels_frame = tk.Frame(
            self.historia_clinica_frame,
            bg="white",
        )
        self.consulta_panels_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(8, 12),
        )

        self.consulta_panels_frame.grid_columnconfigure(0, weight=1)
        self.consulta_panels_frame.grid_columnconfigure(1, weight=1)
        self.consulta_panels_frame.grid_rowconfigure(0, weight=1)
        self.consulta_panels_frame.grid_rowconfigure(1, weight=1)

        paneles= (
            ("Tratamiento", 0, 0),
            ("Observaciones", 0, 1),
            ("Notas", 1, 0),
        )

        self.consulta_historial_textos = {}
        self.consulta_textos = {}

        for titulo, fila, columna in paneles:
            panel = tk.Frame(
                self.consulta_panels_frame,
                bg="#F0F0F0",
                highlightbackground="#D9D9D9",
                highlightthickness=3
            )
            panel.grid(
                row=fila,
                column=columna,
                sticky="nsew",
                padx=6,
                pady=6,
            )

            tk.Label(
                panel,
                text=titulo,
                font=("Arial", 10, "bold"),
                bg="#F0F0F0",
            ).pack(fill="x", pady=(6, 4))

            tk.Label(
                panel,
                text="Consultas anteriores (solo lectura)",
                font=("Arial", 9),
                bg="#F0F0F0",
            ).pack(fill="x", padx=8)

            historial = tk.Text(
                panel,
                height=3,
                wrap="word",
                font=("Arial", 9),
                relief="flat",
                state="disabled",
            )
            historial.pack(fill="both", expand=True, padx=8, pady=(0, 4))
            self.consulta_historial_textos[titulo] = historial

            tk.Label(
                panel,
                text="Consulta actual",
                font=("Arial", 9),
                bg="#F0F0F0",
            ).pack(fill="x", padx=8)

            campo = tk.Text(
                panel,
                height=3,
                wrap="word",
                font=("Arial", 9),
                relief="flat",
            )
            campo.pack(fill="both", expand=True, padx=8, pady=(0, 8))
            self.consulta_textos[titulo] = campo

        historial_panel = tk.Frame(
            self.consulta_panels_frame,
            bg="#F0F0F0",
            highlightbackground="#D9D9D9",
            highlightthickness=3,
        )
        historial_panel.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=6,
        )

        tk.Label(
            historial_panel,
            text="Historial de cambios",
            font=("Arial", 10, "bold"),
            bg="#F0F0F0",
        ).pack(fill="x", pady=(6, 4))

        self.historial_listbox = tk.Listbox(
            historial_panel,
            height=5,
            font=("Arial", 9),
            relief="flat",
        )
        self.historial_listbox.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8),
        )

    def _build_add_hc_view(self):
        header_frame = tk.Frame(self.add_hc_view, bg="white")
        header_frame.pack(fill="x", padx=40, pady=(20, 10))

        tk.Label(header_frame, text="Nueva Hist. Clínica - Nº ", font=("Arial", 16, "bold"), bg="white").pack(side="left")
        tk.Label(header_frame, text="65223", font=("Arial", 16, "bold"), bg="#D1C4E9", padx=10).pack(side="left")

        self.btn_guardar = tk.Button(header_frame, text="💾 Guardar", font=("Arial", 12), relief="flat", bg="#A8D5BA", cursor="hand2")
        self.btn_guardar.pack(side="right")

        bg_green = "#C8E6C9"
        form_frame = tk.Frame(self.add_hc_view, bg=bg_green, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True, padx=40, pady=10)

        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_dni = tk.StringVar()

        tk.Label(form_frame, text="Datos del Cliente", font=("Arial", 10, "bold"), bg=bg_green).grid(row=0, column=0, sticky="w", pady=(0, 10))

        tk.Label(form_frame, text="Nombre", bg=bg_green).grid(row=1, column=0, sticky="e", padx=5)
        tk.Entry(form_frame, textvariable=self.var_nombre).grid(row=1, column=1, sticky="ew", padx=5)

        tk.Label(form_frame, text="Apellido", bg=bg_green).grid(row=1, column=2, sticky="e", padx=5)
        tk.Entry(form_frame, textvariable=self.var_apellido).grid(row=1, column=3, sticky="ew", padx=5)

        tk.Label(form_frame, text="DNI", bg=bg_green).grid(row=1, column=4, sticky="e", padx=5)
        tk.Entry(form_frame, textvariable=self.var_dni).grid(row=1, column=5, sticky="ew", padx=5)

        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
        form_frame.grid_columnconfigure(5, weight=1)

        tk.Label(form_frame, text="Tratamiento", bg=bg_green, font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=6, pady=(20, 5))
        self.caja_tratamiento = tk.Text(form_frame, height=8)
        self.caja_tratamiento.grid(row=3, column=0, columnspan=6, sticky="ew", padx=5)

    def _abrir_modal_eliminar_hc(self):
        # 1. Ventana emergente limpia sin barra de Windows
        dialog = tk.Toplevel(self)
        dialog.overrideredirect(True)  # Quita la barra superior de Windows
        dialog.configure(
            bg="white",
            highlightbackground="#333333",
            highlightthickness=1       # Borde fino oscuro exacto a la foto
        )

        # 2. Título ATENCION!!
        tk.Label(
            dialog,
            text="ATENCION!!",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#1F1F1F",
        ).pack(padx=50, pady=(32, 16))

        # 3. Mensaje de advertencia
        tk.Label(
            dialog,
            text="Esta accion es IRREVERSIBLE y BORRA la\n\nHISTORIA CLINICA del paciente actual.",
            font=("Arial", 10),
            justify="center",
            bg="white",
            fg="#1F1F1F",
        ).pack(padx=50, pady=(0, 30))

        # 4. Contenedor de botones
        buttons_frame = tk.Frame(dialog, bg="white")
        buttons_frame.pack(fill="x", padx=50, pady=(0, 32))

        # Botón CANCELAR (Gris más grande)
        btn_cancelar = tk.Button(
            buttons_frame,
            text="CANCELAR",
            font=("Arial", 11, "bold"),
            bg="#D1D5DB",
            fg="#1F1F1F",
            relief="flat",
            bd=0,
            padx=28,
            pady=12,
            cursor="hand2",
            command=dialog.destroy,
        )
        btn_cancelar.pack(side="left", expand=True, padx=(0, 12))

        # Botón CONTINUAR (Naranja más grande)
        btn_continuar = tk.Button(
            buttons_frame,
            text="CONTINUAR",
            font=("Arial", 11, "bold"),
            bg="#F7A84B",
            fg="#1F1F1F",
            relief="flat",
            bd=0,
            padx=28,
            pady=12,
            cursor="hand2",
            command=lambda: self._confirmar_eliminar_hc(dialog),
        )
        btn_continuar.pack(side="right", expand=True, padx=(12, 0))

        # 5. Centrar sobre la ventana principal
        dialog.update_idletasks()
        parent = self.winfo_toplevel()
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()

    def _confirmar_eliminar_hc(self, dialog):
        dialog.destroy()
        # Oculta la tarjeta de la historia clínica en pantalla simulando la baja
        self.historia_clinica_frame.pack_forget()
        print("Historia Clínica dada de baja exitosamente.")
    
    def _abrir_modal_eliminar_cliente(self):
        # 1. Ventana emergente limpia sin barra de Windows
        dialog = tk.Toplevel(self)
        dialog.overrideredirect(True)
        dialog.configure(
            bg="white",
            highlightbackground="#333333",
            highlightthickness=1
        )

        # 2. Título ATENCION!!
        tk.Label(
            dialog,
            text="ATENCION!!",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#1F1F1F",
        ).pack(padx=50, pady=(32, 16))

        # 3. Mensaje de advertencia de la nueva captura
        tk.Label(
            dialog,
            text=(
                "Esta accion es IRREVERSIBLE y borra TODAS\n\n"
                "las historias clinicas de TODOS los PACIENTES\n"
                "de este cliente."
            ),
            font=("Arial", 10),
            justify="center",
            bg="white",
            fg="#1F1F1F",
        ).pack(padx=50, pady=(0, 30))

        # 4. Contenedor de botones
        buttons_frame = tk.Frame(dialog, bg="white")
        buttons_frame.pack(fill="x", padx=50, pady=(0, 32))

        # Botón CANCELAR (Gris)
        btn_cancelar = tk.Button(
            buttons_frame,
            text="CANCELAR",
            font=("Arial", 11, "bold"),
            bg="#D1D5DB",
            fg="#1F1F1F",
            relief="flat",
            bd=0,
            padx=28,
            pady=12,
            cursor="hand2",
            command=dialog.destroy,
        )
        btn_cancelar.pack(side="left", expand=True, padx=(0, 12))

        # Botón CONTINUAR (Rojo en esta modal, tal cual la foto)
        btn_continuar = tk.Button(
            buttons_frame,
            text="CONTINUAR",
            font=("Arial", 11, "bold"),
            bg="#FA5252",
            fg="#1F1F1F",
            relief="flat",
            bd=0,
            padx=28,
            pady=12,
            cursor="hand2",
            command=lambda: self._confirmar_eliminar_cliente(dialog),
        )
        btn_continuar.pack(side="right", expand=True, padx=(12, 0))

        # 5. Centrar sobre la ventana principal
        dialog.update_idletasks()
        parent = self.winfo_toplevel()
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()

    def _confirmar_eliminar_cliente(self, dialog):
        dialog.destroy()
        # Oculta la información en pantalla simulando la baja del cliente
        self.historia_clinica_frame.pack_forget()
        print("Cliente y todas sus historias clínicas dados de baja exitosamente.")
