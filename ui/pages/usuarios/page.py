import tkinter as tk
from tkinter import ttk

from ui.widgets.searchbar import Searchbar


class UsuariosPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        # --- FRAMES DE VISTAS DE SUB MENU ---
        self.profiles_view = tk.Frame(self, bg="white")
        self.add_professional_view = tk.Frame(self, bg="white")
        # 1. Agregamos el nuevo frame para ver el detalle del perfil
        self.profile_detail_view = tk.Frame(self, bg="white")

        self._build_profiles_view()
        self._build_profile_detail_view()  # 2. Llamamos a la construcción del diseño
        self._build_add_professional_view()  # 3. Llama a la construcción de la vista de agregar profesional

        self.show_section("perfiles")  # Mostrar la vista de perfiles por defecto

    def show_section(self, section):
        # Oculta todas las vistas
        self.profiles_view.pack_forget()
        self.add_professional_view.pack_forget()
        self.profile_detail_view.pack_forget()  # Ocultamos la nueva vista

        # Muestra únicamente la sección elegida
        if section == "perfiles":
            self.profiles_view.pack(fill="both", expand=True)
        elif section == "agregar_profesional":
            self.add_professional_view.pack(fill="both", expand=True)
        elif section == "ver_perfil":
            self.profile_detail_view.pack(
                fill="both", expand=True
            )  # Mostramos la nueva vista
        else:
            raise ValueError(f"Sección de Usuarios desconocida: {section}")

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
        self.tabla.heading("profesional", text="Profeesionales", anchor="w")
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

        # Cargar datos de prueba
        self.cargar_datos_prueba()

        self.tabla.bind("<Double-1>", self._open_profile_detail)

    def cargar_datos_prueba(self):
        datos = [
            (
                "Britney Lanzas",
                "A4738294",
                "Activo",
                "Veterinario",
                "britney.lanzas@email.com",
                "britneyl",
            ),
            (
                "Raul Marian",
                "A4738293",
                "Activo",
                "Asistente",
                "raul.marian@email.com",
                "raulm",
            ),
        ]

        for prof, mat, estado, rol, contacto, usuario in datos:
            self.tabla.insert(
                "",
                "end",
                values=(prof, mat, estado, rol, contacto, usuario),
                tags=("activo" if estado == "Activo" else "inactivo",),
            )

    def _open_profile_detail(self, event):
        item_id = self.tabla.identify_row(event.y)
        if not item_id:
            return "break"

        values = self.tabla.item(item_id, "values")
        if not values:
            return "break"

        self._update_profile_detail(values)
        self.show_section("ver_perfil")
        return "break"

    def _update_profile_detail(self, values):
        name, registration, status, role, contact, username = values
        extra_details = {
            "britneyl": {
                "specialty": "Oftalmología felina",
                "active_since": "07-02-2026",
                "address": "Av. Siempreviva 742",
                "contact": "35162947390",
                "emergency_contact": "35162947392",
            }
        }.get(username, {})

        self.profile_detail_labels["username"].config(text=f"Usuario: {username}")
        self.profile_detail_labels["role"].config(text=f"Rol: {role}")
        self.profile_detail_labels["registration"].config(text=registration)
        self.profile_detail_labels["specialty"].config(
            text=f"Especialidad: {extra_details.get('specialty', 'No disponible')}"
        )
        self.profile_detail_labels["active_since"].config(
            text=f"Activo desde: {extra_details.get('active_since', 'No disponible')}"
        )
        self.profile_detail_labels["name"].config(text=f"Nombre: {name}")
        self.profile_detail_labels["address"].config(
            text=f"Domicilio: {extra_details.get('address', 'No disponible')}"
        )
        self.profile_detail_labels["contact"].config(
            text=f"Contacto: {extra_details.get('contact', 'No disponible')}"
        )
        self.profile_detail_labels["email"].config(text=f"Correo: {contact}")
        self.profile_detail_labels["emergency_contact"].config(
            text=f"Contacto de emergencia: {extra_details.get('emergency_contact', 'No disponible')}"
        )
        self.profile_detail_labels["status"].config(text=f"Estado: {status}")

    def filtrar_profesionales(self, texto):
        pass

    def _build_profile_detail_view(self):
        self.profile_detail_labels = {}
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
        for key, label_text in (
            ("name", "Nombre: "),
            ("address", "Domicilio: No disponible"),
            ("contact", "Contacto: "),
            ("email", "Correo: "),
            ("emergency_contact", "Contacto de emergencia: No disponible"),
        ):
            self.profile_detail_labels[key] = tk.Label(
                datos_frame, text=label_text, bg="white"
            )
            self.profile_detail_labels[key].pack(anchor="w", pady=5)

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
        ).pack(side="right", expand=True, fill="x", padx=(5, 0))

        # crea la vista de crear perfil

    def _build_add_professional_view(self):

        form_frame = tk.Frame(self.add_professional_view, bg="#F0F0F0")
        form_frame.place(
            relx=0.5, rely=0.5, relwidth=0.9, relheight=0.7, anchor="center"
        )

        columnas = tk.Frame(form_frame, bg="#F0F0F0")
        columnas.pack(fill="both", expand=True, padx=40, pady=(30, 10))

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

        # un for para no repetir tanto codigo. Podriamos ver de traer los datos directos de la BD asi no quedan hardcodeados

        for label_text in (
            "Usuario",
            "Rol",
            "Matrícula",
            "Especialidad",
        ):
            fila_frame = tk.Frame(left_frame, bg="#FFFFFF")
            fila_frame.pack(anchor="w", padx=20, pady=(2, 10))

            tk.Label(
                fila_frame, text=f"{label_text}:", anchor="w", width=22, bg="#FFFFFF"
            ).pack(side="left")
            entrada_frame = tk.Frame(left_frame, bg="#FFFFFF")
            entrada_frame.pack(anchor="w", padx=20, pady=(2, 10))

            tk.Entry(
                entrada_frame,
                width=40,
                bd=0,
                relief="flat",
                highlightthickness=0,
                bg="#FFFFFF",
            ).pack()
            tk.Frame(entrada_frame, height=1, bg="#555555").pack(fill="x")

        right_frame = tk.Frame(columnas, bg="#FFFFFF")
        right_frame.pack(side="left", fill="both", expand=True, padx=(12, 0))

        for label_text in (
            "Nombre",
            "Domicilio",
            "Contacto",
            "Correo",
            "Contacto de emergencia",
        ):
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
                width=24,
                bd=0,
                relief="flat",
                highlightthickness=0,
                bg="#FFFFFF",
            ).pack(fill="x")
            tk.Frame(entrada_frame, height=1, bg="#555555").pack(fill="x")

        botones_frame = tk.Frame(form_frame, bg="#F0F0F0")
        botones_frame.pack(fill="x", padx=40, pady=(10, 30))

        tk.Button(
            botones_frame,
            text="Cancelar",
            command=lambda: self.show_section("perfiles"),
            bg="#F0F0F0",
            relief="flat",
            padx=10,
            pady=8,
            width=40,
        ).pack(side="left", padx=(0, 5))
        tk.Button(
            botones_frame,
            text="Crear Perfil",
            bg="#0DB90D",
            fg="white",
            relief="flat",
            padx=10,
            pady=8,
            width=40,
        ).pack(side="right", padx=(5, 0))
