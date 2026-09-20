import tkinter as tk

class Sidebar(tk.Frame):
    def __init__(self, master,on_navigate, **kwargs):
        super().__init__(master, width=240, bg="white", **kwargs)

        self.on_navigate = on_navigate
        self.context_view = None

        self.pack_propagate(False)
        self._build_widgets()
        self._build_layout()

    def _build_widgets(self):
        self.nav_frame = tk.Frame(
            self,
            bg="white"
        )

        self.titulo_label = tk.Label(
                    self.nav_frame,
                    text="Vet Logic",
                    font=("Arial", 18, "bold"),
                    bg="white",
                    anchor="w"
        )

        self.botones = {}

        self.turnero_button = tk.Button(
            self.nav_frame,
            text="Turnero",
            relief="flat", 
            bg="#E0E0E0",
            command=lambda: self.navegar_y_pintar("turnero", self.turnero_button)
        )
        self.botones["turnero"] = self.turnero_button

        self.historias_button = tk.Button(
            self.nav_frame,
            text="Historias clinicas",
            relief="flat",
            bg="#E0E0E0",
            command=lambda: self.navegar_y_pintar("historias", self.historias_button)
        )
        self.botones["historias"] = self.historias_button

        self.usuario_button = tk.Button(
            self.nav_frame,
            text="Usuarios",
            relief="flat",
            bg="#E0E0E0",
            command=lambda: self.navegar_y_pintar("usuarios", self.usuario_button)
        )
        self.botones["usuarios"] = self.usuario_button

        self.context_slot = tk.Frame(
            self,
            bg="white",       
            bd=0,             
            highlightthickness=0
        )


        self.botones["turnero"].config(bg="#8A2BE2", fg="white")

    def _build_layout(self):
        self.nav_frame.pack(fill="x", padx=12, pady=12)
        self.titulo_label.pack(fill="x", pady=(10, 20))

        self.turnero_button.pack(fill="x", pady=4, ipady=4)
        self.historias_button.pack(fill="x", pady=4, ipady=4)
        self.usuario_button.pack(fill="x", pady=4, ipady=4)

        separador = tk.Frame(self, bg="#E0E0E0", height=1)
        separador.pack(fill="x", padx=20, pady=15)

        self.context_slot.pack(fill="x", expand=True)

    def set_context(self, context_class):
        if self.context_view is not None:
            self.context_view.destroy()
            self.context_view = None

        if context_class is None:
            return

        self.context_view = context_class(self.context_slot)
        self.context_view.pack(
            fill="both",
            expand=True,
        )

    def navegar_y_pintar(self, page_name, button):
        self.on_navigate(page_name)

        color_base = "#E0E0E0"
        for btn in self.botones.values():
            btn.config(bg=color_base, fg="black")

        color_violeta= "#8A2BE2"
        button.config(bg=color_violeta, fg="white")
