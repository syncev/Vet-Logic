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
        self._build_profile_detail_view() # 2. Llamamos a la construcción del diseño
        
        self.show_section("perfiles")  # Mostrar la vista de perfiles por defecto

    def show_section(self, section):
        # Oculta todas las vistas
        self.profiles_view.pack_forget()
        self.add_professional_view.pack_forget()
        self.profile_detail_view.pack_forget() # Ocultamos la nueva vista

        # Muestra únicamente la sección elegida
        if section == "perfiles":
            self.profiles_view.pack(fill="both", expand=True)
        elif section == "agregar_profesional":
            self.add_professional_view.pack(fill="both", expand=True)
        elif section == "ver_perfil":
            self.profile_detail_view.pack(fill="both", expand=True) # Mostramos la nueva vista
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

        # Conectar el evento de "Doble Clic" en la tabla para abrir el detalle
        self.tabla.bind("<Double-1>", lambda event: self.show_section("ver_perfil"))

    def cargar_datos_prueba(self):
        datos = [
            ("Britney Lanzas", "A4738294", "Activo", "Veterinario", "britney.lanzas@email.com", "britneyl"),
            ("Raul Marian", "A4738293", "Activo", "Asistente", "raul.marian@email.com", "raulm"),
        ]

        for prof, mat, estado, rol, contacto, usuario in datos:
            self.tabla.insert(
                "",
                "end",
                values=(prof, mat, estado, rol, contacto, usuario),
                tags=("activo" if estado == "Activo" else "inactivo",),
            )

    def filtrar_profesionales(self, texto):
        pass