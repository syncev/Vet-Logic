import tkinter as tk
from tkinter import messagebox

import psycopg

from app.application import App
from core.db import conectar


def main() -> int:
    try:
        with conectar():
            pass
    except (FileNotFoundError, KeyError, OSError, ValueError, psycopg.Error) as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "No se pudo conectar a PostgreSQL",
            "Vet Logic no puede iniciar sin una base de datos disponible.\n\n"
            "Verifique que PostgreSQL esté iniciado y que las credenciales "
            "sean correctas. Si es la primera instalación, ejecute "
            "python setup_database.py.\n\n"
            f"Detalle: {error}",
            parent=root,
        )
        root.destroy()
        return 1

    app = App()
    app.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
