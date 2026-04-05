"""
Vista para la calculadora de punto de corte por percentil 99.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os


class CutoffView:
    """Ventana para calcular y aplicar punto de corte por percentil 99."""
    
    def __init__(self, parent, controller, on_apply_callback):
        """
        Inicializa la ventana de cálculo de punto de corte.
        
        Args:
            parent: Ventana padre
            controller: Controlador principal (AssayController)
            on_apply_callback: Callback cuando se aplica un nuevo cutoff
        """
        self.parent = parent
        self.controller = controller
        self.on_apply_callback = on_apply_callback
        
        self.create_window()
        self.load_statistics()
    
    def create_window(self):
        """Crea la ventana."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Calculadora de Punto de Corte - Percentil 99")
        self.window.geometry("700x650")
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Recálculo de Punto de Corte por Percentil 99",
            font=("Arial", 14, "bold"),
            fg="#1e88e5"
        )
        title_label.pack(pady=(0, 10))
        
        # Descripción
        desc_text = """Este método calcula el punto de corte basado en el percentil 99 de las concentraciones 
de TSH en la población normal. Se recomienda utilizar al menos 30 muestras normales 
para obtener un cálculo estadísticamente significativo."""
        
        desc_label = tk.Label(
            main_frame,
            text=desc_text,
            font=("Arial", 9),
            fg="gray",
            justify="left",
            wraplength=600
        )
        desc_label.pack(pady=(0, 15))
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Frame de estadísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas de la población", padding="15")
        stats_frame.pack(fill="both", expand=True, pady=10)
        
        # Texto de estadísticas
        self.stats_text = tk.Text(stats_frame, height=12, width=70, font=("Courier", 10))
        self.stats_text.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.stats_text, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Frame de opciones
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill="x", pady=10)
        
        self.use_historical_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Incluir datos históricos",
            variable=self.use_historical_var,
            command=self.load_statistics
        ).pack(side="left", padx=5)
        
        ttk.Button(
            options_frame,
            text="Actualizar estadísticas",
            command=self.load_statistics
        ).pack(side="right", padx=5)
        
        # Frame de resultados
        result_frame = ttk.LabelFrame(main_frame, text="Resultado", padding="15")
        result_frame.pack(fill="x", pady=10)
        
        self.result_label = tk.Label(
            result_frame,
            text="",
            font=("Arial", 16, "bold")
        )
        self.result_label.pack()
        
        self.detail_label = tk.Label(
            result_frame,
            text="",
            font=("Arial", 10),
            fg="gray"
        )
        self.detail_label.pack()
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame,
            text="Aplicar nuevo punto de corte",
            command=self.apply_cutoff,
            width=25
        ).pack(side="right", padx=5)
        
        ttk.Button(
            button_frame,
            text="Exportar reporte",
            command=self.export_report,
            width=15
        ).pack(side="right", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cerrar",
            command=self.window.destroy,
            width=10
        ).pack(side="left", padx=5)
        
        # Centrar ventana
        self.center_window()
    
    def load_statistics(self):
        """Carga y muestra las estadísticas."""
        try:
            stats = self.controller.get_cutoff_statistics(
                use_historical=self.use_historical_var.get()
            )
            
            if not stats.get("available"):
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, stats.get("message", "No hay datos disponibles"))
                self.result_label.config(text="No hay suficientes datos", fg="red")
                self.detail_label.config(text="Se necesitan al menos 30 muestras normales")
                return
            
            # Mostrar estadísticas
            self.stats_text.delete(1.0, tk.END)
            
            stats_display = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    ESTADÍSTICAS DE LA POBLACIÓN                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   Número de muestras normales:     {stats['n_samples']:>8}                       ║
║   Media (mUI/L):                    {stats['mean']:>8.2f}                       ║
║   Desviación estándar (mUI/L):      {stats['std']:>8.2f}                       ║
║                                                                  ║
║   Mínimo (mUI/L):                   {stats['min']:>8.2f}                       ║
║   Máximo (mUI/L):                   {stats['max']:>8.2f}                       ║
║                                                                  ║
║   ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║   Percentil 95:                     {stats['percentile_95']:>8.2f}  mUI/L      ║
║   Percentil 97.5:                   {stats['percentile_97_5']:>8.2f}  mUI/L      ║
║   ▶ Percentil 99 (RECOMENDADO):     {stats['percentile_99']:>8.2f}  mUI/L      ║
║   Percentil 99.5:                   {stats['percentile_99_5']:>8.2f}  mUI/L      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
            
            if stats.get('historical_included'):
                stats_display += f"\n📊 Incluye {stats['historical_count']} datos históricos y {stats['current_count']} datos actuales.\n"
            
            self.stats_text.insert(tk.END, stats_display)
            
            # Mostrar resultado
            suggested = stats['percentile_99']
            current = self.controller.current_assay.cutoff if self.controller.current_assay else None
            
            self.result_label.config(
                text=f"Punto de corte sugerido: {suggested:.2f} mUI/L",
                fg="green"
            )
            
            if current:
                change = suggested - current
                change_text = f"(Actual: {current:.2f} mUI/L | Diferencia: {change:+.2f} mUI/L)"
                self.detail_label.config(text=change_text)
            else:
                self.detail_label.config(text="Basado en percentil 99 de la población normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estadísticas: {str(e)}")
    
    def apply_cutoff(self):
        """Aplica el punto de corte sugerido."""
        try:
            stats = self.controller.get_cutoff_statistics(
                use_historical=self.use_historical_var.get()
            )
            
            if not stats.get("available") or stats['n_samples'] < 30:
                messagebox.showwarning(
                    "Datos insuficientes",
                    f"No hay suficientes datos ({stats.get('n_samples', 0)} muestras).\n"
                    "Se necesitan al menos 30 muestras normales para un cálculo confiable."
                )
                return
            
            suggested = stats['percentile_99']
            current = self.controller.current_assay.cutoff if self.controller.current_assay else None
            
            # Confirmar cambio
            msg = f"¿Desea aplicar el nuevo punto de corte?\n\n"
            msg += f"Actual: {current:.2f} mUI/L\n"
            msg += f"Nuevo: {suggested:.2f} mUI/L\n"
            msg += f"Diferencia: {suggested - current:+.2f} mUI/L\n\n"
            msg += f"Basado en {stats['n_samples']} muestras normales (Percentil 99)"
            
            if messagebox.askyesno("Confirmar cambio", msg):
                self.on_apply_callback(suggested)
                self.window.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar punto de corte: {str(e)}")
    
    def export_report(self):
        """Exporta un reporte HTML con la recomendación."""
        try:
            from controllers.cutoff_controller import CutoffController
            cutoff_ctrl = CutoffController()
            
            report = cutoff_ctrl.get_recommendation_report(self.controller.current_assay)
            
            # Guardar archivo
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                initialfile=f"reporte_cutoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                messagebox.showinfo("Exportar", f"Reporte guardado en:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar reporte: {str(e)}")
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')