import tkinter as tk
from ui.widgets.searchbar import Searchbar


class HistoriasPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._build_widgets()
        self._build_layout()



    def _build_widgets(self):
        self.searchbar = Searchbar(self)

    def _build_layout(self):
        self.searchbar.pack(pady=10, padx=10, fill="x")