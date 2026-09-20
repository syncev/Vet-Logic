import tkinter as tk


class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        title = tk.Label(
            self,
            text="Turnero",
            fonr=("Inter", -32)
        )
        title.pack()