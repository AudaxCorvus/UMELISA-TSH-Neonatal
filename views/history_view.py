"""
Vista para gestionar el historial de datos guardados.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class HistoryView:
    """Ventana para ver y gestionar el historial de placas."""
    
    def __init__(self, parent, controller):
        """
        Inicializa la ventana de historial.
        
        Args:
            parent: Ventana padre
            controller: Controlador principal
        """
        self.parent = parent
        self.controller = controller
        self.cutoff_controller = None
        
        self.create_window()
        self.load_history()
    
    def create_window(self):
        """Crea la ventana."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Historial de Datos - UMELISA TSH")
        self.window.geometry("900x600")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Historial de Placas Cargadas",
            font=("Arial", 14, "bold"),
            fg="#1e88e5"
        )
        title_label.pack(pady=(0, 10))
        
        # Descripción
        desc_label = tk.Label(
            main_frame,
            text="Todas las placas cargadas se guardan automáticamente para análisis estadísticos.",
            font=("Arial", 9),
            fg="gray"
        )
        desc_label.pack(pady=(0, 15))
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=5)
        
        # Frame de información
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=10)
        
        self.info_label = tk.Label(
            info_frame,
            text="Cargando historial...",
            font=("Arial", 10),
            fg="blue"
        )
        self.info_label.pack(side=tk.LEFT)
        
        # Frame de tabla
        table_frame = ttk.LabelFrame(main_frame, text="Placas guardadas", padding="10")
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # Treeview con scrollbars
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill="both", expand=True)
        
        scrollbar_y = ttk.Scrollbar(tree_container)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("ID", "Fecha", "Archivo", "Muestras", "Normales", "Cutoff", "Método")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=15
        )
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Configurar columnas
        col_widths = [100, 150, 250, 80, 80, 80, 120]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame,
            text="Eliminar seleccionada",
            command=self.delete_selected,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Calcular percentil desde historial",
            command=self.calculate_from_history,
            width=25
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Borrar TODO el historial",
            command=self.clear_all_history,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Exportar historial",
            command=self.export_history,
            width=15
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Actualizar",
            command=self.load_history,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cerrar",
            command=self.window.destroy,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
        # Centrar ventana
        self.center_window()
    
    def load_history(self):
        """Carga y muestra el historial."""
        try:
            from controllers.cutoff_controller import CutoffController
            self.cutoff_controller = CutoffController()
            
            summary = self.cutoff_controller.get_history_summary()
            
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Agregar placas
            plates = summary.get('plates_list', [])
            for plate in plates:
                fecha = plate.get('date', '')[:19] if plate.get('date') else ''
                self.tree.insert("", tk.END, values=(
                    plate.get('id', '')[:15],
                    fecha,
                    plate.get('file', 'Desconocido'),
                    plate.get('total_count', 0),
                    plate.get('normal_count', 0),
                    '',
                    ''
                ))
            
            # Actualizar información
            total_plates = summary.get('total_plates', 0)
            total_samples = summary.get('total_normal_samples', 0)
            
            info_text = f"📊 Total: {total_plates} placas | {total_samples} muestras normales"
            
            if summary.get('statistics'):
                stats = summary['statistics']
                info_text += f" | Media: {stats['mean']} mUI/L | Percentil 99: {stats['percentile_99']} mUI/L"
            
            self.info_label.config(text=info_text)
            
            if total_plates == 0:
                self.info_label.config(fg="orange")
                self.info_label.config(text="⚠ No hay datos históricos. Cargue placas para acumular historial.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")
    
    def delete_selected(self):
        """Elimina la placa seleccionada."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Sin selección", "Seleccione una placa para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Eliminar esta placa del historial?"):
            try:
                item = self.tree.item(selected[0])
                plate_id = item['values'][0]
                
                self.cutoff_controller.delete_plate_from_history(plate_id)
                self.load_history()
                messagebox.showinfo("Eliminado", "Placa eliminada del historial")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def clear_all_history(self):
        """Borra todo el historial."""
        if messagebox.askyesno(
            "Confirmar eliminación total",
            "⚠ ADVERTENCIA: Esta acción eliminará TODO el historial de placas.\n"
            "¿Está absolutamente seguro?\n\n"
            "Esta operación NO se puede deshacer."
        ):
            try:
                self.cutoff_controller.clear_history()
                self.load_history()
                messagebox.showinfo("Historial limpiado", "Todo el historial ha sido eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"Error al limpiar historial: {str(e)}")
    
    def calculate_from_history(self):
        """Calcula percentil desde el historial completo."""
        try:
            result = self.cutoff_controller.calculate_percentile_from_history(percentile=99)
            
            if result.get('success'):
                msg = f"📊 CÁLCULO DESDE HISTORIAL\n\n"
                msg += f"Total de placas: {result['total_plates']}\n"
                msg += f"Muestras normales: {result['total_normal_samples']}\n"
                msg += f"Percentil 99: {result['percentile_value']} mUI/L\n\n"
                msg += f"Estadísticas:\n"
                msg += f"  Media: {result['statistics']['mean']} mUI/L\n"
                msg += f"  DS: {result['statistics']['std']} mUI/L\n"
                msg += f"  Mín: {result['statistics']['min']} mUI/L\n"
                msg += f"  Máx: {result['statistics']['max']} mUI/L\n\n"
                msg += f"ℹ️ Para aplicar este valor, vaya a Configuración → Editar parámetros"
                
                messagebox.showinfo("Percentil 99 desde historial", msg)
            else:
                messagebox.showwarning("Datos insuficientes", result.get('message', 'Error en el cálculo'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en cálculo: {str(e)}")
    
    def export_history(self):
        """Exporta el historial a un archivo CSV."""
        from tkinter import filedialog
        import csv
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Todos los archivos", "*.*")],
            initialfile=f"historial_umelisa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Fecha", "Archivo", "Muestras", "Normales"])
                    
                    for item in self.tree.get_children():
                        values = self.tree.item(item)['values']
                        writer.writerow(values[:5])
                
                messagebox.showinfo("Exportar", f"Historial exportado a:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')