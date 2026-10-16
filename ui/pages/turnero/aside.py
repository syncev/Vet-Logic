import tkinter as tk

from ui.widgets.calendar_picker import CalendarPicker


class TurneroAside(tk.Frame):
    def __init__(
        self,
        master,
        selected_date=None,
        on_date_selected=None,
        bg="white",
        **kwargs,
    ):
        super().__init__(master, bg=bg, **kwargs)

        self.calendar_picker = CalendarPicker(
            self,
            selected_date=selected_date,
            on_date_selected=on_date_selected,
            allow_past_dates=True,
        )
        self.calendar_picker.pack(fill="x", padx=10, pady=15)

    def set_date(self, selected_date):
        self.calendar_picker.set_date(selected_date)
