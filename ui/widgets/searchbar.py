import tkinter as tk
from tkinter import ttk

class Searchbar(tk.Frame):
    def __init__(self, master, on_search, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(height=100)
        self.pack_propagate(False)
        
        self.on_search = on_search

        self._build_widgets()
        self._build_layout()
#VARIABLES
# wrapper de widget
    def _build_search_widget(self):
        self.search_widget = tk.Frame(
            self,
            height=100,
        )
        self.controls_frame = tk.Frame(
            self.search_widget,
            height=28,
        )
        self.controls_frame.pack_propagate(False)

# titulo
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
        )

# barra de busqueda
    def _build_search(self):
        self.search_frame = tk.Frame(
            self.controls_frame,
            height=28,
        )
        self.search_frame.pack_propagate(True)

        self.search_button_frame = tk.Frame(
            self.search_frame,
            width=28,
            height=28,
        )
        self.search_button_frame.pack_propagate (False)

        self.search_entry = tk.Entry(
            self.search_frame,
            width=40,
        )
        self.search_button = tk.Button(
            self.search_button_frame,
            text="🔍",
            relief="flat",
            bd=0,
            bg="#E0E0E0",
            fg="black",
            activebackground="#8A2BE2",
            activeforeground="white",
            font=("Arial", 14),
            command=self.search,
        )
    def search(self, event=None):
        search_text = self.search_entry.get().strip()

        self.search_button.config(
            bg="#8A2BE2",
            fg="white",
            relief="flat",
        )

        self.on_search(search_text)    
# filtros
    def _build_filter(self):
        self.filter_frame = tk.Frame(
            self.controls_frame,
            width=130,
            height=28,
        )
        self.filter_frame.pack_propagate(False)

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
            width=12
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
        self.search_widget.place(
            relx=0,
            rely=0,
            relwidth=0.5,
            relheight=1,
            anchor="nw",
        )

        self.title_frame.pack(
            anchor="w",
            padx=0,
            pady=(24, 0),
        )
        self.search_title.pack()

        self.controls_frame.pack(
            fill="x",
        )

        self.search_frame.pack(
            side="left",
            fill="x",
            expand=True,
        )
        self.search_button_frame.pack(side="left")

        self.search_button.pack(
            fill="both",
            expand=True,
        )
        self.search_entry.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(6, 0),
       )

        self.search_entry.bind("<Return>", self.search)

        self.filter_frame.pack(
            side="left",
            padx=(12, 0),
        )
        self.filter_options.pack(
            fill="both",
            expand=True,
        )
        