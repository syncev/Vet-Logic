import tkinter as tk
from tkinter import ttk

from ui.widgets.searchbar import Searchbar

class UsuariosPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="white")

        # --- BARRA DE BÚSQUEDA ---
        self.searchbar = Searchbar(
            self,
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
        frame_tabla = tk.Frame(self, bg="white")
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