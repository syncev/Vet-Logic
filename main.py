import tkinter as tk

from screeninfo import get_monitors

root = tk.Tk()

# variables
# toma las dimensiones del monitor principal
monitores = get_monitors()
monitor_princial= monitores[0]
ancho_pantalla = monitor_princial.width
alto_pantalla = monitor_princial.height
# modifica esas dimensiones para que no sea arranque en pantalla completa
ancho = int(ancho_pantalla * 0.7)
alto = int(alto_pantalla * 0.8)

root.title("Vet Logic")
root.geometry(f"{ancho}x{alto}")
root.resizable(True, True)
root.config(bg="white")


titulo = tk.Label(
    root,
    text="Vet Logic",
    font=("Inter", 36, "bold"),
    bg="white",
)
titulo.pack()
subtitulo = tk.Label(
    root,
    text="Gestión veterinaria",
    font=("Inter", 16, "italic"),
    bg="white",
)
subtitulo.pack()

root.mainloop()
