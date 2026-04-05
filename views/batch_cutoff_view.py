"""
Vista para calcular percentil 99 desde múltiples archivos.
Solo calcula usando muestras NORMALES (no elevadas).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
from typing import Dict, List


class BatchCutoffView:
    """Ventana para calcular percentil 99 desde múltiples archivos .flu."""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.cutoff_controller = None
        self.loaded_plates_data = []
        
        self.create_window()
    
    def create_window(self):
        """Crea la ventana."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Cálculo de Percentil 99 - Múltiples Archivos")
        self.window.geometry("950x800")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Cálculo de Percentil 99 desde Múltiples Archivos",
            font=("Arial", 14, "bold"),
            fg="#1e88e5"
        )
        title_label.pack(pady=(0, 10))
        
        # Descripción
        desc_text = """Seleccione múltiples archivos .flu para calcular el percentil 99.
El cálculo se realiza SOLO sobre MUESTRAS NORMALES (excluye "Elevado" y "> Ult. Punto").
El resultado es solo informativo - usted deberá aplicar el valor manualmente en Configuración."""
        
        desc_label = tk.Label(
            main_frame,
            text=desc_text,
            font=("Arial", 9),
            fg="gray",
            justify="left",
            wraplength=900
        )
        desc_label.pack(pady=(0, 15))
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=5)
        
        # Frame de selección de archivos
        file_frame = ttk.LabelFrame(main_frame, text="Archivos seleccionados", padding="10")
        file_frame.pack(fill="both", expand=True, pady=10)
        
        # Listbox con scrollbar
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.files_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Botones de archivos
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame,
            text="Agregar archivos...",
            command=self.add_files,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Agregar carpeta...",
            command=self.add_folder,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Eliminar seleccionados",
            command=self.remove_selected,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Limpiar todo",
            command=self.clear_all,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame de opciones
        options_frame = ttk.LabelFrame(main_frame, text="Opciones de cálculo", padding="10")
        options_frame.pack(fill="x", pady=10)
        
        # Percentil
        ttk.Label(options_frame, text="Percentil a calcular:").pack(side=tk.LEFT, padx=5)
        self.percentile_var = tk.StringVar(value="99")
        percentile_combo = ttk.Combobox(
            options_frame,
            textvariable=self.percentile_var,
            values=["95", "97.5", "99", "99.5", "99.9"],
            width=8,
            state="readonly"
        )
        percentile_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(options_frame, text="(Usar percentil 99 para punto de corte TSH)").pack(side=tk.LEFT, padx=10)
        
        # Punto de corte para interpretación
        ttk.Label(options_frame, text=" | Punto de corte para interpretación:").pack(side=tk.LEFT, padx=10)
        self.cutoff_var = tk.StringVar(value="30.0")
        cutoff_entry = ttk.Entry(options_frame, textvariable=self.cutoff_var, width=8)
        cutoff_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(options_frame, text="mUI/L").pack(side=tk.LEFT)
        
        # Frame de resultados
        result_frame = ttk.LabelFrame(main_frame, text="Resultados del cálculo", padding="10")
        result_frame.pack(fill="both", expand=True, pady=10)
        
        # Text widget para resultados
        self.result_text = tk.Text(result_frame, height=14, width=85, font=("Courier", 10))
        self.result_text.pack(fill="both", expand=True)
        
        result_scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        result_scrollbar.pack(side="right", fill="y")
        
        # Frame de botones
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            action_frame,
            text="Calcular Percentil",
            command=self.calculate_percentile,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Exportar resultados",
            command=self.export_results,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Cerrar",
            command=self.window.destroy,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Listo. Seleccione archivos .flu para calcular.")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        status_bar.pack(fill="x", pady=(10, 0))
        
        self.center_window()
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos .flu",
            filetypes=[("Archivos de fluorescencia", "*.flu"), ("Todos los archivos", "*.*")]
        )
        for file in files:
            if file not in self.files_listbox.get(0, tk.END):
                self.files_listbox.insert(tk.END, file)
        self.status_var.set(f"{self.files_listbox.size()} archivos seleccionados")
    
    def add_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta con archivos .flu")
        if folder:
            import glob
            files = glob.glob(os.path.join(folder, "*.flu"))
            files.extend(glob.glob(os.path.join(folder, "*.FLU")))
            added = 0
            for file in files:
                if file not in self.files_listbox.get(0, tk.END):
                    self.files_listbox.insert(tk.END, file)
                    added += 1
            self.status_var.set(f"Agregados {added} archivos. Total: {self.files_listbox.size()}")
    
    def remove_selected(self):
        selected = self.files_listbox.curselection()
        for i in reversed(selected):
            self.files_listbox.delete(i)
        self.status_var.set(f"{self.files_listbox.size()} archivos seleccionados")
    
    def clear_all(self):
        self.files_listbox.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("Lista limpiada")
    
    def calculate_percentile(self):
        files = list(self.files_listbox.get(0, tk.END))
        
        if len(files) == 0:
            messagebox.showwarning("Sin archivos", "Seleccione al menos un archivo .flu")
            return
        
        from controllers.cutoff_controller import CutoffController
        self.cutoff_controller = CutoffController()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "🔄 Procesando archivos...\n")
        self.result_text.insert(tk.END, "   (Calculando concentraciones y excluyendo muestras elevadas)\n\n")
        self.window.update()
        
        # Usar el cutoff actual de la configuración o el ingresado
        try:
            cutoff_value = float(self.cutoff_var.get())
        except:
            cutoff_value = 30.0
        
        plates_data, errors = self.cutoff_controller.load_multiple_flu_files(files, cutoff=cutoff_value)
        
        if not plates_data:
            self.result_text.delete(1.0, tk.END)
            error_msg = "❌ ERROR: No se pudo procesar ningún archivo.\n\n"
            if errors:
                error_msg += "Errores encontrados:\n"
                for err in errors:
                    error_msg += f"  • {err}\n"
            self.result_text.insert(tk.END, error_msg)
            self.status_var.set("Error: No se procesaron archivos")
            return
        
        percentile = float(self.percentile_var.get())
        result = self.cutoff_controller.calculate_percentile_from_loaded_plates(plates_data, percentile=percentile)
        
        self.display_results(result, plates_data, errors)
    
    def display_results(self, result: Dict, plates_data: List[Dict], errors: List[str]):
        self.result_text.delete(1.0, tk.END)
        
        if not result.get('success'):
            self.result_text.insert(tk.END, f"❌ {result.get('message', 'Error en el cálculo')}\n")
            self.status_var.set("Cálculo fallido")
            return
        
        # Encabezado
        self.result_text.insert(tk.END, "=" * 80 + "\n")
        self.result_text.insert(tk.END, f"  CÁLCULO DE PERCENTIL {result['percentile']:.0f} - TSH NEONATAL\n")
        self.result_text.insert(tk.END, "=" * 80 + "\n\n")
        
        # Resultado principal
        self.result_text.insert(tk.END, "📊 RESULTADO PRINCIPAL:\n")
        self.result_text.insert(tk.END, f"  ▶ Percentil {result['percentile']:.0f}: {result['percentile_value']} mUI/L\n\n")
        
        # Resumen de datos
        self.result_text.insert(tk.END, "📈 RESUMEN DE DATOS:\n")
        self.result_text.insert(tk.END, f"  • Total de placas procesadas: {result['total_plates']}\n")
        self.result_text.insert(tk.END, f"  • Total de muestras analizadas: {result['total_samples']}\n")
        self.result_text.insert(tk.END, f"  • Muestras ELEVADAS excluidas: {result.get('total_elevated', 0)}\n")
        self.result_text.insert(tk.END, f"  • Muestras > Ult. Punto excluidas: {result.get('total_above_last', 0)}\n")
        self.result_text.insert(tk.END, f"  • ✅ MUESTRAS NORMALES UTILIZADAS: {result['total_normal_samples']}\n\n")
        
        # Estadísticas
        stats = result['statistics']
        self.result_text.insert(tk.END, "📐 ESTADÍSTICAS DE LA POBLACIÓN NORMAL (mUI/L):\n")
        self.result_text.insert(tk.END, f"  • Media (promedio):        {stats['mean']:>8.2f} mUI/L\n")
        self.result_text.insert(tk.END, f"  • Desviación estándar:     {stats['std']:>8.2f} mUI/L\n")
        self.result_text.insert(tk.END, f"  • Mediana:                 {stats['median']:>8.2f} mUI/L\n")
        self.result_text.insert(tk.END, f"  • Mínimo:                  {stats['min']:>8.2f} mUI/L\n")
        self.result_text.insert(tk.END, f"  • Máximo:                  {stats['max']:>8.2f} mUI/L\n\n")
        
        # Percentiles
        self.result_text.insert(tk.END, "📊 PERCENTILES:\n")
        self.result_text.insert(tk.END, f"  • Percentil 95:            {stats['percentile_95']:>8.2f} mUI/L\n")
        self.result_text.insert(tk.END, f"  • Percentil 97.5:          {stats['percentile_97_5']:>8.2f} mUI/L\n")
        self.result_text.insert(tk.END, f"  • ▶ Percentil 99:          {stats['percentile_99']:>8.2f} mUI/L  ← RECOMENDADO\n")
        self.result_text.insert(tk.END, f"  • Percentil 99.5:          {stats['percentile_99_5']:>8.2f} mUI/L\n\n")
        
        # Detalle por placa (versión CORREGIDA - sin mean_conc)
        self.result_text.insert(tk.END, "📁 DETALLE POR PLACA:\n")
        self.result_text.insert(tk.END, "-" * 80 + "\n")
        self.result_text.insert(tk.END, f"{'Archivo':<35} {'Total':<8} {'Normales':<10} {'Elevados':<10}\n")
        self.result_text.insert(tk.END, "-" * 80 + "\n")
        
        for plate in plates_data:
            name = plate['file'][:34] if len(plate['file']) > 34 else plate['file']
            elevated = plate.get('elevated_count', 0)
            self.result_text.insert(tk.END, 
                f"{name:<35} {plate['total_samples']:<8} {plate['normal_count']:<10} {elevated:<10}\n")
        
        # Mostrar también las estadísticas por placa si están disponibles
        if result.get('plates_summary'):
            self.result_text.insert(tk.END, "\n📊 ESTADÍSTICAS POR PLACA (muestras normales):\n")
            self.result_text.insert(tk.END, "-" * 80 + "\n")
            self.result_text.insert(tk.END, f"{'Archivo':<35} {'Muestras':<10} {'Mínimo':<10} {'Máximo':<10} {'Media':<10}\n")
            self.result_text.insert(tk.END, "-" * 80 + "\n")
            
            for summary in result.get('plates_summary', []):
                name = summary['file'][:34] if len(summary['file']) > 34 else summary['file']
                self.result_text.insert(tk.END, 
                    f"{name:<35} {summary['normal_count']:<10} {summary['min_conc']:<10.2f} {summary['max_conc']:<10.2f} {summary['mean_conc']:<10.2f}\n")
        
        if errors:
            self.result_text.insert(tk.END, "\n⚠ ARCHIVOS CON ERRORES:\n")
            for err in errors:
                self.result_text.insert(tk.END, f"  • {err}\n")
        
        self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n")
        self.result_text.insert(tk.END, "ℹ️ NOTA: Este es solo un cálculo informativo.\n")
        self.result_text.insert(tk.END, "       Para aplicar este valor, vaya a Configuración → Editar parámetros\n")
        self.result_text.insert(tk.END, "       y modifique el 'Punto de corte' manualmente.\n")
        self.result_text.insert(tk.END, "=" * 80 + "\n")
        
        self.status_var.set(f"Cálculo completado. Percentil {result['percentile']:.0f} = {result['percentile_value']} mUI/L (basado en {result['total_normal_samples']} muestras normales)")
    
    def export_results(self):
        if self.result_text.get(1.0, tk.END).strip() == "":
            messagebox.showwarning("Sin resultados", "Primero debe calcular el percentil")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile=f"percentil_calculo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.get(1.0, tk.END))
                messagebox.showinfo("Exportar", f"Resultados guardados en:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')