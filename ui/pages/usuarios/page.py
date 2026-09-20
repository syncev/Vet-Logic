import tkinter as tk


class UsuariosPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        title = tk.Label(
            self,
            text="Usuarios",
            font=("Inter", -32)
        )
        title.pack()