import tkinter as tk


class AgregarHC(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", **kwargs)

        self._build_widgets()
        self._build_layout()

    def _build_add_hc_button(self):
        self.add_hc_button = tk.Button(
            self,
            text="+ Agregar HC",
            font=("Inter", 12, "bold"),
            bg="#A8D5BA",
            fg="#1D3525",
            bd=0,
            relief="flat",
            highlightthickness=0,
            activebackground="#96C7A4",
            activeforeground="#1D3525",
            padx=20,
            pady=12,
            cursor="hand2",
        )

    def _build_widgets(self):
        self._build_add_hc_button()

    def _build_layout(self):
        self.add_hc_button.pack(fill="x", padx=10, pady=10)
