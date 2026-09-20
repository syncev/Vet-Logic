import tkinter as tk


class LoginView(tk.Frame):
    def __init__(self, master,on_login, **kwargs):
        kwargs.setdefault("bg", "white")
        super().__init__(master, **kwargs)
        self.on_login = on_login
        self._build_widgets()
        self._build_layout()

        # WIDGETS

    def _build_widgets(self):
        # titles
        self.title = tk.Label(
            self,
            text="Vet Logic",
            font=("Inter", -64, "bold"),
            bg="white",
        )
        self.subtitle = tk.Label(
            self,
            text="Gestión veterinaria",
            font=("Inter", -24, "italic"),
            bg="white",
        )
        # input wrapper
        self.frame_inputs = tk.Frame(
            self,
            width=525,
            height=488,
            bg="#D9D9D9",
        )
        # inputs
        self.name_label = tk.Label(
            self.frame_inputs,
            text="Usuario",
            font=("Inter", -32, "bold"),
            bg="#D9D9D9",
        )
        self.name_entry = tk.Entry(
            self.frame_inputs,
            width=45,
            bg="white",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#CCCCCC",
            highlightcolor="#8A2BE2",
        )

        self.password_label = tk.Label(
            self.frame_inputs,
            text="Contraseña",
            font=("Inter", -32, "bold"),
            bg="#D9D9D9",
        )
        self.password_entry = tk.Entry(
            self.frame_inputs,
            width=45,
            bg="white",
            show="*",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#CCCCCC",
            highlightcolor="#8A2BE2",
        )
        # login button
        self.login_button = tk.Button(
            self.frame_inputs,
            text="Ingresar",
            width=20,
            bg="#8938D6",
            font=(
                "Inter",
                -32,
                
            ),
            fg="white",
            relief="flat",
            bd=0,
            command=self.login,
        )

        # LAYOUT

    def _build_layout(self):
        self.title.pack(pady=(75, 0))
        self.subtitle.pack()
        self.frame_inputs.pack(pady=(150, 0))
        self.frame_inputs.pack_propagate(
            False
        )  # Evita que el frame se ajuste al tamaño de sus hijos
        self.name_label.pack(pady=(77, 0))
        self.name_entry.pack()
        self.password_label.pack(pady=(31, 0))
        self.password_entry.pack()
        self.login_button.pack(pady=(78, 0))

        # LOGICA
    def login(self):
        self.on_login()