"""
Aplicación principal UMELISA TSH Neonatal.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from controllers.assay_controller import AssayController
from views.assay_view import AssayView
from views.config_view import ConfigView


class Application:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("UMELISA TSH Neonatal")
        self.app.configure(bg="#f0f0f0")
        self.app.geometry("1200x800")
        self.app.minsize(900, 700)

        self.controller = AssayController()
        self.assay_view = None
        self.config_view = None
        
        self.config = {
            "cutoff": 30.0,
            "control_lower": 20.0,
            "control_upper": 30.0,
            "calibrators": {
                "A": 0.520,
                "B": 10.750,
                "C": 25.200,
                "D": 49.850,
                "E": 96.150,
                "F": 194.000
            }
        }

        self.create_widgets()
        self.create_menu()

        self.app.mainloop()

    def create_widgets(self):
        # HEADER - solo el título, sin subtexto
        header_frame = tk.Frame(self.app, bg="#1e88e5", padx=10, pady=10)
        header_frame.pack(fill="x")

        # header_label = tk.Label(
        #     header_frame,
        #     text="UMELISA TSH Neonatal",
        #     font=("Arial", 20, "bold"),
        #     fg="white",
        #     bg="#1e88e5"
        # )
        # header_label.pack()

        # MAIN CONTENT
        self.content_frame = tk.Frame(self.app, bg="#f0f0f0")
        self.content_frame.pack(fill="both", expand=True)

        self.default_label = ttk.Label(
            self.content_frame,
            text="Bienvenido a UMELISA TSH Neonatal\nCargue un archivo .flu para comenzar",
            font=("Arial", 16)
        )
        self.default_label.pack(expand=True)

    def create_menu(self):
        menubar = tk.Menu(self.app)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Abrir placa...", command=self.open_plate)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.app.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Editar parámetros...", command=self.open_config)
        menubar.add_cascade(label="Configuración", menu=config_menu)

        self.app.config(menu=menubar)

    def open_config(self):
        if self.config_view is None or not hasattr(self.config_view, 'window') or not self.config_view.window.winfo_exists():
            self.config_view = ConfigView(self.app, self.config, self.on_config_changed)
        else:
            self.config_view.window.lift()

    def on_config_changed(self, new_config):
        self.config = new_config
        
        if self.controller.current_assay:
            self.controller.current_assay.cutoff = self.config["cutoff"]
            self.controller.current_assay.control_lower = self.config["control_lower"]
            self.controller.current_assay.control_upper = self.config["control_upper"]
            
            for cal, conc in self.config["calibrators"].items():
                if cal in self.controller.current_assay.calibrators:
                    self.controller.current_assay.calibrators[cal]["conc"] = conc
                    self.controller.current_assay.calibrators[cal]["log_conc"] = math.log10(conc) if conc > 0 else -10
            
            self.controller.current_assay._build_curve_points()
            
            current_method = self.controller.current_method
            self.controller.calculate_concentrations(current_method)
            self.controller.interpret_assay()
            
            if self.assay_view:
                self.assay_view.refresh_results()
                
            messagebox.showinfo("Configuración", "Parámetros actualizados y ensayo recalculado")

    def open_plate(self):
        filepath = filedialog.askopenfilename(
            title="Abrir archivo de placa",
            filetypes=[("Archivos de fluorescencia", "*.flu"), ("Todos los archivos", "*.*")]
        )
        
        if filepath:
            try:
                plate = self.controller.load_flu_file(filepath)
                
                assay = self.controller.new_assay(
                    plate, 
                    cutoff=self.config["cutoff"],
                    control_lower=self.config["control_lower"],
                    control_upper=self.config["control_upper"],
                    calibrators=self.config["calibrators"]
                )
                
                self.controller.calculate_concentrations("semilog_piecewise")
                self.controller.interpret_assay()
                
                self._init_assay_view(assay)
                
                messagebox.showinfo("Éxito", f"Placa cargada: {os.path.basename(filepath)}")
                
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _init_assay_view(self, assay):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Pasar el controller a la vista
        self.assay_view = AssayView(self.content_frame, assay, self.config, self.controller)
        # Mostrar curva por defecto
        self.assay_view.show_curve()


if __name__ == "__main__":
    import math
    app = Application()