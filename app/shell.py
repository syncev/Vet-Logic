import tkinter as tk

from ui.sidebar.sidebar import Sidebar
from ui.pages.turnero.page import TurneroPage
from ui.pages.historias.page import HistoriasPage
from ui.pages.usuarios.page import UsuariosPage


class Shell(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.current_page = None

        self._build_layout()
        self._build_routes()
        self.show_page("turnero")

    def _build_layout(self):

        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_page
            )
        self.sidebar.pack(
            side="left",
            fill="y"
            )

        self.content = tk.Frame(self)
        self.content.pack(side="left", fill="both", expand=True)

    def _build_routes(self):
        self.routes = {
            "turnero": TurneroPage,
            "historias": HistoriasPage,
            "usuarios": UsuariosPage
        }
        

    def show_page(self, page_name):
        page_class = self.routes.get(page_name)

        if page_class is None:
            raise ValueError(f"Pagina no encontrada: {page_name}")

        if self.current_page is not None:
            self.current_page.destroy()

        self.current_page = page_class(
            self.content,
           
        )
        self.current_page.pack(
            fill="both",
            expand=True,
        )