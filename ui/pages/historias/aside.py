import tkinter as tk


class AgregarHC(tk.Frame):
    def __init__(self, parent, on_select_section=None, **kwargs):
        super().__init__(parent, bg="white", **kwargs)

        self.on_select_section = on_select_section

        self._build_widgets()
        self._build_layout()

    def _build_widgets(self):
        self.btn_buscar = tk.Button(
            self, 
            text="Buscar HC", 
            font=("Arial", 10, "bold"),
            bg="#F0F0F0", 
            fg="#1F1F1F", 
            relief="flat", 
            bd=0, 
            padx=14, 
            pady=12, 
            cursor="hand2",
          
            command=lambda: self._select_section("buscar_hc")
        )

        self.btn_nueva = tk.Button(
            self, 
            text="+ Agregar HC", 
            font=("Arial", 10, "bold"),
            bg="#D1C4E9", 
            fg="#1F1F1F", 
            relief="flat", 
            bd=0, 
            padx=14, 
            pady=12, 
            cursor="hand2",
            # 3. Usamos lambda para pasar el parámetro
            command=lambda: self._select_section("nueva_hc")
        )

    def _select_section(self, section_name):
        if self.on_select_section:
            self.on_select_section(section_name)

    def _build_layout(self):
        self.btn_buscar.pack(fill="x", padx=10, pady=10)
        self.btn_nueva.pack(fill="x", padx=10, pady=10)
