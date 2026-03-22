"""
Vista para el ensayo UMELISA TSH Neonatal.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import numpy as np
import pandas as pd
from datetime import datetime
from scipy import interpolate


class AssayView:
    """Vista principal para mostrar la placa y resultados del ensayo TSH."""

    def __init__(self, root, assay, config, controller=None):
        self.root = root
        self.assay = assay
        self.config = config
        self.controller = controller

        # Frame principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Barra de herramientas
        self._create_toolbar()

        # Área de contenido dinámico
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Mostrar validación inicial
        self._check_validation()

    def _create_toolbar(self):
        """Crea la barra de herramientas con botones."""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Ver Placa", 
                   command=self.show_plate).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Ver Resultados", 
                   command=self.show_results).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Ver Curva", 
                   command=self.show_curve).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Menú de métodos
        ttk.Label(toolbar, text="Método:").pack(side=tk.LEFT, padx=(5, 2))
        self.method_var = tk.StringVar(value=self.assay.current_method)
        method_combo = ttk.Combobox(toolbar, textvariable=self.method_var,
                                    values=self.assay.AVAILABLE_METHODS,
                                    width=22, state="readonly")
        method_combo.pack(side=tk.LEFT, padx=2)
        method_combo.bind("<<ComboboxSelected>>", self.on_method_change)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Menú de exportación
        export_btn = ttk.Menubutton(toolbar, text="Exportar")
        export_btn.pack(side=tk.LEFT, padx=2)

        export_menu = tk.Menu(export_btn, tearoff=0)
        export_menu.add_command(label="Exportar Placa (CSV)", 
                                command=self.export_plate_csv)
        export_menu.add_command(label="Exportar Resultados (CSV)", 
                                command=self.export_results_csv)
        export_menu.add_command(label="Exportar Curva (CSV)", 
                                command=self.export_curve_csv)
        export_menu.add_separator()
        export_menu.add_command(label="Guardar Curva como PNG", 
                                command=self.save_curve_as_png)
        export_menu.add_command(label="Guardar Tabla como HTML", 
                                command=self.save_results_as_html)
        export_btn.config(menu=export_menu)

    # ============================================================
    #   EXPORTACIONES
    # ============================================================

    def export_plate_csv(self):
        """Exporta los valores de la placa a un archivo CSV."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"placa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not filename:
            return

        rows = "ABCDEFGH"
        cols = range(1, 13)

        data = []
        for row in rows:
            row_data = []
            for col in cols:
                well_id = f"{row}{col}"
                value = self.assay.plate.get_well_value(well_id)
                row_data.append(value)
            data.append(row_data)

        df = pd.DataFrame(data, index=list(rows), columns=[str(c) for c in cols])
        df.to_csv(filename)
        messagebox.showinfo("Exportar", f"Placa exportada a:\n{filename}")

    def export_results_csv(self):
        """Exporta los resultados a un archivo CSV."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not filename:
            return

        results = []
        for i, sample in enumerate(self.assay.samples, 1):
            results.append({
                "N": i,
                "Código": "",
                "Fluor1": f"{sample['fluor1']:.2f}",
                "Fluor2": f"{sample['fluor2']:.2f}",
                "Media": f"{sample['mean_fluor']:.2f}",
                "mUVL": f"{sample['concentration']:.2f}" if sample['concentration'] is not None else "-",
                "Resultado": sample['interpretation'] if sample['interpretation'] else ""
            })

        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)
        messagebox.showinfo("Exportar", f"Resultados exportados a:\n{filename}")

    def export_curve_csv(self):
        """Exporta los puntos de la curva de calibración a CSV."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"curva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not filename:
            return

        data = []
        for p in self.assay.curve_points:
            data.append({
                "Concentracion_mUIL": p["conc"],
                "Fluorescencia": p["fluor"]
            })

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        messagebox.showinfo("Exportar", f"Curva exportada a:\n{filename}")

    def save_curve_as_png(self):
        """Guarda la curva actual como imagen PNG."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"curva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        if not filename:
            return

        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        self._plot_curve(ax)
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(fig)
        messagebox.showinfo("Exportar", f"Curva guardada como:\n{filename}")

    def save_results_as_html(self):
        """Guarda la tabla de resultados como archivo HTML."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialfile=f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        if not filename:
            return

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Resultados UMELISA TSH Neonatal</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background-color: #f2f2f2; }}
        .elevado {{ background-color: #ADD8E6; }}
        .repetir {{ background-color: #FFFF00; }}
        .ult-punto {{ background-color: #C0C0C0; }}
    </style>
</head>
<body>
    <h1>UMELISA TSH Neonatal - Resultados</h1>
    <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Método:</strong> {self.assay.current_method}</p>
    <p><strong>Punto de corte:</strong> {self.assay.cutoff} mUI/L</p>
    <p><strong>Validación curva:</strong> {self.assay.get_calibration_status()}</p>
    <p><strong>Validación control:</strong> {self.assay.get_control_status()}</p>
     <table>
        <thead>
            <tr><th>N.</th><th>Código</th><th>Fluor1</th><th>Fluor2</th><th>Media</th><th>mUVL (mUI/L)</th><th>Resultado</th>\
        </thead>
        <tbody>
"""

        for i, sample in enumerate(self.assay.samples, 1):
            conc_str = f"{sample['concentration']:.2f}" if sample['concentration'] is not None else "-"
            result = sample['interpretation'] if sample['interpretation'] else ""
            row_class = ""
            if result == "Elevado":
                row_class = "elevado"
            elif result == "Repetir":
                row_class = "repetir"
            elif result == "> Ult. Punto":
                row_class = "ult-punto"

            html_content += f"""
            <tr class="{row_class}">
                 <td>{i}</td>
                 <td></td>
                 <td>{sample['fluor1']:.2f}</td>
                 <td>{sample['fluor2']:.2f}</td>
                 <td>{sample['mean_fluor']:.2f}</td>
                 <td>{conc_str}</td>
                 <td>{result}</td>
             </tr>"""

        html_content += """
        </tbody>
     </table>
</body>
</html>"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        messagebox.showinfo("Exportar", f"Resultados guardados como HTML:\n{filename}")

    # ============================================================
    #   MÉTODOS DE VISTA
    # ============================================================

    def refresh_results(self):
        if hasattr(self, 'content_frame'):
            self.show_results()

    def on_method_change(self, event):
        if self.controller:
            self.controller.calculate_concentrations(self.method_var.get())
            self.controller.interpret_assay()
            self.assay = self.controller.current_assay
            # Por defecto mostrar curva al cambiar método
            self.show_curve()

    def show_plate(self):
        self._clear_content()
        self._show_plate_grid()

    def show_results(self):
        self._clear_content()
        self._show_validation_panel()
        self._show_results_table()

    def show_curve(self):
        self._clear_content()
        self._show_curve_plot()

    # ============================================================
    #   MÉTODOS PRIVADOS DE VISUALIZACIÓN
    # ============================================================

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _check_validation(self):
        if not self.assay.valid:
            messagebox.showwarning("Validación", self.assay.validation_message)

    def _show_validation_panel(self):
        valid_frame = tk.Frame(self.content_frame, bg="#f0f0f0", relief="ridge", bd=2)
        valid_frame.pack(fill="x", padx=20, pady=5)

        cal_status = self.assay.get_calibration_status()
        ctrl_status = self.assay.get_control_status()

        color_cal = "green" if self.assay.calibration_valid else "red"
        color_ctrl = "green" if self.assay.control_valid else "red"

        tk.Label(valid_frame, text=cal_status, fg=color_cal,
                 font=("Arial", 9, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10, pady=2)
        tk.Label(valid_frame, text=ctrl_status, fg=color_ctrl,
                 font=("Arial", 9, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10, pady=2)

        if not self.assay.control_valid and not (self.assay.control_lower == 0 and self.assay.control_upper == 0):
            warning_frame = tk.Frame(self.content_frame, bg="#FFE4E1", relief="ridge", bd=2)
            warning_frame.pack(fill="x", padx=20, pady=5)
            tk.Label(warning_frame,
                     text="⚠ CONTROL FUERA DE RANGO - Resultados mostrados solo como referencia",
                     fg="red", font=("Arial", 10, "bold"), bg="#FFE4E1").pack(pady=5)

    def _show_results_table(self):
        table_frame = ttk.Frame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("N.", "Código", "Fluor1", "Fluor2", "Media", "mUVL...", "Resultado")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                            yscrollcommand=scrollbar.set, height=20)
        scrollbar.config(command=tree.yview)

        col_widths = [40, 60, 70, 70, 70, 80, 100]
        for col, width in zip(columns, col_widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        tree.tag_configure("elevado", background="#ADD8E6")
        tree.tag_configure("repetir", background="#FFFF00")
        tree.tag_configure("ult_punto", background="#C0C0C0")
        tree.tag_configure("negativo", background="#FFFFFF")

        for i, sample in enumerate(self.assay.samples, 1):
            conc_str = f"{sample['concentration']:.2f}" if sample['concentration'] is not None else "-"

            if sample["interpretation"] == "Elevado":
                tag = "elevado"
            elif sample["interpretation"] == "Repetir":
                tag = "repetir"
            elif sample["interpretation"] == "> Ult. Punto":
                tag = "ult_punto"
                conc_str = "-"
            else:
                tag = "negativo"

            tree.insert("", tk.END, values=(
                i, "",
                f"{sample['fluor1']:.2f}",
                f"{sample['fluor2']:.2f}",
                f"{sample['mean_fluor']:.2f}",
                conc_str,
                sample["interpretation"] if sample["interpretation"] else ""
            ), tags=(tag,))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _show_curve_plot(self):
        method_names = {
            "linear_piecewise": "Lineal punto a punto",
            "semilog_piecewise": "Semilog (A-B lineal, resto log)",
            "linear_extrapolation": "Lineal con extrapolación",
            "polynomial_degree2": "Polinomial grado 2",
            "polynomial_degree3": "Polinomial grado 3",
            "cubic_spline": "Spline cúbico",
            "akima_spline": "Akima spline",
            "model_4pl": "Modelo 4PL",
            "model_5pl": "Modelo 5PL"
        }
        
        ttk.Label(self.content_frame,
                  text=f"Curva de Calibración - Método: {method_names.get(self.assay.current_method, self.assay.current_method)}",
                  font=("Arial", 14, "bold")).pack(pady=10)

        fig_frame = ttk.Frame(self.content_frame)
        fig_frame.pack(fill="both", expand=True, padx=20, pady=10)

        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        self._plot_curve(ax)

        canvas = FigureCanvasTkAgg(fig, master=fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _plot_curve(self, ax):
        """Dibuja la curva en el eje proporcionado."""
        x_conc = np.array([p["conc"] for p in self.assay.curve_points])
        y_fluor = np.array([p["fluor"] for p in self.assay.curve_points])
        
        # Último calibrador
        last_calib_conc = max(x_conc)
        first_calib_conc = min(x_conc)
        max_fluor = max(y_fluor)
        
        # Obtener ticks dinámicos de los calibradores
        calibrator_ticks = [p["conc"] for p in self.assay.curve_points]
        
        # Limitar eje X a [0, 200] o hasta el último calibrador si es menor
        x_max_display = min(200, last_calib_conc * 1.05)
        
        # Graficar puntos de calibradores
        ax.plot(x_conc, y_fluor, 'bo', markersize=8, label="Calibradores")
        
        # Generar curva suave
        if len(x_conc) >= 2:
            method = self.assay.current_method
            
            # ============================================================
            # MÉTODOS CON ESCALA LINEAL EN X (todos excepto semilog)
            # ============================================================
            if method != "semilog_piecewise":
                # Generar puntos desde 0 hasta x_max_display
                x_smooth = np.linspace(0, x_max_display, 500)
                
                if method in ["linear_piecewise", "linear_extrapolation"]:
                    y_smooth = np.interp(x_smooth, x_conc, y_fluor)
                    
                elif method in ["polynomial_degree2", "polynomial_degree3"]:
                    deg = 2 if method == "polynomial_degree2" else 3
                    coeffs = np.polyfit(x_conc, y_fluor, deg)
                    y_smooth = np.polyval(coeffs, x_smooth)
                    
                elif method in ["cubic_spline", "akima_spline"]:
                    if method == "cubic_spline":
                        spline = interpolate.CubicSpline(x_conc, y_fluor, extrapolate=False)
                    else:
                        spline = interpolate.Akima1DInterpolator(x_conc, y_fluor)
                    y_smooth = spline(x_smooth)
                    
                elif method in ["model_4pl", "model_5pl"]:
                    params = self.assay.fit_params
                    if "4pl_params" in params and method == "model_4pl":
                        p = params["4pl_params"]
                        y_smooth = p["D"] + (p["A"] - p["D"]) / (1 + (p["C"] / x_smooth) ** p["B"])
                    elif "5pl_params" in params and method == "model_5pl":
                        p = params["5pl_params"]
                        y_smooth = p["D"] + (p["A"] - p["D"]) / (1 + (p["C"] / x_smooth) ** p["B"]) ** p["F"]
                    else:
                        y_smooth = np.interp(x_smooth, x_conc, y_fluor)
                else:
                    y_smooth = np.interp(x_smooth, x_conc, y_fluor)
                
                # Extrapolación hacia 0
                idx_below = x_smooth < first_calib_conc
                if np.any(idx_below):
                    y_smooth[idx_below] = y_fluor[0] * (x_smooth[idx_below] / first_calib_conc)
                
                y_smooth = np.maximum(y_smooth, 0)
                
                ax.plot(x_smooth, y_smooth, 'r-', linewidth=2, alpha=0.7)
                ax.set_xscale('linear')
                ax.set_xlim([0, x_max_display])
                
            # ============================================================
            # MÉTODO SEMILOG (escala logarítmica)
            # ============================================================
            else:
                # Generar puntos en escala logarítmica desde 0.01 hasta x_max_display
                x_smooth = np.logspace(np.log10(0.05), np.log10(x_max_display), 500)
                log_x_conc = np.log10(x_conc)
                log_x_smooth = np.log10(x_smooth)
                y_smooth = np.interp(log_x_smooth, log_x_conc, y_fluor)
                
                # Extrapolación hacia valores bajos
                idx_below = x_smooth < first_calib_conc
                if np.any(idx_below):
                    y_smooth[idx_below] = y_fluor[0] * (x_smooth[idx_below] / first_calib_conc)
                
                y_smooth = np.maximum(y_smooth, 0)
                
                ax.plot(x_smooth, y_smooth, 'r-', linewidth=2, alpha=0.7)
                ax.set_xscale('log')
                ax.set_xlim([0.01, x_max_display])
        
        # Configurar ticks del eje X (dinámicos según calibradores)
        ax.set_xticks(calibrator_ticks)
        ax.set_xticklabels([f"{tick:.2f}" for tick in calibrator_ticks], rotation=45)
        
        # Marcar punto de corte
        cutoff_fluor = self._find_fluorescence_at_cutoff()
        if cutoff_fluor and self.assay.cutoff <= last_calib_conc:
            ax.axhline(y=cutoff_fluor, color='g', linestyle='--', alpha=0.7,
                       linewidth=2, label=f'Corte {self.assay.cutoff} mUI/L')
        
        # Marcar último punto (F)
        if len(y_fluor) > 0:
            ax.axhline(y=y_fluor[-1], color='gray', linestyle=':', alpha=0.7,
                       linewidth=2, label='Último punto (F)')
            ax.plot(last_calib_conc, y_fluor[-1], 'ks', markersize=10,
                    markerfacecolor='none', markeredgecolor='gray', markeredgewidth=2)
        
        # Configurar límites del eje Y
        y_max = max_fluor * 1.15
        ax.set_ylim([0, y_max])
        
        ax.set_xlabel("Concentración (mUI/L)")
        ax.set_ylabel("Fluorescencia")
        ax.set_title("Curva de Calibración")
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best', fontsize=9)
    
    def _find_fluorescence_at_cutoff(self):
        """Encuentra la fluorescencia aproximada para el punto de corte."""
        if not self.assay.calibration_valid:
            return None
        
        for i in range(len(self.assay.curve_points) - 1):
            p1 = self.assay.curve_points[i]
            p2 = self.assay.curve_points[i + 1]
            
            if p1["conc"] <= self.assay.cutoff <= p2["conc"]:
                if self.assay.current_method in ["linear_piecewise", "linear_extrapolation",
                                                  "polynomial_degree2", "polynomial_degree3",
                                                  "cubic_spline", "akima_spline",
                                                  "model_4pl", "model_5pl"]:
                    return self._inverse_linear(p1, p2, self.assay.cutoff)
                else:
                    return self._inverse_semilog(p1, p2, self.assay.cutoff)
        return None
    
    def _inverse_linear(self, p1, p2, target_conc):
        if p2["conc"] == p1["conc"]:
            return p1["fluor"]
        ratio = (target_conc - p1["conc"]) / (p2["conc"] - p1["conc"])
        return p1["fluor"] + ratio * (p2["fluor"] - p1["fluor"])
    
    def _inverse_semilog(self, p1, p2, target_conc):
        if p2["conc"] == p1["conc"]:
            return p1["fluor"]
        log_t = math.log10(target_conc)
        log_p1 = math.log10(p1["conc"])
        log_p2 = math.log10(p2["conc"])
        ratio = (log_t - log_p1) / (log_p2 - log_p1)
        return p1["fluor"] + ratio * (p2["fluor"] - p1["fluor"])
    
    def _show_plate_grid(self):
        """Muestra la placa de 96 pozos ocupando todo el espacio."""
        grid_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar grid para que se expanda
        for i in range(9):  # 8 filas + 1 de encabezado
            grid_frame.grid_rowconfigure(i, weight=1)
        for j in range(13):  # 12 columnas + 1 de encabezado
            grid_frame.grid_columnconfigure(j, weight=1)
        
        rows = "ABCDEFGH"
        cols = range(1, 13)
        
        # Colores especiales para calibradores y control
        special_wells = {
            "A1": "#FEFEC1", "B1": "#FEFEC1", "C1": "#84E0F9", "D1": "#84E0F9",
            "E1": "#997070", "F1": "#997070", "G1": "#90EE90", "H1": "#90EE90",
            "A2": "#FFB6C1", "B2": "#FFB6C1", "C2": "#DDA0DD", "D2": "#DDA0DD",
            "E2": "#87CEEB", "F2": "#87CEEB",
        }
        
        # Encabezados de columnas
        for j, col in enumerate(cols):
            lbl = tk.Label(grid_frame, text=str(col), bg="#d0d0d0", relief="solid",
                           bd=1, font=("Arial", 10, "bold"))
            lbl.grid(row=0, column=j+1, padx=1, pady=1, sticky="nsew")
        
        # Filas y pozos
        for i, row in enumerate(rows):
            # Etiqueta de fila
            lbl_row = tk.Label(grid_frame, text=row, bg="#d0d0d0", relief="solid",
                               bd=1, font=("Arial", 10, "bold"))
            lbl_row.grid(row=i+1, column=0, padx=1, pady=1, sticky="nsew")
            
            # Pozos
            for j, col in enumerate(cols):
                well_id = f"{row}{col}"
                value = self.assay.plate.get_well_value(well_id)
                
                if well_id in special_wells:
                    bg_color = special_wells[well_id]
                else:
                    bg_color = self._get_sample_color(well_id)
                
                lbl = tk.Label(grid_frame, text=f"{value:.2f}", bg=bg_color,
                               relief="solid", bd=1, font=("Arial", 9))
                lbl.grid(row=i+1, column=j+1, padx=1, pady=1, sticky="nsew")
    
    def _get_sample_color(self, well_id):
        for sample in self.assay.samples:
            if sample["well1_coord"] == well_id or sample["well2_coord"] == well_id:
                if sample["interpretation"] == "Elevado":
                    return "#ADD8E6"
                elif sample["interpretation"] == "Repetir":
                    return "#FFFF00"
                elif sample["interpretation"] == "> Ult. Punto":
                    return "#C0C0C0"
        return "#FFFFFF"