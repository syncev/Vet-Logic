import tkinter as tk
from tkinter import ttk


class UsuariosPage(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent, padding=(30, 20))

        # --- ENCABEZADO Y TÍTULO ---
        lbl_titulo = ttk.Label(
            self,
            text="Busqueda De Profesionales",
            font=("Segoe UI", 14, "bold"),
        )
        lbl_titulo.pack(anchor="w", pady=(0, 15))

        # --- BARRA DE BÚSQUEDA Y BOTÓN DE FILTROS ---
        frame_busqueda = ttk.Frame(self)
        frame_busqueda.pack(fill="x", pady=(0, 20))

        # Entrada de búsqueda estándar (sin dependencia externa)
        self.entry_buscar = ttk.Entry(frame_busqueda, font=("Segoe UI", 10))
        self.entry_buscar.insert(0, "Britney")
        self.entry_buscar.pack(
            side="left", fill="x", expand=True, ipady=3, padx=(0, 10)
        )

        # Botón Filtros
        btn_filtros = ttk.Button(frame_busqueda, text="Y  Filtros")
        btn_filtros.pack(side="right")

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