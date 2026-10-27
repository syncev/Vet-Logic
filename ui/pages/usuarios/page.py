import tkinter as tk
import psycopg
from tkinter import messagebox, ttk
from core.db import conectar

from repositories.usuarios import (
    actualizar_profesional,
    crear_profesional,
    inhabilitar_profesional,
    obtener_profesionales_activos,
)
from ui.widgets.searchbar import Searchbar


class UsuariosPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        # --- FRAMES DE VISTAS DE SUB MENU ---
        self.profiles_view = tk.Frame(self, bg="white")
        self.add_professional_view = tk.Frame(self, bg="white")
        # 1. Agregamos el nuevo frame para ver el detalle del perfil
        self.profile_detail_view = tk.Frame(self, bg="white")

        self.veterinarios_por_matricula = {}

        self._build_profiles_view()
        self._build_profile_detail_view()  # 2. Llamamos a la construcción del diseño
        self._build_add_professional_view()  # 3. Llama a la construcción de la vista de agregar profesional
              
        self.show_section("perfiles")  # Mostrar la vista de perfiles por defecto

    def set_aside(self, aside_instance):
        self.aside = aside_instance
        
    def show_section(self, section):
        # Oculta todas las vistas
        self.profiles_view.pack_forget()
        self.add_professional_view.pack_forget()
        self.profile_detail_view.pack_forget()
        
        if hasattr(self, "aside") and self.aside:
            self.aside.ocultar_inhabilitar()

        # Muestra únicamente la sección elegida
        if section == "perfiles":
            self.cargar_profesionales()
            self.profiles_view.pack(fill="both", expand=True)
        elif section == "agregar_profesional":
            self.add_professional_view.pack(fill="both", expand=True)
        elif section == "ver_perfil":
            self.profile_detail_view.pack(fill="both", expand=True)
            if hasattr(self, 'aside') and self.aside:
                self.aside.mostrar_inhabilitar(self._abrir_modal_inhabilitar)

        else:
            raise ValueError(f"Sección de Usuarios desconocida: {section}")    # Oculta todas las vistas
        
    def _build_profiles_view(self):

        # --- BARRA DE BÚSQUEDA ---
        self.searchbar = Searchbar(
            self.profiles_view,
            controls_relwidth=1.0,
            title_text="Búsqueda de Profesionales",
            filter_values=[
                "Todos",
                "Nombre",
                "Apellido",
                "Matrícula",
            ],
            on_search=self._buscar_profesionales,
        )
        self.searchbar.pack(
            pady=(0, 10),
            padx=40,
            fill="x",
        )

        # --- TABLA DE PROFESIONALES ---
        frame_tabla = tk.Frame(self.profiles_view, bg="white")
        frame_tabla.pack(fill="both", expand=True)

        columnas = ("profesional", "matricula", "estado", "rol", "contacto", "usuario")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings", height=8
        )

        # Encabezados
        self.tabla.heading("profesional", text="Profesionales", anchor="w")
        self.tabla.heading("matricula", text="Matricula", anchor="w")
        self.tabla.heading("estado", text="Activo/Inactivo", anchor="center")
        self.tabla.heading("rol", text="Rol", anchor="w")
        self.tabla.heading("contacto", text="Contacto", anchor="w")
        self.tabla.heading("usuario", text="Usuario", anchor="w")

        # Anchos de columna
        self.tabla.column("profesional", width=220, anchor="w")
        self.tabla.column("matricula", width=120, anchor="w")
        self.tabla.column("estado", width=120, anchor="center")
        self.tabla.column("rol", width=120, anchor="w")
        self.tabla.column("contacto", width=120, anchor="w")
        self.tabla.column("usuario", width=120, anchor="w")

        # Estilo morado para Activo
        self.tabla.tag_configure("activo", foreground="#6200EE")

        self.tabla.pack(fill="both", expand=True)

        self.tabla.bind("<Double-1>", self._open_profile_detail)

    def cargar_profesionales(self):
        try:
            with conectar() as conexion:
                filas = obtener_profesionales_activos(conexion)
        except (psycopg.Error, OSError, ValueError) as error:
            messagebox.showerror(
                "Error al cargar profesionales",
                f"No se pudieron consultar los veterinarios de la base de datos:\n{error}",
                parent=self,
            )
            return

        veterinarios = {}
        for matricula, nombre, apellido, estado, contacto, especialidad, domicilio, correo, emergencia in filas:
            veterinarios[matricula] = {
                "nombre": nombre,
                "apellido": apellido,
                "estado": estado,
                "contacto": contacto,
                "especialidad": especialidad,
                "domicilio": domicilio,
                "correo": correo,
                "contacto_emergencia": emergencia,
            }

        self.veterinarios_por_matricula = veterinarios

        for item_id in self.tabla.get_children():
            self.tabla.delete(item_id)

        for matricula, datos in veterinarios.items():
            estado = "Activo" if datos["estado"] == "ACTIVO" else "Inactivo"
            nombre_completo = f'{datos["nombre"]} {datos["apellido"]}'

            self.tabla.insert(
                "",
                "end",
                values=(
                    nombre_completo,
                    matricula,
                    estado,
                    "Veterinario",
                    datos["contacto"] or "No disponible",
                    "No disponible",
                ),
                tags=("activo" if estado == "Activo" else "inactivo",),
            )

    def _open_profile_detail(self, event):
        item_id = self.tabla.identify_row(event.y)
        if not item_id:
            return "break"

        values = self.tabla.item(item_id, "values")
        if not values:
            return "break"

        if not self._update_profile_detail(values):
            return "break"

        self.show_section("ver_perfil")
        return "break"

    def _update_profile_detail(self, values):
        name, registration, status, role, contact, username = values
        datos = self.veterinarios_por_matricula.get(registration)

        if datos is None:
            messagebox.showerror(
                "Perfil no disponible",
                "No se encontraron los datos del veterinario seleccionado.",
                parent=self,
            )
            return False

        self.username_actual = username
        self.matricula_actual = registration

        self.profile_detail_labels["username"].config(text=f"Usuario: {username}")
        self.profile_detail_labels["role"].config(text=f"Rol: {role}")
        self.profile_detail_labels["registration"].config(text=registration)
        self.profile_detail_labels["specialty"].config(
            text=f"Especialidad: {datos['especialidad'] or 'No disponible'}"
        )
        self.profile_detail_labels["active_since"].config(
            text="Activo desde: No disponible"
        )
        self.profile_detail_labels["status"].config(text=f"Estado: {status}")

        datos_a_cargar = {
            "name": f"{datos['nombre']} {datos['apellido']}",
            "address": datos["domicilio"] or "No disponible",
            "contact": datos["contacto"] or "No disponible",
            "email": datos["correo"] or "No disponible",
            "emergency_contact": (
                datos["contacto_emergencia"] or "No disponible"
            ),
        }

        for key, entry in self.profile_detail_entries.items():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, datos_a_cargar.get(key, ""))
            entry.config(state="disabled")
        return True

    def filtrar_profesionales(self, texto):
        pass

    def _build_profile_detail_view(self):
        self.profile_detail_labels = {}
        self.profile_detail_entries = {}  # Cajas de texto para editar
        left_frame = tk.Frame(self.profile_detail_view, bg="white", padx=20, pady=20)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)

        right_frame = tk.Frame(self.profile_detail_view, bg="#F0F0F0")
        right_frame.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        # COLUMNA IZQUIERDA
        tk.Label(left_frame, text="FOTO", bg="#D9D9D9", width=15, height=7).pack(
            pady=(10, 20)
        )

        self.profile_detail_labels["username"] = tk.Label(
            left_frame, text="Usuario: ", bg="white", font=("Arial", 10, "bold")
        )
        self.profile_detail_labels["username"].pack(anchor="w", pady=4)
        self.profile_detail_labels["role"] = tk.Label(
            left_frame, text="Rol: ", bg="white"
        )
        self.profile_detail_labels["role"].pack(anchor="w", pady=4)

        # Para que la matrícula quede violeta y en la misma línea, usamos un mini-frame
        mat_frame = tk.Frame(left_frame, bg="white")
        mat_frame.pack(anchor="w", pady=4)
        tk.Label(
            mat_frame, text="Matrícula: ", bg="white", font=("Arial", 10, "bold")
        ).pack(side="left")
        self.profile_detail_labels["registration"] = tk.Label(
            mat_frame, text="", bg="white", fg="#8A2BE2"
        )
        self.profile_detail_labels["registration"].pack(side="left")

        for key, label_text in (
            ("specialty", "Especialidad: No disponible"),
            ("active_since", "Activo desde: No disponible"),
            ("status", "Estado: "),
        ):
            self.profile_detail_labels[key] = tk.Label(
                left_frame, text=label_text, bg="white"
            )
            self.profile_detail_labels[key].pack(anchor="w", pady=4)

        # ---COLUMNA DERECHA ---
        tk.Button(
            right_frame,
            text="Ver historial",
            bg="#D1C4E9",
            font=("Arial", 12),
            relief="flat",
        ).pack(fill="x", pady=(0, 20))

        datos_frame = tk.Frame(right_frame, bg="white", padx=20, pady=20)
        datos_frame.pack(fill="both", expand=True)

        tk.Label(
            datos_frame,
            text="Datos Personales:",
            bg="white",
            font=("Arial", 11, "bold"),
        ).pack(anchor="w", pady=(0, 15))

       # Inicializamos el diccionario de entries para la edición
        self.profile_detail_entries = {}
        
        for key, label_text in (
            ("name", "Nombre: "),
            ("address", "Domicilio: No disponible"),
            ("contact", "Contacto: "),
            ("email", "Correo: "),
            ("emergency_contact", "Contacto de emergencia: No disponible"),
        ):
        # Creamos un mini frame para cada línea
            frame_campo = tk.Frame(datos_frame, bg="white")
            frame_campo.pack(anchor="w", fill="x", pady=5)
            
        # Extraemos la etiqueta limpia
            texto_etiqueta = label_text.split(":")[0] + ":"
            tk.Label(frame_campo, text=texto_etiqueta, bg="white", width=22, anchor="w").pack(side="left")
            
        # Creamos el Entry bloqueado por defecto
            entry = tk.Entry(frame_campo, font=("Arial", 10), state="disabled", width=30)
            entry.pack(side="left", fill="x", expand=True)
            self.profile_detail_entries[key] = entry

        botones_frame = tk.Frame(right_frame, bg="#F0F0F0")
        botones_frame.pack(fill="x", pady=(20, 0))

        tk.Button(
            botones_frame,
            text="Modificar datos",
            bg="#D1C4E9",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self._habilitar_edicion,
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        tk.Button(
            botones_frame,
            text="Guardar",
            bg="#32CD32",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self._guardar_cambios_bd,
        ).pack(side="right", expand=True, fill="x", padx=(5, 0))

        
    def _build_add_professional_view(self):
        self.var_usuario = tk.StringVar(master=self)
        self.var_rol = tk.StringVar(master=self)
        self.var_matricula = tk.StringVar(master=self)
        self.var_especialidad = tk.StringVar(master=self)
        self.var_nombre = tk.StringVar(master=self)
        self.var_apellido = tk.StringVar(master=self)
        self.var_domicilio = tk.StringVar(master=self)
        self.var_contacto = tk.StringVar(master=self)
        self.var_correo = tk.StringVar(master=self)
        self.var_contacto_emergencia = tk.StringVar(master=self)

        form_frame = tk.Frame(self.add_professional_view, bg="#F0F0F0")
        form_frame.place(
            relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor="center"
        )

        columnas = tk.Frame(form_frame, bg="#F0F0F0")
        columnas.pack(side="top", fill="both", expand=True, padx=40, pady=(15, 5))

        left_frame = tk.Frame(columnas, bg="#FFFFFF")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 12))

        foto_frame = tk.Frame(left_frame, width=140, height=140, bg="#D9D9D9")
        foto_frame.pack(pady=(0, 20))
        foto_frame.pack_propagate(False)  # Evita que el frame se ajuste al contenido

        foto_canvas = tk.Canvas(
            foto_frame, width=140, height=140, bg="#FFFFFF", highlightthickness=0
        )
        foto_canvas.pack(fill="both", expand=True)
        foto_canvas.create_oval(
            4, 4, 136, 136, fill="#D9D9D9", outline=""
        )  # Círculo gris para la foto
        foto_canvas.create_text(70, 70, text="Foto", fill="#333333")
        tk.Button(foto_frame, text="+", font=("Arial", 16, "bold")).place(
            relx=1.0, rely=1.0, anchor="se"
        )

        campos_izq = (
            ("Usuario", self.var_usuario),
            ("Rol", self.var_rol),
            ("Matrícula", self.var_matricula),
            ("Especialidad", self.var_especialidad),
        )

        for label_text, variable in campos_izq:
            fila_frame = tk.Frame(left_frame, bg="#FFFFFF")
            fila_frame.pack(anchor="w", padx=20, pady=(2, 10))

            tk.Label(
                fila_frame, text=f"{label_text}:", anchor="w", width=22, bg="#FFFFFF"
            ).pack(side="left")
            entrada_frame = tk.Frame(left_frame, bg="#FFFFFF")
            entrada_frame.pack(anchor="w", padx=20, pady=(2, 10))

            tk.Entry(
                entrada_frame,
                textvariable=variable,
                width=40,
                bd=0,
                relief="flat",
                highlightthickness=0,
                bg="#FFFFFF",
            ).pack()
            tk.Frame(entrada_frame, height=1, bg="#555555").pack(fill="x")

        right_frame = tk.Frame(columnas, bg="#FFFFFF")
        right_frame.pack(side="left", fill="both", expand=True, padx=(12, 0))

        campos_der = (
            ("Nombre", self.var_nombre),
            ("Apellido", self.var_apellido),
            ("Domicilio", self.var_domicilio),
            ("Contacto", self.var_contacto),
            ("Correo", self.var_correo),
            ("Contacto de emergencia", self.var_contacto_emergencia),
        )

        for label_text, variable in campos_der:
            campo_frame = tk.Frame(right_frame, bg="#FFFFFF")
            campo_frame.pack(fill="x", padx=20, pady=6, expand=True)

            tk.Label(
                campo_frame,
                text=f"{label_text}:",
                anchor="w",
                bg="#FFFFFF",
            ).pack(anchor="w")

            entrada_frame = tk.Frame(campo_frame, bg="#FFFFFF")
            entrada_frame.pack(fill="x", pady=(2, 0))

            tk.Entry(
                entrada_frame,
                textvariable=variable,
                width=24,
                bd=0,
                relief="flat",
                highlightthickness=0,
                bg="#FFFFFF",
            ).pack(fill="x")
            tk.Frame(entrada_frame, height=1, bg="#555555").pack(fill="x")

        botones_frame = tk.Frame(form_frame, bg="#F0F0F0")
        botones_frame.pack(side="bottom", fill="x", padx=40, pady=15)

        tk.Button(
            botones_frame,
            text="Cancelar",
            command=self.cancelar_creacion,
            bg="#F0F0F0",
            relief="flat",
            padx=10,
            pady=6,
            width=30,
        ).pack(side="left", padx=(0, 5))
        tk.Button(
            botones_frame,
            text="Crear Perfil",
            command=self.guardar_profesional,
            bg="#0DB90D",
            fg="white",
            relief="flat",
            padx=10,
            pady=6,
            width=30,
        ).pack(side="right", padx=(5, 0))

    def guardar_profesional(self):
        matricula = self.var_matricula.get().strip()
        nombre = self.var_nombre.get().strip()
        apellido = self.var_apellido.get().strip()
        contacto = self.var_contacto.get().strip()
        especialidad = self.var_especialidad.get().strip()
        domicilio = self.var_domicilio.get().strip()
        correo = self.var_correo.get().strip()
        contacto_emergencia = self.var_contacto_emergencia.get().strip()

        if not matricula or not nombre or not apellido or not contacto:
            messagebox.showwarning(
                "Campos obligatorios",
                "Por favor completa la Matrícula, Nombre, Apellido y Contacto.",
                parent=self,
            )
            return

        try:
            with conectar() as conexion:
                crear_profesional(
                    conexion,
                    matricula,
                    nombre,
                    apellido,
                    contacto,
                    especialidad,
                    domicilio,
                    correo,
                    contacto_emergencia,
                )
        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Error de Base de Datos",
                f"Ocurrió un error al guardar: {error}",
                parent=self,
            )
            return

        messagebox.showinfo(
            "Éxito",
            "El profesional se ha registrado correctamente.",
            parent=self,
        )
        self.cancelar_creacion()

    def cancelar_creacion(self):
        for variable in (
            self.var_usuario,
            self.var_rol,
            self.var_matricula,
            self.var_especialidad,
            self.var_nombre,
            self.var_apellido,
            self.var_domicilio,
            self.var_contacto,
            self.var_correo,
            self.var_contacto_emergencia,
        ):
            variable.set("")

        self.show_section("perfiles")

    def _abrir_modal_inhabilitar(self):
        # Crear la ventana emergente (Toplevel) para la confirmación
        modal = tk.Toplevel(self)
        modal.title("Inhabilitar Perfil")
        modal.geometry("420x230")
        modal.configure(bg="white")
        modal.transient(self)
        modal.grab_set()  # Bloquea la ventana principal hasta que se cierre el modal

        # Etiqueta de mensaje de confirmación según Figma
        lbl_mensaje = tk.Label(
            modal,
            text="ATENCIÓN!!\n\nEsta acción no BORRA el perfil, solo lo\nINHABILITA. Puede ser recuperado\nposteriormente.",
            font=("Arial", 10),
            bg="white",
            fg="#333333",
            justify="center"
        )
        lbl_mensaje.pack(pady=20)

        # Frame contenedor para los botones de acción del modal
        frame_botones = tk.Frame(modal, bg="white")
        frame_botones.pack(pady=10)

        # Botón para cancelar y cerrar el modal (A la izquierda)
        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            bg="#E0E0E0",
            fg="#333333",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=modal.destroy
        )
        btn_cancelar.pack(side="left", padx=10)

        # Botón para continuar / confirmar la inhabilitación (A la derecha)
        btn_continuar = tk.Button(
            frame_botones,
            text="Continuar",
            bg="#FF4D4D",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=lambda: self._ejecutar_inhabilitacion(modal)
        )
        btn_continuar.pack(side="left", padx=10)

    def _ejecutar_inhabilitacion(self, modal):
        try:
            with conectar() as conexion:
                filas_actualizadas = inhabilitar_profesional(
                    conexion, self.matricula_actual
                )
        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Error al inhabilitar el perfil",
                f"No se pudo actualizar el estado del veterinario:\n{error}",
                parent=modal,
            )
            return

        if filas_actualizadas != 1:
            messagebox.showwarning(
                "Perfil no actualizado",
                "El veterinario no existe o ya estaba inhabilitado.",
                parent=modal,
            )
            return

        modal.destroy()
        messagebox.showinfo(
            "Perfil inhabilitado",
            "El veterinario pasó a estado INACTIVO.",
            parent=self,
        )
        self.show_section("perfiles")

    def _habilitar_edicion(self):
        """Habilita todas las cajas de texto para poder editarlas."""
        for entry in self.profile_detail_entries.values():
            entry.config(state="normal")

    def _guardar_cambios_bd(self):
        """Toma los valores ingresados y actualiza el profesional en la base de datos."""
        print("Usuario actual intentando guardar:", self.username_actual)
        
        nuevo_nombre = self.profile_detail_entries["name"].get()
        nuevo_domicilio = self.profile_detail_entries["address"].get()
        nuevo_contacto = self.profile_detail_entries["contact"].get()
        nuevo_correo = self.profile_detail_entries["email"].get()
        nuevo_emergencia = self.profile_detail_entries["emergency_contact"].get()

        try:
            with conectar() as conexion:
                filas_actualizadas = actualizar_profesional(
                    conexion,
                    self.matricula_actual,
                    nuevo_nombre,
                    nuevo_domicilio,
                    nuevo_contacto,
                    nuevo_correo,
                    nuevo_emergencia,
                )

            if filas_actualizadas != 1:
                messagebox.showwarning(
                    "Perfil no actualizado",
                    "No se encontró el veterinario que se intentó actualizar.",
                    parent=self,
                )
                return

            tk.messagebox.showinfo("Éxito", "¡Datos actualizados correctamente en la base de datos!")

            # Volvemos a bloquear los campos tras guardar
            for entry in self.profile_detail_entries.values():
                entry.config(state="disabled")

        except (psycopg.Error, OSError, ValueError, KeyError) as error:
            tk.messagebox.showerror("Error", f"No se pudieron guardar los cambios: {error}")

    def _buscar_profesionales(self, texto, filtro):
        texto = texto.strip().casefold()

        for item_id in self.tabla.get_children():
            self.tabla.delete(item_id)

        for matricula, datos in self.veterinarios_por_matricula.items():
            nombre = str(datos.get("nombre") or "")
            apellido = str(datos.get("apellido") or "")
            matricula_texto = str(matricula)

            if filtro == "Todos":
                coincide = (
                    texto in nombre.casefold()
                    or texto in apellido.casefold()
                    or texto in matricula_texto.casefold()
                )
            elif filtro == "Nombre":
                coincide = texto in nombre.casefold()
            elif filtro == "Apellido":
                coincide = texto in apellido.casefold()
            elif filtro == "Matrícula":
                coincide = texto in matricula_texto.casefold()
            else:
                coincide = False

            if coincide:
                estado = "Activo" if datos["estado"] == "ACTIVO" else "Inactivo"

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        f"{nombre} {apellido}",
                        matricula_texto,
                        estado,
                        "Veterinario",
                        datos.get("contacto") or "No disponible",
                        "No disponible",
                    ),
                    tags=("activo" if estado == "Activo" else "inactivo",),
                )