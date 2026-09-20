import tkinter as tk


class HistoriasPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Título
        title = tk.Label(
            self,
            text="Historias",
            font=("Inter", -32)
        )
        title.pack()