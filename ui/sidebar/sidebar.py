import tkinter as tk


class Sidebar(tk.Frame):
    def __init__(self, master,on_navigate, **kwargs):
        super().__init__(master, width=240, **kwargs)

        self.on_navigate = on_navigate
        self.context_view = None

        self.pack_propagate(False)
        self._build_widgets()
        self._build_layout()

    def _build_widgets(self):
        self.nav_frame = tk.Frame(
            self,
        )

        self.turnero_button = tk.Button(
            self.nav_frame,
            text="Turnero",
            command=lambda: self.on_navigate("turnero")
        )

        self.historias_button = tk.Button(
            self.nav_frame,
            text="Historias clinicas",
            command=lambda: self.on_navigate("historias")
        )

        self.usuario_button = tk.Button(
            self.nav_frame,
            text="Usuarios",
            command=lambda: self.on_navigate("usuarios")
        )

        self.context_slot = tk.Frame(
            self,
            bg="#303030"
        )

    def _build_layout(self):
        self.nav_frame.pack(
            fill="x",
            padx=12,
            pady=12,
        )
        self.turnero_button.pack(
            fill="x",
            pady=4
        )
        
        self.historias_button.pack(
            fill="x",
            pady=4
        )
        self.usuario_button.pack(
            fill="x",
            pady=4
        )
        self.context_slot.pack(
            fill="x",
            expand=True
        )

    def set_context(self,context_class):
        if self.context_view is not None:
            self.context_view.destroy()

        self.context_view = context_class(self.context_slot)
        self.context_view.pack(
            fill="both",
            expand=True,
        )