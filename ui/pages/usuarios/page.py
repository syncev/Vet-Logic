import tkinter as tk
from tkinter import ttk

from ui.widgets.searchbar import Searchbar

class UsuariosPage(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent, padding=0)

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
        frame_tabla = ttk.Frame(self)
        frame_tabla.pack(fill="both", expand=True)

        columnas = ("profesional", "matricula", "area", "estado")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings", height=8
        )

        # Encabezados
        self.tabla.heading("profesional", text="Profeesionales", anchor="w")
        self.tabla.heading("matricula", text="Matricula", anchor="w")
        self.tabla.heading("area", text="Area", anchor="w")
        self.tabla.heading("estado", text="Activo/Inactivo", anchor="center")

        # Anchos de columna
        self.tabla.column("profesional", width=220, anchor="w")
        self.tabla.column("matricula", width=120, anchor="w")
        self.tabla.column("area", width=120, anchor="w")
        self.tabla.column("estado", width=120, anchor="center")

        # Estilo morado para Activo
        self.tabla.tag_configure("activo", foreground="#6200EE")

        self.tabla.pack(fill="both", expand=True)

        # Cargar datos de prueba
        self.cargar_datos_prueba()

    def cargar_datos_prueba(self):
        datos = [
            ("Britney Lanzas", "A4738294", "AREA A", "Activo"),
            ("Raul Marian", "A4738293", "AREA B", "Activo"),
        ]

        for prof, mat, area, estado in datos:
            self.tabla.insert(
                "",
                "end",
                values=(prof, mat, area, estado),
                tags=("activo" if estado == "Activo" else "inactivo",),
            )

    def filtrar_profesionales(self, texto):
        pass