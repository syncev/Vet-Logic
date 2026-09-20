from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import tkinter as tk

from ui.widgets.searchbar import Searchbar


class TurneroPage(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._build_widgets()
        self._build_layout()
#LOGICA
#date stepper es el widget que permite cambiar de dia de 1 en 1 en el turnero
    def _build_date_stepper(self):
        self.date_stepper = tk.Frame(self)
        timezone = ZoneInfo("America/Argentina/Buenos_Aires")

        # logca para que los dias se sumen sin pasar de 31 a 32
        today = datetime.now(timezone)
        tomorrow = today + timedelta(days=1)
        next_day = today + timedelta(days=2)

        self.previous_button = tk.Button(
            self.date_stepper,
            text="<",
        )
        self.today_button = tk.Button(
            self.date_stepper,
            text=str(today.day),
        )
        self.tomorrow_button = tk.Button(
            self.date_stepper,
            text=str(tomorrow.day),
        )
        self.next_day_button = tk.Button(
            self.date_stepper,
            text=str(next_day.day),
        )
        self.next_button = tk.Button(
            self.date_stepper,
            text=">",
        )
#tabla de turnos
#WIDGETS
    def _build_widgets(self):
        #importa el searchbar que es un widget reciclable
        self.searchbar = Searchbar(self)

        self._build_date_stepper()
        
        #boton de agregar turno
        self.add_appointment_button = tk.Button(
            self,
            text="+ Agregar Turno",
        )
#LAYOUT
    def _build_layout(self):
        self.searchbar.pack(fill="x", padx=40, pady=30)
        self.date_stepper.pack()
        self.previous_button.pack(side="left")
        self.today_button.pack(side="left")
        self.tomorrow_button.pack(side="left")
        self.next_day_button.pack(side="left")
        self.next_button.pack(side="left")
        self.add_appointment_button.pack()
