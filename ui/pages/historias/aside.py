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
        self.btn_eliminar = tk.Button(
            self,
            text="⛔  Inhabilitar\nHC",
            font=("Arial", 11, "bold"),
            bg="#F7A84B",
            fg="#1F1F1F",
            relief="flat",
            bd=0,
            padx=16,
            pady=16,             # Más alto y grande
            cursor="hand2",
            command=lambda: self._select_section("eliminar_hc")
        )
   # Botón Eliminar Cliente (Rojo / Coral de la captura)
        self.btn_eliminar_cliente = tk.Button(self,
            text="⚠️  Eliminar\nCLIENTE",
            font=("Arial", 11, "bold"),
            bg="#FA5252",        # Rojo / coral de la foto
            fg="#1F1F1F",
            relief="flat",
            bd=0,
            padx=16,
            pady=16,
            cursor="hand2",
            command=lambda: self._select_section("eliminar_cliente")
        )



    def _select_section(self, section_name):
        if self.on_select_section:
            self.on_select_section(section_name)

    def _build_layout(self):
        self.btn_buscar.pack(fill="x", padx=10, pady=10)
        self.btn_nueva.pack(fill="x", padx=10, pady=10)
        self.btn_eliminar.pack(fill="x", padx=10, pady=(45 , 10))
        self.btn_eliminar_cliente.pack(fill="x", padx=10, pady=(45 , 10))