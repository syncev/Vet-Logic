import tkinter as tk

from ui.widgets.searchbar import Searchbar
class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._build_widgets()
        self._build_layout()

    def _build_widgets(self):
        self.searchbar = Searchbar(self)

    def _build_layout(self):
        self.searchbar.pack(
            fill="x",
            padx=40,
            pady=30
        )




