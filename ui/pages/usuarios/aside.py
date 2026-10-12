import tkinter as tk
from tkinter import messagebox

class UsuariosAside(tk.Frame):
    def __init__(self, parent, on_select_section=None, **kwargs):
        super().__init__(parent, bg="white", **kwargs)

        self.on_select_section = on_select_section
        self._build_widgets()
        self._build_layout()
        self._set_active("perfiles")  # Selecciona la sección "Perfiles" por defecto

    def _build_action_button(self, text, command):
        return tk.Button(
            self,
            text=text,
            command=command,
            bg="#F0F0F0",
            fg="#1F1F1F",
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=12,
            cursor="hand2",
            activebackground="#E0E0E0",
            activeforeground="#1F1F1F",
        )
    def _select_section(self,section):
        # Resalta la opción pulsada y avisa a la página qué vista mostrar.
        self._set_active(section)

        if self.on_select_section is not None:
            self.on_select_section(section)

    def _set_active(self, section):
        buttons = {
            "perfiles": self.profiles_button,
            "agregar_profesional": self.add_professional_button,
        }

        for name, button in buttons.items():
            selected = name == section
            button.config(
                bg="#8A2BE2" if selected else "#F0F0F0",
                fg="white" if selected else "#1F1F1F",
            )
    def _build_widgets(self):
        self.profiles_button = self._build_action_button("Perfiles", lambda: self._select_section("perfiles"))
        self.add_professional_button = self._build_action_button("Agregar Profesional", lambda: self._select_section("agregar_profesional"))

    def _build_layout(self):
        self.profiles_button.pack(fill="x", padx=10, pady=(10, 6))
        self.add_professional_button.pack(fill="x", padx=10, pady=(0, 10))
    # Botón Inhabilitar Perfil
        self.inhabilitar_button = tk.Button(
            self,
            text="INHABILITAR PERFIL",
            bg="red",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=12,
            cursor="hand2",
            command=self._abrir_modal_inhabilitar
             )

    def _build_layout(self):
        self.profiles_button.pack(fill="x", padx=10, pady=(10, 6))
        self.add_professional_button.pack(fill="x", padx=10, pady=(0, 10))
        self.inhabilitar_button.pack(fill="x", padx=10, pady=(0, 10))  # 👉 Aquí se coloca

    # Modal de confirmación

    def _abrir_modal_inhabilitar(self):
        modal = tk.Toplevel(self)
        modal.title("ATENCIÓN!!")
        modal.geometry("400x200")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        mensaje = tk.Label(
            modal,
            text="Esta acción no BORRA el PERFIL,\n"
                 "solo lo INHABILITA.\n"
                 "Puede ser recuperado posteriormente.",
            fg="red",
            font=("Arial", 12, "bold"),
            pady=20
        )
        mensaje.pack()

        botones = tk.Frame(modal)
        botones.pack(pady=20)

        cancelar_btn = tk.Button(
            botones,
            text="CANCELAR",
            bg="lightgray",
            command=modal.destroy
        )
        cancelar_btn.pack(side="left", padx=10)

        continuar_btn = tk.Button(
            botones,
            text="CONTINUAR",
            bg="red",
            fg="white",
            command=lambda: self._inhabilitar_accion(modal)
        )
        continuar_btn.pack(side="left", padx=10)

    def _inhabilitar_accion(self, modal):
        # inhabilitar perfil
        print("Perfil inhabilitado")
        messagebox.showinfo("Acción realizada", "El perfil ha sido inhabilitado.")
        modal.destroy()