from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import tkinter as tk

class HorariosSelector(tk.Frame):
    HORARIOS = (
        "09:00",
        "09:40",
        "10:20",
        "11:00",
        "11:40",
        "12:20",
        "16:00",
        "16:40",
        "17:20",
        "18:00",
        "18:40",
        "19:20",
    )

    def __init__(
        self,
        master,
        fecha_base: date,
        horarios_ocupados=None,
        on_fecha_base_change=None,
        on_horario_seleccionado=None,
        **kwargs,
    ):
        kwargs.setdefault("bg", "white")
        super().__init__(master, **kwargs)

        self.fecha_base = fecha_base
        self.horario_seleccionado = None
        self.horarios_ocupados = (
            horarios_ocupados if horarios_ocupados is not None else set()
        )
        self.on_fecha_base_change = on_fecha_base_change
        self.on_horario_seleccionado = on_horario_seleccionado
        self._build_grid()

    def actualizar_datos(self, fecha_base: date, horarios_ocupados):
        self.fecha_base = fecha_base
        self.horarios_ocupados = set(horarios_ocupados)
        self._render_grid()

    def _build_grid(self):
        self.navigation_frame = tk.Frame(self, bg="white")
        self.navigation_frame.pack(fill="x")

        tk.Button(
            self.navigation_frame,
            text="<",
            bg="#E0E0E0",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Arial", 14, "bold"),
            width=3,
            height=2,
            command=lambda: self._move_days(-1),
        ).pack(side="left")

        tk.Button(
            self.navigation_frame,
            text=">",
            bg="#E0E0E0",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Arial", 14, "bold"),
            width=3,
            height=2,
            command=lambda: self._move_days(1),
        ).pack(side="right")

        self.grid_frame = tk.Frame(self, bg="white")
        self.grid_frame.pack(fill="both", expand=True)

        self._render_grid()

    def _render_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        current_minutes = now.hour * 60 + now.minute

        for day_offset in range(3):
            day = self.fecha_base + timedelta(days=day_offset)
            day_frame = tk.Frame(self.grid_frame, bg="white")
            day_frame.grid(row=0, column=day_offset, padx=6, sticky="nsew")
            self.grid_frame.columnconfigure(day_offset, weight=1)

            tk.Label(
                day_frame,
                text=day.strftime("%d/%m"),
                bg="#FCE4E4" if day == now.date() else "white",
                font=("Arial", 12, "bold"),
                anchor="center",
                relief="solid",
                bd=1,
            ).pack(fill="x", pady=4, ipady=2)

            for hour in self.HORARIOS:
                hour_frame = tk.Frame(day_frame, bg="white")
                hour_frame.pack(fill="x")

                tk.Label(
                    hour_frame,
                    text=hour,
                    font=("Arial", 11),
                    bg="white",
                    width=6,
                ).pack(side="left")

                occupied = (day, hour) in self.horarios_ocupados
                hour_minutes = int(hour[:2]) * 60 + int(hour[3:])
                past = day < now.date() or(
                    day == now.date() and hour_minutes <= current_minutes
                )
                available = not occupied and not past
                selected = self.horario_seleccionado == (day, hour)

                tk.Button(
                    hour_frame,
                    text="+" if available and not selected else "",
                    bg="#BDBDBD" if selected else (
                        "#61D161"if available else "#999999"
                    ),
                    state=tk.NORMAL if available else tk.DISABLED,
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    font=("Arial", 14, "bold"),
                    fg="white",
                    command=lambda select_day=day, select_hour=hour:
                        self._select_slot(select_day, select_hour),
                ).pack(side="right", fill="x", expand=True, padx=2, pady=1, ipady=2)

    def _move_days(self, amount):
        self.fecha_base += timedelta(days=amount)

        if self.on_fecha_base_change is not None:
            self.on_fecha_base_change(self.fecha_base)

        self._render_grid()

    def _select_slot(self, day, hour):
        self.horario_seleccionado = (day, hour)
        self._render_grid()

        if self.on_horario_seleccionado is not None:
            self.on_horario_seleccionado(day, hour)
