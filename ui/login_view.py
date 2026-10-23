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

         

            bg="#D9D9D9",

        )

        # inputs

        self.name_label = tk.Label(

            self.frame_inputs,

            text="Hola de nuevo!",

            font=("Inter", -32, "bold"),

            bg="#D9D9D9",

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

            command=self.login,

        )



        # LAYOUT



    def _build_layout(self):

        self.title.pack(pady=(75, 0))

        self.subtitle.pack()

        self.frame_inputs.place(
            relx=0.5,
            rely=0.58,
            anchor="center",
        )
  # Evita que el frame se ajuste al tamaño de sus hijos

        self.name_label.pack(padx=70, pady=(50, 0))
        self.login_button.pack(padx=70, pady=(40, 50))



        # LOGICA

    def login(self):

        self.on_login() 