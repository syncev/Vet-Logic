import tkinter as tk
from ui.widgets.searchbar import Searchbar


class HistoriasPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="white", **kwargs)

        self._build_widgets()
        self._build_layout()


    def _build_historia_clinica_card(self):
        self.historia_clinica_frame = tk.Frame(
            self, 
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
    def _build_widgets(self):
        self.searchbar = Searchbar(
            self,
            controls_relwidth=1.0,
            title_text="Búsqueda de Historia Clínica",
            )
        self._build_historia_clinica_card()
        

    def _build_layout(self):
        self.searchbar.pack(
            pady=(0, 10),
            padx=40,
            fill="x",
        )

        separador = tk.Frame(self, height=1, bg="#E0E0E0")
        separador.pack(fill="x", padx=20, pady=(0, 15))

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