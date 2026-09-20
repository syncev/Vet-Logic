import tkinter as tk

from ui.widgets.searchbar import Searchbar
class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._build_widgets()
        self._build_layout()

    def _build_widgets(self):
        self.searchbar = Searchbar(
            self,
            on_search=self.search_turnos,
            )
    def search_turnos(self, search_text):
        print(f"Texto buscado: {search_text}")

    def _build_layout(self):
        self.searchbar.pack(
            fill="x",
            padx=40,
            pady=(0, 30),
        )




