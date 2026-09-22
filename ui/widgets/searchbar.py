import tkinter as tk
from tkinter import ttk

class Searchbar(tk.Frame):
    def __init__(
        self,
        master,
        on_search=None,
        controls_relwidth=0.85,
        title_text="Búsqueda",
        filter_values=None,
        **kwargs
    ):
        super().__init__(master, bg="white", **kwargs)

        self.on_search = on_search
        self.controls_relwidth = controls_relwidth
        self.title_text = title_text
        self.filter_values = filter_values or [
            "Todos",
            "Cliente",
            "Paciente",
            "Especie",
            "Motivo",
            "HC",
            "Telefono",
        ]

        self._build_widgets()
        self._build_layout()
#VARIABLES
# wrapper de wdiget
    def _build_search_widget(self):
        self.search_widget = tk.Frame(
            self,
            height=80,
            bg="white",
        )
        self.search_widget.pack_propagate(False)

        self.controls_frame = tk.Frame(
            self.search_widget,
            height=28,
            bg="white",
        )
        self.controls_frame.pack_propagate(False)

    def _build_title(self):
        self.title_frame = tk.Frame(
            self.search_widget,
            height=30,
            bg="white",
        )

        self.search_title = tk.Label(
            self.title_frame,
            text=self.title_text,
            font=("Arial", 14, "bold"),
            fg="black",
            bg="white",
            anchor="w",
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
        self.search_button_frame.pack_propagate(False)
        
        self.search_entry = tk.Entry(
            self.search_frame,
            width=40,
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search(),
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
            command=self.search,
        )

    def search(self):
        self.search_button.config(
            bg="#8A2BE2",
            fg="white",
        )

        query = self.search_entry.get().strip()
        selected_filter = self.filter_options.get()

        if self.on_search is not None:
            self.on_search(query, selected_filter)

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
            values=self.filter_values,
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
        self.search_title.pack(
            anchor="w",
        )

        self.controls_frame.place(
            relx=0,
            rely=0,
            relwidth=self.controls_relwidth,
            y=52,
            height=28,
        )

        self.controls_frame.columnconfigure(
            1,
            weight=1,
        )

        self.search_frame.grid(
            row=0,
            column=1,
            padx=(0, 8),
            sticky="ew",
        )

        self.filter_frame.grid(
            row=0,
            column=2,
            sticky="nsew",
        )

        self.search_button_frame.pack(
            side="left",
            padx=(0, 8),
        )
        
        self.search_button.pack(
            fill="both",
            expand=True,
        )

        self.search_entry.pack(
            fill="both",
            expand=True,
        )
        
        self.filter_options.pack(
            fill="both",
            expand=True,
        )

