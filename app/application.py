import tkinter as tk

from screeninfo import get_monitors

from ui.login_view import LoginView


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # VARIABLES

        # toma las dimensiones del monitor principal para que la ventana se ajuste a la pantalla
        monitors = get_monitors()
        principal_monitors = monitors[0]
        screen_width = principal_monitors.width
        screen_height = principal_monitors.height

        # modifica esas dimensiones para que no sea arranque en pantalla completa
        app_width = int(screen_width * 0.7)
        app_height = int(screen_height * 0.8)

        # basicas de ventana principal
        self.geometry(f"{app_width}x{app_height}")
        self.resizable(True, True)
        self.configure(bg="white")
        self.title("Vet Logic")

        # trae la funcion de login_view
        self.login_view = LoginView(
            self,
            on_login=self.show_turnero)
        
        
        self.login_view.pack()

    def show_turnero(self):
        self.login_view.destroy()
        self.turnero_view = TurneroPage(self)
        self.turnero_view.pack(fill="both", expand=True)