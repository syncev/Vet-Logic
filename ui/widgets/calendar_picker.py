import calendar
import tkinter as tk
from datetime import date


class CalendarPicker(tk.Frame):
    MONTHS = (
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    )

    def __init__(
        self,
        master,
        selected_date=None,
        on_date_selected=None,
        **kwargs,
    ):
        kwargs.setdefault("bg", "#F4F4F5")
        kwargs.setdefault("padx", 12)
        kwargs.setdefault("pady", 10)
        super().__init__(master, **kwargs)

        self.selected_date = selected_date or date.today()
        self.current_month = self.selected_date.replace(day=1)
        self.on_date_selected = on_date_selected

        self._build_widgets()
        self._render()

    def _build_widgets(self):
        navigation = tk.Frame(self, bg="#F4F4F5")
        navigation.pack(fill="x", pady=(0, 8))

        tk.Button(
            navigation,
            text="‹",
            width=3,
            relief="flat",
            command=lambda: self._change_month(-1),
        ).pack(side="left")

        self.month_label = tk.Label(
            navigation,
            text="",
            bg="#F4F4F5",
            font=("Arial", 11, "bold"),
        )
        self.month_label.pack(side="left", expand=True)

        tk.Button(
            navigation,
            text="›",
            width=3,
            relief="flat",
            command=lambda: self._change_month(1),
        ).pack(side="right")

        self.days_frame = tk.Frame(self, bg="#F4F4F5")
        self.days_frame.pack()

    def set_date(self, selected_date):
        self.selected_date = selected_date
        self.current_month = selected_date.replace(day=1)
        self._render()

    def _render(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        month_name = self.MONTHS[self.current_month.month - 1]
        self.month_label.configure(
            text=f"{month_name} {self.current_month.year}"
        )

        weekdays = ("Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do")
        for column, name in enumerate(weekdays):
            tk.Label(
                self.days_frame,
                text=name,
                width=4,
                bg="#F4F4F5",
                font=("Arial", 9, "bold"),
            ).grid(row=0, column=column, padx=2, pady=2)

        weeks = calendar.Calendar(
            firstweekday=calendar.MONDAY
        ).monthdayscalendar(
            self.current_month.year,
            self.current_month.month,
        )

        for row, week in enumerate(weeks, start=1):
            for column, day in enumerate(week):
                if day == 0:
                    continue

                day_date = self.current_month.replace(day=day)
                selected = day_date == self.selected_date

                tk.Button(
                    self.days_frame,
                    text=str(day),
                    width=3,
                    relief="flat",
                    bg="#F5BFC2" if selected else "white",
                    font=("Arial", 9, "bold" if selected else "normal"),
                    state=tk.DISABLED if day_date < date.today() else tk.NORMAL,
                    command=lambda selected_day=day: self._select_day(
                        selected_day
                    ),
                ).grid(row=row, column=column, padx=2, pady=2)

    def _select_day(self, day):
        self.selected_date = self.current_month.replace(day=day)
        self._render()

        if self.on_date_selected is not None:
            self.on_date_selected(self.selected_date)

    def _change_month(self, offset):
        month_index = self.current_month.month - 1 + offset
        year = self.current_month.year + month_index // 12
        month = month_index % 12 + 1

        self.current_month = date(year, month, 1)
        self._render()