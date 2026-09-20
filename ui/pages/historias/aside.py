import tkinter as tk


class AgregarHC(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._build_widgets()
        self._build_layout()


    def _build_widgets(self):
        self._agregar_hc_button = tk.Button(
            self,
            text="+ Agregar HC",
            font=("Inter", -24),
        )

    def _build_layout(self):
        self._agregar_hc_button.pack(pady=10, padx=10, fill="x")
