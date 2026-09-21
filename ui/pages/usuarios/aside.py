import tkinter as tk


class UsuariosAside(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", **kwargs)

        self._build_widgets()
        self._build_layout()

    def _build_action_button(self, text):
        return tk.Button(
            self,
            text=text,
            bg="#F0F0F0",
            fg="#1F1F1F",
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=12,
            cursor="hand2",
            activebackground="#E0E0E0",
            activeforeground="#1F1F1F",
        )

    def _build_widgets(self):
        self.professionals_button = self._build_action_button("Profesionales")
        self.password_button = self._build_action_button("Cambiar contraseña")

    def _build_layout(self):
        self.professionals_button.pack(fill="x", padx=10, pady=(10, 6))
        self.password_button.pack(fill="x", padx=10, pady=(0, 10))