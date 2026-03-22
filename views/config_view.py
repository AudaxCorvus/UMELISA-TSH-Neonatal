"""
Ventana de configuración para UMELISA TSH Neonatal.
Permite editar todos los parámetros del ensayo.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ConfigView:
    """Ventana de configuración del ensayo."""
    
    def __init__(self, parent, config, on_change_callback):
        """
        Inicializa la ventana de configuración.
        
        Args:
            parent: Ventana padre
            config: Diccionario con la configuración actual
            on_change_callback: Función a llamar cuando cambia la configuración
        """
        self.parent = parent
        self.config = config
        self.on_change_callback = on_change_callback
        
        self.create_window()
        
    def create_window(self):
        """Crea la ventana de configuración."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Configuración del Ensayo")
        self.window.geometry("600x550")
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        
        # Frame principal con scroll
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # ===== LOTE Y TIPO DE MUESTRA =====
        basic_frame = ttk.LabelFrame(main_frame, text="Información básica", padding="15")
        basic_frame.pack(fill="x", pady=(0, 15))
        
        # ===== PUNTO DE CORTE =====
        cutoff_frame = ttk.LabelFrame(main_frame, text="Punto de corte", padding="15")
        cutoff_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(cutoff_frame, text="Valor (mUI/L):", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        self.cutoff_entry = ttk.Entry(cutoff_frame, width=15, font=("Arial", 10))
        self.cutoff_entry.insert(0, str(self.config["cutoff"]))
        self.cutoff_entry.grid(row=0, column=1, sticky="w", padx=10)
        
        # Mostrar valores según tipo
        self.cutoff_info = ttk.Label(cutoff_frame, text="", font=("Arial", 9), foreground="gray")
        self.cutoff_info.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # ===== LÍMITES DEL CONTROL =====
        control_frame = ttk.LabelFrame(main_frame, text="Límites del Control", padding="15")
        control_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(control_frame, text="Límite inferior:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.lower_entry = ttk.Entry(control_frame, width=15, font=("Arial", 10))
        self.lower_entry.insert(0, str(self.config["control_lower"]))
        self.lower_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ttk.Label(control_frame, text="Límite superior:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.upper_entry = ttk.Entry(control_frame, width=15, font=("Arial", 10))
        self.upper_entry.insert(0, str(self.config["control_upper"]))
        self.upper_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        ttk.Label(control_frame, text="(0 = sin validación)", font=("Arial", 9), 
                 foreground="gray").grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        # ===== CALIBRADORES =====
        cal_frame = ttk.LabelFrame(main_frame, text="Concentraciones de Calibradores (mUI/L)", padding="15")
        cal_frame.pack(fill="x", pady=(0, 15))
        
        # Crear entradas para cada calibrador
        self.cal_entries = {}
        cal_row = 0
        for i, (cal, value) in enumerate(self.config["calibrators"].items()):
            col = i % 3
            if col == 0:
                cal_row += 1
            
            # Frame para cada calibrador
            cal_item_frame = ttk.Frame(cal_frame)
            cal_item_frame.grid(row=cal_row, column=col, sticky="w", padx=10, pady=5)
            
            ttk.Label(cal_item_frame, text=f"{cal}:", font=("Arial", 10, "bold")).pack(side="left")
            entry = ttk.Entry(cal_item_frame, width=10, font=("Arial", 10))
            entry.insert(0, str(value))
            entry.pack(side="left", padx=5)
            self.cal_entries[cal] = entry
        
        # ===== BOTONES =====
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save_config,
                  width=15).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.window.destroy,
                  width=15).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Restaurar", command=self.restore_defaults,
                  width=15).pack(side="left", padx=5)
        
        # Centrar ventana
        self.center_window()
    
    def save_config(self):
        """Guarda la configuración y notifica al callback."""
        try:
            # Validar y obtener valores
            new_config = {
                "cutoff": float(self.cutoff_entry.get()),
                "control_lower": float(self.lower_entry.get()),
                "control_upper": float(self.upper_entry.get()),
                "calibrators": {}
            }
            
            # Validar calibradores
            for cal, entry in self.cal_entries.items():
                value = float(entry.get())
                if value <= 0:
                    raise ValueError(f"El calibrador {cal} debe ser > 0")
                new_config["calibrators"][cal] = value
            
            # Validar cutoff positivo
            if new_config["cutoff"] <= 0:
                raise ValueError("El punto de corte debe ser > 0")
            
            # Validar límites de control
            if new_config["control_lower"] < 0 or new_config["control_upper"] < 0:
                raise ValueError("Los límites de control no pueden ser negativos")
            
            if (new_config["control_lower"] > 0 or new_config["control_upper"] > 0) and \
               new_config["control_lower"] >= new_config["control_upper"]:
                raise ValueError("El límite inferior debe ser menor que el superior")
            
            # Actualizar configuración
            self.config = new_config
            
            # Notificar cambio
            self.on_change_callback(new_config)
            
            # Cerrar ventana
            self.window.destroy()
           
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def restore_defaults(self):
        """Restaura los valores por defecto."""
        if messagebox.askyesno("Restaurar", "¿Restaurar valores por defecto?"):
            # Valores por defecto
            
            self.cutoff_entry.delete(0, tk.END)
            self.cutoff_entry.insert(0, "30.0")
            
            self.lower_entry.delete(0, tk.END)
            self.lower_entry.insert(0, "20.0")
            
            self.upper_entry.delete(0, tk.END)
            self.upper_entry.insert(0, "30.0")
            
            # Calibradores por defecto
            defaults = {
                "A": 0.520,
                "B": 10.750,
                "C": 25.200,
                "D": 49.850,
                "E": 96.150,
                "F": 194.000
            }
            
            for cal, value in defaults.items():
                entry = self.cal_entries[cal]
                entry.delete(0, tk.END)
                entry.insert(0, str(value))
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')