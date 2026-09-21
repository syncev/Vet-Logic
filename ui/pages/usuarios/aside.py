import tkinter as tk



class UsuariosAside(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._build_widgets()
        self._build_layout()

    def _build_usuarios_menu(self):
        self._usuarios_menu = tk.Frame(
            self,
        )
        self.menu_profesionales_button = tk.Button(
            self._usuarios_menu,
            text="Profesionales",
            font=("Inter", -16),
        )
        self.menu_cambiar_contrasena_button = tk.Button(
            self._usuarios_menu,
            text="Cambiar contraseña",
            font=("Inter", -16),
        )
    def _build_widgets(self):
        self._build_usuarios_menu()

    def _build_layout(self):
        self._usuarios_menu.pack(pady=10, padx=10, fill="x")
        self.menu_profesionales_button.pack(pady=10, padx=10, fill="x")
        self.menu_cambiar_contrasena_button.pack(pady=10, padx=10, fill="x")
