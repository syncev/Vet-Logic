import datetime
import tkinter as tk


class TurneroAside(tk.Frame):
    def __init__(self, master, bg="white", **kwargs):
        super().__init__(master, bg="white", **kwargs)
        self._build_calendar()

    def _build_calendar(self):
        calendar_frame = tk.Frame(self, bg="white")
        calendar_frame.pack(fill="x", padx=10, pady=15)

        for column in range(7):
            calendar_frame.columnconfigure(column, weight=1)

        days = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
        for column, day in enumerate(days):
            tk.Label(
                calendar_frame,
                text=day,
                font=("Arial", 9, "bold"),
                bg="white",
                fg="#777777",
            ).grid(row=0, column=column, padx=1, pady=2, sticky="n")

        month_days = [
            ["", "", 1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10, 11, 12],
            [13, 14, 15, 16, 17, 18, 19],
            [20, 21, 22, 23, 24, 25, 26],
            [27, 28, 29, 30, 31, "", ""],
        ]

        current_day = datetime.date.today().day
        for row, week in enumerate(month_days, start=1):
            for column, day_number in enumerate(week):
                selected = day_number == current_day
                background = "#8A2BE2" if selected else "white"
                foreground = "white" if selected else "#333333"

                tk.Label(
                    calendar_frame,
                    text=str(day_number) if day_number != "" else "",
                    font=("Arial", 9, "bold" if selected else "normal"),
                    bg=background,
                    fg=foreground,
                    width=2,
                    anchor="center",
                ).grid(row=row, column=column, padx=1, pady=1, sticky="n")
