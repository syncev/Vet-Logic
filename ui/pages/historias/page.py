import tkinter as tk
from ui.widgets.searchbar import Searchbar


class HistoriasPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", **kwargs)

        self.search_view = tk.Frame(self, bg="white")
        self.add_hc_view = tk.Frame(self, bg="white")

        self._build_search_view()
        self._build_add_hc_view()

        self.show_section("buscar_hc")

    def show_section(self, section):
        self.search_view.pack_forget()
        self.add_hc_view.pack_forget()

        if section == "buscar_hc":
            self.search_view.pack(fill="both", expand=True)
        elif section == "nueva_hc":
            self.add_hc_view.pack(fill="both", expand=True)
        else:
            raise ValueError(f"Sección de Historias desconocida: {section}")

    def _build_search_view(self):
        self.searchbar = Searchbar(
            self.search_view,
            controls_relwidth=1.0,
            title_text="Búsqueda de Historia Clínica",
        )
        self.searchbar.pack(pady=(0, 10), padx=40, fill="x")

        separador = tk.Frame(self.search_view, height=1, bg="#E0E0E0")
        separador.pack(fill="x", padx=20, pady=(0, 15))

        self._build_historia_clinica_card()

        self.historia_clinica_frame.pack(pady=(30, 10), padx=10, fill="x")
        self.hc_header_frame.pack(pady=5, padx=5, fill="x")
        self.HC_title_label.pack(side="left")
        self.HC_number_label.pack(side="left", padx=5)
        self.HC_client_label.pack(pady=5, padx=5, fill="x")
        self.hc_patient_info_frame.pack(pady=5, padx=5, fill="x")
        self.patient_name_label.pack(side="left", padx=5)
        self.patient_species_label.pack(side="left", padx=5)
        self.patient_age_label.pack(side="left", padx=5)
        self.patient_sex_label.pack(side="left", padx=5)
        self.patient_neutered_label.pack(side="left", padx=5)
        self.patient_weight_label.pack(side="left", padx=5)

    def _build_historia_clinica_card(self):
        self.historia_clinica_frame = tk.Frame(
            self.search_view,
            bg="white",
            highlightbackground="#E0E0E0",
            highlightthickness=1

        )
#contiene el numero y cliente de HC
        self.hc_header_frame = tk.Frame(self.historia_clinica_frame, bg="white")

        self.HC_title_label = tk.Label(
            self.hc_header_frame,
            text="Historia Clínica Nº",
            font=("Inter", -24, "bold"),
            bg="white"
        )
        self.HC_number_label = tk.Label(
            self.hc_header_frame,
            text="123456",
            font=("Inter", -24),
            bg="white"
        )
        self.HC_client_label = tk.Label(
            self.historia_clinica_frame,
            text="Cliente: Juan Pérez",
            font=("Inter", -16),
            bg="white"
        )
#contiene datos principales del paciente
        self.hc_patient_info_frame = tk.Frame(self.historia_clinica_frame, bg="white")

        self.patient_name_label = tk.Label(
            self.hc_patient_info_frame,
            text="Paciente: Fido",
            font=("Inter", -16),
            bg="white"
        )
        self.patient_species_label = tk.Label(
            self.hc_patient_info_frame,
            text="Especie: Canino",
            font=("Inter", -16),
            bg="white"
        )
        self.patient_age_label = tk.Label(
            self.hc_patient_info_frame,
            text="Edad: 5 años",
            font=("Inter", -16),
            bg="white"
        )
        self.patient_sex_label = tk.Label(
            self.hc_patient_info_frame,
            text="Sexo: Macho",
            font=("Inter", -16),
            bg="white"
        )   
        self.patient_neutered_label = tk.Label(
            self.hc_patient_info_frame,
            text="Castrado: Sí",
            font=("Inter", -16),
            bg="white"
        )
        self.patient_weight_label = tk.Label(
            self.hc_patient_info_frame,
            text="Peso: 20 kg",
            font=("Inter", -16),
            bg="white"
        )
    def _build_add_hc_view(self):
        header_frame = tk.Frame(self.add_hc_view, bg="white")
        header_frame.pack(fill="x", padx=40, pady=(20, 10))

        tk.Label(header_frame, text="Nueva Hist. Clínica - Nº ", font=("Arial", 16, "bold"), bg="white").pack(side="left")
        tk.Label(header_frame, text="65223", font=("Arial", 16, "bold"), bg="#D1C4E9", padx=10).pack(side="left")

        self.btn_guardar = tk.Button(header_frame, text="💾 Guardar", font=("Arial", 12), relief="flat", bg="#A8D5BA", cursor="hand2")
        self.btn_guardar.pack(side="right")

        bg_green = "#C8E6C9"
        form_frame = tk.Frame(self.add_hc_view, bg=bg_green, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True, padx=40, pady=10)

        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_dni = tk.StringVar()

        tk.Label(form_frame, text="Datos del Cliente", font=("Arial", 10, "bold"), bg=bg_green).grid(row=0, column=0, sticky="w", pady=(0, 10))

        tk.Label(form_frame, text="Nombre", bg=bg_green).grid(row=1, column=0, sticky="e", padx=5)
        tk.Entry(form_frame, textvariable=self.var_nombre).grid(row=1, column=1, sticky="ew", padx=5)

        tk.Label(form_frame, text="Apellido", bg=bg_green).grid(row=1, column=2, sticky="e", padx=5)
        tk.Entry(form_frame, textvariable=self.var_apellido).grid(row=1, column=3, sticky="ew", padx=5)

        tk.Label(form_frame, text="DNI", bg=bg_green).grid(row=1, column=4, sticky="e", padx=5)
        tk.Entry(form_frame, textvariable=self.var_dni).grid(row=1, column=5, sticky="ew", padx=5)

        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
        form_frame.grid_columnconfigure(5, weight=1)

        tk.Label(form_frame, text="Tratamiento", bg=bg_green, font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=6, pady=(20, 5))
        self.caja_tratamiento = tk.Text(form_frame, height=8)
        self.caja_tratamiento.grid(row=3, column=0, columnspan=6, sticky="ew", padx=5)