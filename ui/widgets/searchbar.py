import tkinter as tk
from tkinter import ttk

class Searchbar(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._build_widgets()
        self._build_layout()
#VARIABLES
# wrapper de wdiget
    def _build_search_widget(self):
        self.search_widget = tk.Frame(
            self,
        )

    def _build_title(self):
        self.title_frame = tk.Frame(
            self.search_widget,
            width=96,
            height=30,
        )
        self.title_frame.pack_propagate(False)

        self.search_title = tk.Label(
            self.title_frame,
            text="Búsqueda",
            font=("Arial", 14, "bold"),
            fg="black",
        )

# barra de busqueda
    def _build_search(self):
        self.search_frame = tk.Frame(
            self.search_widget
            
        )
        self.search_entry = tk.Entry(
            self.search_frame,
            width=40,
        
        )
        self.search_button = tk.Button(
            self.search_frame,
                
        )
# filtros
    def _build_filter(self):
        self.filter_frame = tk.Frame(
            self.search_widget

        )
        self.filter_options = ttk.Combobox(
            self.filter_frame,
            values=[
                "Todos",
                "Cliente",
                "Paciente",
                "Especie",
                "Motivo",
                "HC",
                "Telefono"
            ],
            state="readonly",
            width=18
        )
        self.filter_options.set("Todos")
#WIDGETS
    def _build_widgets(self):
        self._build_search_widget()
        self._build_title()
        self._build_search()
        self._build_filter()

# LAYOUT
    def _build_layout(self):
        self.search_widget.pack(fill="x")

        self.title_frame.pack(
            anchor="w",
            padx=0,
            pady=(22, 0),
        )
        self.search_title.pack()
        
        self.search_frame.pack(fill="x")
        self.search_button.pack(side="left")
        self.search_entry.pack(side="left")

        self.filter_frame.pack(fill="x")
        self.filter_options.pack(side="right")
        

