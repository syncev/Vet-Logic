import tkinter as tk
import psycopg
from datetime import date
from tkinter import messagebox, ttk

import psycopg

from ui.widgets.searchbar import Searchbar
from core.db import conectar
from repositories.historias import (
    obtener_consultas_paciente,
    obtener_detalle_paciente,
    obtener_historias,
    obtener_veterinarios_activos,
    registrar_consulta,
    obtener_turnos_pendientes_hoy,
    inhabilitar_cliente_de_paciente,
    eliminar_historia_clinica,
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
            on_search=self._buscar_historias,
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
        self.hc_table.tag_configure(
            "cliente_inactivo",
            foreground="#888888",
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
        texto = self.searchbar.get_search_text()
        filtro = self.searchbar.filter_options.get()
        conexion = conectar()
        try:
            filas = obtener_historias(conexion, texto, filtro)
        finally:
            conexion.close()

        self._actualizar_tabla_historias(filas)

    def _buscar_historias(self, texto, filtro):
        try:
            with conectar() as conexion:
                filas = obtener_historias(conexion, texto, filtro)
        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Error al buscar historias clínicas",
                f"No se pudieron buscar las historias clínicas:\n{error}",
                parent=self,
            )
            return

        self._actualizar_tabla_historias(filas)

    def _actualizar_tabla_historias(self, filas):
        for item_id in self.hc_table.get_children():
            self.hc_table.delete(item_id)
        for fila in filas:
            valores = list(fila[:7])
            for indice in (5, 6):
                if valores[indice] is None:
                    valores[indice] = "Sin consultas"
            tags = (
                ("cliente_inactivo",)
                if (fila[7] or "").upper() == "INACTIVO"
                else ()
            )
            self.hc_table.insert(
                "",
                "end",
                values=valores,
                tags=tags,
            )

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

    def _cargar_turnos_pendientes(self, turnos):
        opcion_sin_turno= "Sin turno (urgencia u otra consulta)"
        opciones = [opcion_sin_turno]
        self.turnos_por_opcion = {opcion_sin_turno: None}

        for id_turno, hora_inicio, motivo in turnos:
            hora = hora_inicio.strftime("%H:%M")
            opcion = f"{hora} - {motivo} (turno{id_turno})"
            opciones.append(opcion)
            self.turnos_por_opcion[opcion] = id_turno

        self.turno_selector["values"] = opciones
        self.turno_selector.set("")

    def _abrir_historia_clinica(self, event):
        item_id = self.hc_table.identify_row(event.y)
        if not item_id:
            return "break"

        valores = self.hc_table.item(item_id, "values")
        if not valores:
            return "break"

        self.HC_number_label.config(text=str(valores[3]))
        self.id_paciente_seleccionado = int(valores[3])

        with conectar() as conexion:
            self.consultas_historial = obtener_consultas_paciente(
                conexion,
                self.id_paciente_seleccionado,
            )
            detalle = obtener_detalle_paciente(
                conexion,
                self.id_paciente_seleccionado,
            )
            turnos_pendientes = obtener_turnos_pendientes_hoy(
                conexion,
                self.id_paciente_seleccionado,
            )

        if detalle is None:
            messagebox.showerror(
                "Paciente no encontrado",
                "No se encontraron los datos del paciente seleccionado.",
                parent=self,
            )
            return "break"

        self._cargar_turnos_pendientes(turnos_pendientes)

        (
            nombre_cliente,
            apellido_cliente,
            telefono,
            domicilio,
            dni,
            nombre_paciente,
            especie,
            fecha_nacimiento,
            sexo,
            castrado,
            peso,
        ) = detalle

        if fecha_nacimiento is None:
            edad_texto = "No informada"
        else:
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year
            if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                edad -= 1
            edad_texto = f"{edad} año" if edad == 1 else f"{edad} años"

        if castrado is None:
            castrado_texto = "No informado"
        elif castrado:
            castrado_texto = "Sí"
        else:
            castrado_texto = "No"

        peso_texto = "No informado" if peso is None else f"{peso} kg"

        self.HC_client_label.config(
            text=f"Cliente: {nombre_cliente} {apellido_cliente}"
        )
        self.client_phone_label.config(text=f"Teléfono: {telefono}")
        self.client_address_label.config(
            text=f"Domicilio: {domicilio or 'No informado'}"
        )
        self.client_dni_label.config(text=f"DNI: {dni}")
        self.patient_name_label.config(text=f"Paciente: {nombre_paciente}")
        self.patient_species_label.config(text=f"Especie: {especie}")
        self.patient_age_label.config(text=f"Edad: {edad_texto}")
        self.patient_sex_label.config(text=f"Sexo: {sexo or 'No informado'}")
        self.patient_neutered_label.config(text=f"Castrado: {castrado_texto}")
        self.patient_weight_label.config(text=f"Peso: {peso_texto}")

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
        dialog = tk.Toplevel(self)
        dialog.transient(self.winfo_toplevel())
        dialog.configure(
            bg="white",
            highlightbackground="#333333",
            highlightthickness=1,
        )

        tk.Label(
            dialog,
            text="Está finalizando la consulta.\n¿Desea GUARDAR los cambios?",
            font=("Arial", 12),
            justify="center",
            bg="white",
            fg="#1F1F1F",
        ).pack(padx=40, pady=(28, 24))

        buttons_frame = tk.Frame(dialog, bg="white")
        buttons_frame.pack(fill="x", padx=40, pady=(0, 28))

        tk.Button(
            buttons_frame,
            text="ATRÁS",
            font=("Arial", 11, "bold"),
            bg="#D1D5DB",
            fg="#1F1F1F",
            relief="flat",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=dialog.destroy,
        ).pack(side="left", expand=True, padx=(0, 10))

        tk.Button(
            buttons_frame,
            text="GUARDAR",
            font=("Arial", 11, "bold"),
            bg="#8FD694",
            fg="#1F1F1F",
            relief="flat",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=lambda: self._guardar_consulta_confirmada(dialog),
        ).pack(side="right", expand=True, padx=(10, 0))

        dialog.update_idletasks()
        parent = self.winfo_toplevel()
        parent.update_idletasks()
        x = parent.winfo_rootx() + (
            parent.winfo_width() - dialog.winfo_width()
        ) // 2
        y = parent.winfo_rooty() + (
            parent.winfo_height() - dialog.winfo_height()
        ) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.grab_set()

    def _guardar_consulta_confirmada(self, dialog):
        opcion_veterinario = self.veterinario_var.get().strip()
        matricula = self.veterinarios_por_opcion.get(opcion_veterinario)

        if not matricula:
            messagebox.showwarning(
                "Falta seleccionar veterinario",
                "Seleccioná el veterinario que realizó la consulta.",
                parent=self,
            )
            dialog.destroy()
            return

        opcion_turno = self.turno_var.get().strip()
        if opcion_turno not in self.turnos_por_opcion:
            messagebox.showwarning(
                "Falta seleccionar turno",
                "Seleccioná un turno o la opción 'Sin turno'",
                parent=self,
            )
            dialog.destroy()
            return

        id_turno = self.turnos_por_opcion[opcion_turno]

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
            dialog.destroy()
            return

        if len(notas) > 200:
            messagebox.showwarning(
                "Notas demasiado largas",
                "El campo Notas admite hasta 200 caracteres.",
                parent=self,
            )
            dialog.destroy()
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
                    id_turno=id_turno,
                )
                consultas = obtener_consultas_paciente(
                    conexion,
                    self.id_paciente_seleccionado,
                )
                historias = obtener_historias(
                    conexion,
                    self.searchbar.get_search_text(),
                    self.searchbar.filter_options.get(),
                )
        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Error al guardar la consulta",
                f"No se pudo guardar la consulta en la base de datos:\n{error}",
                parent=self,
            )
            return

        dialog.destroy()

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
        self._cargar_turnos_pendientes(turnos_pendientes)

        self._actualizar_tabla_historias(historias)

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
            font=("Arial", 12),
            bg="white",
        )

        self.client_address_label = tk.Label(
            self.client_contact_frame,
            text="Domicilio: Sobremonte 2011",
            font=("Arial", 12),
            bg="white",
        )

        self.client_dni_label = tk.Label(
            self.client_contact_frame,
            text="DNI: 98555888",
            font=("Arial", 12),
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
        self.HC_title_label.pack(side="left", padx=(30, 0))
        self.HC_number_label.pack(side="left", padx=(6, 20))
        self.HC_client_label.pack(side="left")

        self.hc_patient_info_frame.pack(fill="x", padx=12, pady=6)

        for columna in range(6):
            self.hc_patient_info_frame.grid_columnconfigure(columna, weight=1)

        self.patient_name_label.grid(row=0, column=0, sticky="w", padx=6)
        self.patient_species_label.grid(row=0, column=1, sticky="w", padx=6)
        self.patient_age_label.grid(row=0, column=2, sticky="w", padx=6)
        self.patient_sex_label.grid(row=0, column=3, sticky="w", padx=6)
        self.patient_neutered_label.grid(row=0, column=4, sticky="w", padx=6)
        self.patient_weight_label.grid(row=0, column=5, sticky="w", padx=6)

        self.selectores_frame = tk.Frame(
            self.historia_clinica_frame,
            bg="white",
        )
        self.selectores_frame.pack(
            fill="x",
            padx=12,
            pady=(0, 6),
        )

        self.veterinario_selector_frame = tk.Frame(
            self.selectores_frame,
            bg="white",
        )

        tk.Label(
            self.veterinario_selector_frame,
            text="Veterinario de la consulta:",
            bg="white",
            font=("Arial", 11),
        ).pack(side="left", padx=(6, 4))

        self.veterinario_var = tk.StringVar()
        self.veterinario_selector = ttk.Combobox(
            self.veterinario_selector_frame,
            textvariable=self.veterinario_var,
            state="readonly",
            width=18,
            font=("Arial", 11),
        )
        self.veterinario_selector.pack(side="left")
        self.veterinario_selector_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )

        self.turno_selector_frame = tk.Frame(
            self.selectores_frame,
            bg="white",
        )

        tk.Label(
            self.turno_selector_frame,
            text="Turno pendiente de hoy:",
            bg="white",
            font=("Arial", 11),
        ).pack(side="left", padx=(6, 4))

        self.turno_var = tk.StringVar()
        self.turno_selector = ttk.Combobox(
            self.turno_selector_frame,
            textvariable=self.turno_var,
            state="readonly",
            width=18,
            font=("Arial", 11),
        )
        self.turno_selector.pack(side="left")
        self.turno_selector_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
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

        tk.Label(
            header_frame,
            text="Nueva Historia Clínica",
            font=("Arial", 16, "bold"),
            bg="white",
        ).pack(side="left")

        self.btn_guardar = tk.Button(
            header_frame,
            text="💾 Guardar",
            font=("Arial", 12),
            relief="flat",
            bg="#A8D5BA",
            cursor="hand2",
            command=self._guardar_nueva_hc,
        )
        self.btn_guardar.pack(side="right")

        bg_green = "#C8E6C9"
        form_frame = tk.Frame(self.add_hc_view, bg=bg_green, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True, padx=40, pady=10)

        for nombre_variable in (
            "nombre_cliente",
            "apellido_cliente",
            "dni_cliente",
            "telefono_cliente",
            "mail_cliente",
            "domicilio_cliente",
            "nombre_paciente",
            "especie_paciente",
            "raza_paciente",
            "sexo_paciente",
        ):
            setattr(self, f"var_{nombre_variable}", tk.StringVar())

        tk.Label(
            form_frame,
            text="Datos del cliente",
            font=("Arial", 10, "bold"),
            bg=bg_green,
        ).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        self._agregar_campo_formulario(
            form_frame, "Nombre *", self.var_nombre_cliente, 1, 0, bg_green
        )
        self._agregar_campo_formulario(
            form_frame, "Apellido *", self.var_apellido_cliente, 1, 2, bg_green
        )
        self._agregar_campo_formulario(
            form_frame, "DNI *", self.var_dni_cliente, 1, 4, bg_green
        )
        self._agregar_campo_formulario(
            form_frame, "Teléfono *", self.var_telefono_cliente, 2, 0, bg_green
        )
        self._agregar_campo_formulario(
            form_frame, "Email", self.var_mail_cliente, 2, 2, bg_green
        )
        self._agregar_campo_formulario(
            form_frame, "Domicilio", self.var_domicilio_cliente, 2, 4, bg_green
        )

        tk.Label(
            form_frame,
            text="Datos del paciente",
            font=("Arial", 10, "bold"),
            bg=bg_green,
        ).grid(row=3, column=0, columnspan=6, sticky="w", pady=(24, 10))

        self._agregar_campo_formulario(
            form_frame, "Nombre *", self.var_nombre_paciente, 4, 0, bg_green
        )
        self._agregar_campo_formulario(
            form_frame, "Especie *", self.var_especie_paciente, 4, 2, bg_green
        )
        self._agregar_campo_formulario(
            form_frame, "Raza", self.var_raza_paciente, 4, 4, bg_green
        )
        self._agregar_campo_formulario(
            form_frame, "Sexo", self.var_sexo_paciente, 5, 0, bg_green
        )

        for columna in (1, 3, 5):
            form_frame.grid_columnconfigure(columna, weight=1)

        tk.Label(
            form_frame,
            text=(
                "Los campos marcados con * son obligatorios. "
                "Si el DNI ya existe, se conservarán los datos del cliente "
                "y se agregará el paciente a ese cliente."
            ),
            bg=bg_green,
            wraplength=800,
            justify="left",
        ).grid(row=6, column=0, columnspan=6, sticky="w", pady=(24, 0))

    @staticmethod
    def _agregar_campo_formulario(
        parent,
        etiqueta,
        variable,
        fila,
        columna,
        color_fondo,
    ):
        tk.Label(
            parent,
            text=etiqueta,
            bg=color_fondo,
        ).grid(row=fila, column=columna, sticky="e", padx=5, pady=5)
        tk.Entry(
            parent,
            textvariable=variable,
        ).grid(
            row=fila,
            column=columna + 1,
            sticky="ew",
            padx=5,
            pady=5,
        )

    def _guardar_nueva_hc(self):
        datos = {
            "dni": self.var_dni_cliente.get().strip(),
            "nombre_cliente": self.var_nombre_cliente.get().strip(),
            "apellido_cliente": self.var_apellido_cliente.get().strip(),
            "telefono": self.var_telefono_cliente.get().strip(),
            "mail": self.var_mail_cliente.get().strip(),
            "domicilio": self.var_domicilio_cliente.get().strip(),
            "nombre_paciente": self.var_nombre_paciente.get().strip(),
            "especie": self.var_especie_paciente.get().strip(),
            "raza": self.var_raza_paciente.get().strip(),
            "sexo": self.var_sexo_paciente.get().strip(),
        }
        requeridos = (
            "dni",
            "nombre_cliente",
            "apellido_cliente",
            "telefono",
            "nombre_paciente",
            "especie",
        )
        if any(not datos[campo] for campo in requeridos):
            messagebox.showwarning(
                "Faltan datos obligatorios",
                "Completá todos los campos marcados con *.",
                parent=self,
            )
            return

        try:
            with conectar() as conexion:
                id_paciente, cliente_creado = registrar_cliente_y_paciente(
                    conexion,
                    datos["dni"],
                    datos["nombre_cliente"],
                    datos["apellido_cliente"],
                    datos["telefono"],
                    datos["mail"],
                    datos["domicilio"],
                    datos["nombre_paciente"],
                    datos["especie"],
                    datos["raza"],
                    datos["sexo"],
                )
                historias = obtener_historias(conexion, "", "Todos")
        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Error al guardar la historia clínica",
                f"No se pudo guardar el cliente y el paciente:\n{error}",
                parent=self,
            )
            return

        self._actualizar_tabla_historias(historias)
        self.searchbar.search_entry.delete(0, tk.END)
        self.searchbar.filter_options.set("Todos")
        self._limpiar_formulario_hc()
        self.show_section("buscar_hc")

        mensaje = f"Se creó la historia clínica Nº {id_paciente}."
        if not cliente_creado:
            mensaje += (
                "\nEl DNI ya estaba registrado; se conservaron los datos "
                "existentes del cliente."
            )
        messagebox.showinfo(
            "Historia clínica guardada",
            mensaje,
            parent=self,
        )

    def _limpiar_formulario_hc(self):
        for nombre_variable in (
            "nombre_cliente",
            "apellido_cliente",
            "dni_cliente",
            "telefono_cliente",
            "mail_cliente",
            "domicilio_cliente",
            "nombre_paciente",
            "especie_paciente",
            "raza_paciente",
            "sexo_paciente",
        ):
            getattr(self, f"var_{nombre_variable}").set("")

    def _abrir_modal_eliminar_hc(self):
        id_paciente = self._obtener_id_paciente_seleccionado()
        if id_paciente is None:
            return

        # 1. Ventana emergente limpia sin barra de Windows
        if not self.search_view.winfo_manager():
            messagebox.showwarning(
                "Sección no disponible",
                "Volvé a la búsqueda de historias clínicas para eliminar una HC.",
                parent=self,
            )
            return

        if self.historia_clinica_frame.winfo_manager():
            id_paciente = self.id_paciente_seleccionado
        else:
            seleccion = self.hc_table.selection()
            if not seleccion:
                messagebox.showwarning(
                    "Seleccioná una historia clínica",
                    "Seleccioná una fila de la lista antes de eliminar.",
                    parent=self,
                )
                return

            valores = self.hc_table.item(seleccion[0], "values")
            try:
                id_paciente = int(valores[3])
            except (IndexError, TypeError, ValueError):
                messagebox.showerror(
                    "Selección inválida",
                    "No se pudo identificar la historia clínica seleccionada.",
                    parent=self,
                )
                return
        dialog = tk.Toplevel(self)
        dialog.transient(self.winfo_toplevel())
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
            text=(
                "Se eliminarán permanentemente el paciente,\n"
                "sus consultas y todos sus turnos,\n"
                "incluidos los cancelados. El cliente se conservará."
            ),
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
            command=lambda: self._confirmar_eliminar_hc(dialog, id_paciente),
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

    def _confirmar_eliminar_hc(self, dialog, id_paciente):
        try:
            with conectar() as conexion:
                eliminado = eliminar_historia_clinica(conexion, id_paciente)
        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Error al eliminar la historia clínica",
                f"No se pudo eliminar la historia clínica:\n{error}",
                parent=self,
            )
            return

        if not eliminado:
            dialog.destroy()
            messagebox.showwarning(
                "Historia clínica no encontrada",
                "No se encontró el paciente seleccionado en la base de datos.",
                parent=self,
            )
            return

        dialog.destroy()

        if self.historia_clinica_frame.winfo_manager():
            self._cerrar_historia_clinica()

        for item_id in self.hc_table.get_children():
            self.hc_table.delete(item_id)

        try:
            self._cargar_historias()
        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            messagebox.showwarning(
                "Historia eliminada, lista no actualizada",
                "La historia se eliminó de la base de datos, "
                f"pero no se pudo actualizar el listado:\n{error}",
                parent=self,
            )
            return

        messagebox.showinfo(
            "Historia clínica eliminada",
            "Se eliminaron el paciente, sus consultas y sus turnos. "
            "El cliente se conservó.",
            parent=self,
        )
    
    def _abrir_modal_eliminar_cliente(self):
        id_paciente = self._obtener_id_paciente_seleccionado()
        if id_paciente is None:
            return

        # 1. Ventana emergente limpia sin barra de Windows
        dialog = tk.Toplevel(self)
        dialog.transient(self.winfo_toplevel())
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
                "El cliente quedará inhabilitado.\n"
                "Se conservarán sus pacientes, historias\n"
                "clínicas, consultas y turnos."
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
            command=lambda: self._confirmar_eliminar_cliente(
                dialog,
                id_paciente,
            ),
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

    def _confirmar_eliminar_cliente(self, dialog, id_paciente):
        try:
            with conectar() as conexion:
                inhabilitado = inhabilitar_cliente_de_paciente(
                    conexion,
                    id_paciente,
                )
                historias = obtener_historias(
                    conexion,
                    self.searchbar.get_search_text(),
                    self.searchbar.filter_options.get(),
                )
        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Error al inhabilitar el cliente",
                f"No se pudo inhabilitar el cliente:\n{error}",
                parent=self,
            )
            return

        dialog.destroy()

        if not inhabilitado:
            messagebox.showwarning(
                "Cliente no encontrado",
                "No se encontró el cliente asociado al paciente seleccionado.",
                parent=self,
            )
            return

        self._actualizar_historias_en_pantalla(historias)
        messagebox.showinfo(
            "Cliente inhabilitado",
            "El cliente fue inhabilitado. Sus pacientes, historias clínicas, "
            "consultas y turnos se conservaron.",
            parent=self,
        )

    def _obtener_id_paciente_seleccionado(self):
        if not self.search_view.winfo_manager():
            messagebox.showwarning(
                "Abrí la búsqueda de historias clínicas",
                "Volvé a la lista de historias clínicas para seleccionar "
                "el registro que querés eliminar.",
                parent=self,
            )
            return None

        seleccion = self.hc_table.selection()
        if not seleccion:
            messagebox.showwarning(
                "Seleccioná una historia clínica",
                "Seleccioná una fila de la lista antes de eliminar.",
                parent=self,
            )
            return None

        valores = self.hc_table.item(seleccion[0], "values")
        if len(valores) <= 3:
            messagebox.showerror(
                "Selección inválida",
                "No se pudo identificar el paciente seleccionado.",
                parent=self,
            )
            return None

        try:
            return int(valores[3])
        except (TypeError, ValueError):
            messagebox.showerror(
                "Selección inválida",
                "El identificador del paciente seleccionado no es válido.",
                parent=self,
            )
            return None

    def _actualizar_historias_en_pantalla(self, historias):
        self._actualizar_tabla_historias(historias)
        self.id_paciente_seleccionado = None
        if self.historia_clinica_frame.winfo_manager():
            self._cerrar_historia_clinica()
