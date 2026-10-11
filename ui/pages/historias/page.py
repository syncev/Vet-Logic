import tkinter as tk
from tkinter import messagebox

import psycopg

from repositories.historia_repository import eliminar_historia_clinica
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
        self.delete_hc_button.pack(anchor="e", padx=10, pady=10)

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

        self.delete_hc_button = tk.Button(
            self.historia_clinica_frame,
            text="Eliminar HC",
            command=self._open_delete_hc_confirmation,
            bg="#F0F0F0",
            fg="#1F1F1F",
            relief="flat",
            cursor="hand2",
        )

    def _open_delete_hc_confirmation(self):
        hc_number = self.HC_number_label.cget("text").strip()
        if not hc_number.isdecimal() or int(hc_number) <= 0:
            messagebox.showerror(
                "HC no válida",
                "No se pudo identificar el número de la historia clínica actual.",
                parent=self.winfo_toplevel(),
            )
            return

        dialog = tk.Toplevel(self)
        dialog.title("Eliminar historia clínica")
        dialog.transient(self.winfo_toplevel())
        dialog.resizable(False, False)
        dialog.configure(bg="white")

        tk.Label(
            dialog,
            text="¡ATENCIÓN!",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(padx=24, pady=(20, 8))
        tk.Label(
            dialog,
            text=(
                "Esta acción es irreversible y eliminará la historia\n"
                f"clínica Nº {hc_number} que está abierta.\n\n"
                "¿Querés continuar?"
            ),
            justify="left",
            bg="white",
        ).pack(padx=24, pady=(0, 10))

        buttons_frame = tk.Frame(dialog, bg="white")
        buttons_frame.pack(fill="x", padx=24, pady=(0, 20))

        tk.Button(
            buttons_frame,
            text="CANCELAR",
            command=dialog.destroy,
            relief="flat",
            padx=14,
            pady=8,
        ).pack(side="left", expand=True, padx=(0, 8))
        tk.Button(
            buttons_frame,
            text="ACEPTAR",
            command=lambda: self._confirm_delete_hc(int(hc_number), dialog),
            bg="#E53935",
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
        ).pack(side="right", expand=True, padx=(8, 0))

        parent = self.winfo_toplevel()
        parent.update_idletasks()
        dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        dialog.grab_set()
        dialog.wait_visibility()

    def _confirm_delete_hc(self, hc_number, dialog):
        try:
            eliminar_historia_clinica(hc_number)
        except ValueError as error:
            messagebox.showerror(
                "No se pudo eliminar la HC",
                str(error),
                parent=dialog,
            )
            return
        except psycopg.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo eliminar la HC:\n{error}",
                parent=dialog,
            )
            return

        dialog.destroy()
        self.historia_clinica_frame.pack_forget()
        messagebox.showinfo(
            "HC eliminada",
            f"La historia clínica Nº {hc_number} fue eliminada.",
            parent=self.winfo_toplevel(),
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