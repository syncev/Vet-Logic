import tkinter as tk

import customtkinter as ctk
from screeninfo import get_monitors


# VARIABLES


# toma las dimensiones del monitor principal para que la ventana se ajuste a la pantalla
monitors = get_monitors()
principal_monitors = monitors[0]
screen_width = principal_monitors.width
screen_height = principal_monitors.height
# modifica esas dimensiones para que no sea arranque en pantalla completa
ancho = int(screen_width * 0.7)
alto = int(screen_height * 0.8)

# basicas de ventana principal
root = ctk.CTk(fg_color="white")
root.title("Vet Logic")
root.geometry(f"{ancho}x{alto}")
root.resizable(True, True)
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# WIDGETS

# titles
title = ctk.CTkLabel(
    root,
    text="Vet Logic",
    font=("Inter", 36, "bold"),
    bg_color="white",
)
subtitle = ctk.CTkLabel(
    root,
    text="Gestión veterinaria",
    font=("Inter", 16, "italic"),
    bg_color="white",
)

# input wrapper
frame_inputs = ctk.CTkFrame(
    root,
    width=725,
    height=488,
    corner_radius=10,
    fg_color="#D9D9D9",
)

# inputs
name_label = ctk.CTkLabel(
    frame_inputs,
    text="Usuario",
    font=("Inter", 32, "bold"),
)
name_entry = ctk.CTkEntry(
    frame_inputs,
    border_width=0,
    corner_radius=5,
    width=400,
    height=40,
    fg_color="white",
    placeholder_text= "JuanPerez",
)
password_label = ctk.CTkLabel(
    frame_inputs,
    text="Contraseña",
    font=("Inter", 32, "bold"),
)
password_entry = ctk.CTkEntry(
    frame_inputs,
    border_width=0,
    corner_radius=5,
    width=400,
    height=40,
    fg_color="white",
    show="*",
)

# login button

login_button = ctk.CTkButton(frame_inputs, text="Ingresar", width=400, height=66)


# LAYOUT
title.pack(pady=(75, 0))
subtitle.pack()
frame_inputs.pack(pady=(150, 0))
frame_inputs.pack_propagate(
    False
)  # Evita que el frame se ajuste al tamaño de sus hijos
name_label.pack()
name_entry.pack()
password_label.pack()
password_entry.pack()
login_button.pack()


root.mainloop()
