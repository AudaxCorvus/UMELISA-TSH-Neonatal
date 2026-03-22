"""
Modelo para el ensayo UMELISA TSH Neonatal.
Implementa múltiples métodos de interpolación/regresión.
"""

from models.plate_model import PlateModel
import math
import numpy as np
from scipy import interpolate
from scipy.optimize import curve_fit
from typing import List, Dict, Optional, Callable
import warnings
warnings.filterwarnings('ignore')


class AssayModel:
    """
    Representa un ensayo UMELISA TSH Neonatal completo.
    Soporta múltiples métodos de calibración.
    """
    
    # Tolerancias para duplicados
    TOLERANCE_SUERO = 0.10  # 10%
    TOLERANCE_PAPEL = 0.15  # 15%
    
    # Métodos disponibles
    AVAILABLE_METHODS = [
        "linear_piecewise",      # Lineal punto a punto
        "semilog_piecewise",     # Semilog (A-B lineal, resto log)
        "linear_extrapolation",  # Lineal con extrapolación
        "polynomial_degree2",    # Polinomio grado 2
        "polynomial_degree3",    # Polinomio grado 3
        "cubic_spline",          # Spline cúbico
        "akima_spline",          # Akima spline
        "model_4pl",             # Modelo 4PL
        "model_5pl"              # Modelo 5PL
    ]
    
    def __init__(self, plate: PlateModel, 
                 cutoff: float = 30.0, 
                 control_lower: float = 0.0, 
                 control_upper: float = 0.0, 
                 calibrators: Optional[Dict[str, float]] = None):
        """
        Inicializa el modelo de ensayo TSH.
        """
        if plate.is_empty():
            raise ValueError("La placa está vacía. Por favor, cargue datos antes de crear el modelo de ensayo.")
        
        self.plate = plate
        self.cutoff = cutoff
        self.control_lower = control_lower
        self.control_upper = control_upper
        
        # Concentraciones de calibradores
        if calibrators is None:
            self.calibrator_concentrations = {
                "A": 0.520, "B": 10.750, "C": 25.200,
                "D": 49.850, "E": 96.150, "F": 194.000
            }
        else:
            self.calibrator_concentrations = calibrators
        
        # Almacenar calibradores
        self.calibrators = {}
        for cal, conc in self.calibrator_concentrations.items():
            self.calibrators[cal] = {
                "well1": None, "well2": None, "mean": None, 
                "conc": conc, "log_conc": math.log10(conc) if conc > 0 else -10
            }
        
        # Control del ensayo
        self.assay_control = {"well1": None, "well2": None, "mean": None}
        
        # Muestras
        self.samples: List[Dict] = []
        
        # Estado de validación
        self.calibration_valid = True
        self.control_valid = True
        self.valid = True
        self.validation_message = ""
        
        # Datos de la curva
        self.curve_points: List[Dict] = []
        self.interpolation_function: Optional[Callable] = None
        self.current_method: str = "semilog_piecewise"
        
        # Parámetros de modelos ajustados
        self.fit_params: Dict = {}
        
        # Ejecutar el proceso completo
        self._process()
    
    # ============================================================
    #   PROCESO COMPLETO DEL ENSAYO
    # ============================================================
    
    def _process(self):
        """Ejecuta todas las etapas del procesamiento del ensayo."""
        self._extract_calibrators_and_control()
        self._validate_calibration_curve()
        self._pair_samples()
        self._validate_control()
    
    # ============================================================
    #   EXTRACCIÓN DE CALIBRADORES Y CONTROL
    # ============================================================
    
    def _extract_calibrators_and_control(self):
        """Extrae calibradores y control desde posiciones estándar de la placa."""
        cal_positions = {
            "A": ("A1", "B1"), "B": ("C1", "D1"), "C": ("E1", "F1"),
            "D": ("G1", "H1"), "E": ("A2", "B2"), "F": ("C2", "D2")
        }
        
        for cal, (well1, well2) in cal_positions.items():
            self.calibrators[cal]["well1"] = self.plate.get_well_value(well1)
            self.calibrators[cal]["well2"] = self.plate.get_well_value(well2)
            self.calibrators[cal]["mean"] = (self.calibrators[cal]["well1"] + self.calibrators[cal]["well2"]) / 2
        
        # Control
        self.assay_control["well1"] = self.plate.get_well_value("E2")
        self.assay_control["well2"] = self.plate.get_well_value("F2")
        self.assay_control["mean"] = (self.assay_control["well1"] + self.assay_control["well2"]) / 2
        
        self._build_curve_points()
    
    def _build_curve_points(self):
        """Construye la lista de puntos (conc, fluor) para la curva de calibración."""
        self.curve_points = []
        for cal in ["A", "B", "C", "D", "E", "F"]:
            if self.calibrators[cal]["mean"] is not None:
                self.curve_points.append({
                    "conc": self.calibrators[cal]["conc"],
                    "log_conc": self.calibrators[cal]["log_conc"],
                    "fluor": self.calibrators[cal]["mean"]
                })
        self.curve_points.sort(key=lambda p: p["conc"])
    
    # ============================================================
    #   VALIDACIÓN DE LA CURVA
    # ============================================================
    
    def _validate_calibration_curve(self):
        """Valida que la curva sea monótona creciente."""
        prev_fluor = -float('inf')
        for cal in ["A", "B", "C", "D", "E", "F"]:
            current_fluor = self.calibrators[cal]["mean"]
            if current_fluor is None or current_fluor <= prev_fluor:
                self.calibration_valid = False
                self.valid = False
                self.validation_message = "CURVA DE CALIBRACIÓN RECHAZADA, REPITA EL ENSAYO"
                return
            prev_fluor = current_fluor
        self.calibration_valid = True
    
    def _validate_control(self):
        """Valida el control del ensayo."""
        if self.control_lower == 0 and self.control_upper == 0:
            self.control_valid = False
            return
        
        if (self.assay_control["mean"] is None or
            self.assay_control["mean"] < self.control_lower or
            self.assay_control["mean"] > self.control_upper):
            self.control_valid = False
            self.validation_message = "SUERO CONTROL FUERA DE RANGO. SUGERIMOS REPETIR EL ENSAYO"
        else:
            self.control_valid = True
    
    # ============================================================
    #   AGRUPACIÓN DE MUESTRAS
    # ============================================================
    
    def _pair_samples(self):
        """Agrupa pozos en pares consecutivos (duplicados)."""
        all_wells = list(self.plate.get_all_wells())
        sample_wells = all_wells[14:]  # Saltar calibradores y control
        
        self.samples = []
        for i in range(0, len(sample_wells), 2):
            if i + 1 < len(sample_wells):
                well1_coord, well1_value = sample_wells[i]
                well2_coord, well2_value = sample_wells[i + 1]
                
                mean_fluor = (well1_value + well2_value) / 2
                
                if well1_value > 0 or well2_value > 0:
                    self.samples.append({
                        "well1_coord": well1_coord,
                        "well2_coord": well2_coord,
                        "fluor1": well1_value,
                        "fluor2": well2_value,
                        "mean_fluor": mean_fluor,
                        "concentration": None,
                        "interpretation": None,
                        "needs_repeat": False,
                        "repeat_reason": None
                    })
    
    # ============================================================
    #   CÁLCULO DE CONCENTRACIONES - MÚLTIPLES MÉTODOS
    # ============================================================
    
    def calculate_concentrations(self, method: str = "semilog_piecewise") -> bool:
        """Calcula las concentraciones de las muestras usando el método especificado."""
        if not self.calibration_valid:
            return False
        
        if method not in self.AVAILABLE_METHODS:
            raise ValueError(f"Método no disponible: {method}. Disponibles: {self.AVAILABLE_METHODS}")
        
        self.current_method = method
        
        # Construir función de interpolación según el método
        self._build_interpolation_function(method)
        
        # Calcular cada muestra
        for sample in self.samples:
            try:
                sample["concentration"] = self._interpolate(sample["mean_fluor"])
                if sample["concentration"] is not None and sample["concentration"] < 0:
                    sample["concentration"] = 0.0
            except Exception as e:
                print(f"Error en muestra {sample['well1_coord']}: {e}")
                sample["concentration"] = None
        
        return True
    
    def _build_interpolation_function(self, method: str):
        """Construye la función de interpolación según el método seleccionado."""
        x_conc = np.array([p["conc"] for p in self.curve_points])
        x_log = np.array([p["log_conc"] for p in self.curve_points])
        y_fluor = np.array([p["fluor"] for p in self.curve_points])
        
        if method == "linear_piecewise":
            # Interpolación lineal punto a punto en espacio original
            self.interpolation_function = lambda f: np.interp(f, y_fluor, x_conc)
            
        elif method == "semilog_piecewise":
            # Según manual: entre A y B es lineal-lineal, resto lineal en log(conc)
            def semilog_interp(fluorescence):
                pA = self.curve_points[0]
                pB = self.curve_points[1]
                
                # Zona A-B: interpolación lineal-lineal
                if fluorescence <= pB["fluor"]:
                    if pB["fluor"] == pA["fluor"]:
                        return pA["conc"]
                    return pA["conc"] + (fluorescence - pA["fluor"]) * (pB["conc"] - pA["conc"]) / (pB["fluor"] - pA["fluor"])
                else:
                    # Zona resto: interpolación lineal en espacio log(conc)
                    for i in range(1, len(self.curve_points) - 1):
                        p1 = self.curve_points[i]
                        p2 = self.curve_points[i + 1]
                        if p1["fluor"] <= fluorescence <= p2["fluor"]:
                            if p2["fluor"] == p1["fluor"]:
                                return p1["conc"]
                            log_conc = p1["log_conc"] + (fluorescence - p1["fluor"]) * (p2["log_conc"] - p1["log_conc"]) / (p2["fluor"] - p1["fluor"])
                            return 10 ** log_conc
                    
                    # Extrapolación superior
                    p_last = self.curve_points[-1]
                    p_prev = self.curve_points[-2]
                    if fluorescence > p_last["fluor"]:
                        log_conc = p_prev["log_conc"] + (fluorescence - p_prev["fluor"]) * (p_last["log_conc"] - p_prev["log_conc"]) / (p_last["fluor"] - p_prev["fluor"])
                        return 10 ** log_conc
                    
                    return None
            self.interpolation_function = semilog_interp
            
        elif method == "linear_extrapolation":
            # Lineal con extrapolación
            def linear_extrap(fluorescence):
                if fluorescence <= y_fluor[-1]:
                    return np.interp(fluorescence, y_fluor, x_conc)
                else:
                    p1, p2 = self.curve_points[-2], self.curve_points[-1]
                    slope = (p2["conc"] - p1["conc"]) / (p2["fluor"] - p1["fluor"])
                    return p2["conc"] + slope * (fluorescence - p2["fluor"])
            self.interpolation_function = linear_extrap
            
        elif method == "polynomial_degree2":
            # Polinomio grado 2 en espacio LINEAL
            coeffs = np.polyfit(y_fluor, x_conc, 2)
            self.fit_params["coeffs"] = coeffs
            self.fit_params["poly_degree"] = 2
            self.interpolation_function = lambda f: np.polyval(coeffs, f)
            
        elif method == "polynomial_degree3":
            # Polinomio grado 3 en espacio LINEAL
            coeffs = np.polyfit(y_fluor, x_conc, 3)
            self.fit_params["coeffs"] = coeffs
            self.fit_params["poly_degree"] = 3
            self.interpolation_function = lambda f: np.polyval(coeffs, f)
            
        elif method == "cubic_spline":
            # Spline cúbico en espacio LINEAL
            spline = interpolate.CubicSpline(y_fluor, x_conc, extrapolate=True)
            self.fit_params["spline"] = spline
            self.interpolation_function = lambda f: spline(f)
            
        elif method == "akima_spline":
            # Akima spline en espacio LINEAL
            akima = interpolate.Akima1DInterpolator(y_fluor, x_conc)
            self.fit_params["akima"] = akima
            self.interpolation_function = lambda f: akima(f)
            
        elif method == "model_4pl":
            self._fit_4pl(x_conc, y_fluor)
            self.interpolation_function = lambda f: self._inverse_4pl(f)
            
        elif method == "model_5pl":
            self._fit_5pl(x_conc, y_fluor)
            self.interpolation_function = lambda f: self._inverse_5pl(f)
    
    def _fit_4pl(self, x: np.ndarray, y: np.ndarray):
        """Ajusta modelo 4PL."""
        A0 = max(y) * 1.05
        D0 = min(y) * 0.95
        C0 = x[len(x)//2]
        B0 = 1.2
        
        def _4pl(x, A, B, C, D):
            return D + (A - D) / (1 + (C / x) ** B)
        
        try:
            popt, _ = curve_fit(_4pl, x, y, p0=[A0, B0, C0, D0], maxfev=5000)
            self.fit_params["4pl_params"] = {
                "A": popt[0], "B": popt[1], "C": popt[2], "D": popt[3]
            }
        except Exception as e:
            print(f"Error en ajuste 4PL: {e}")
            self.fit_params["4pl_params"] = {"A": A0, "B": B0, "C": C0, "D": D0}
    
    def _inverse_4pl(self, y_value: float) -> float:
        """Calcula x a partir de y usando el modelo 4PL."""
        params = self.fit_params.get("4pl_params", {})
        A = params.get("A", 1)
        B = params.get("B", 1)
        C = params.get("C", 1)
        D = params.get("D", 0)
        
        if y_value <= D:
            return 0.0
        if y_value >= A:
            return 1000.0
        
        try:
            term = (A - D) / (y_value - D) - 1
            if term > 0:
                return C / (term ** (1 / B))
            else:
                return 1000.0
        except:
            return 1000.0
    
    def _fit_5pl(self, x: np.ndarray, y: np.ndarray):
        """Ajusta modelo 5PL."""
        A0 = max(y) * 1.05
        D0 = min(y) * 0.95
        C0 = x[len(x)//2]
        B0 = 1.2
        F0 = 1.0
        
        def _5pl(x, A, B, C, D, F):
            return D + (A - D) / (1 + (C / x) ** B) ** F
        
        try:
            popt, _ = curve_fit(_5pl, x, y, p0=[A0, B0, C0, D0, F0], maxfev=5000)
            self.fit_params["5pl_params"] = {
                "A": popt[0], "B": popt[1], "C": popt[2], "D": popt[3], "F": popt[4]
            }
        except Exception as e:
            print(f"Error en ajuste 5PL: {e}")
            self.fit_params["5pl_params"] = {"A": A0, "B": B0, "C": C0, "D": D0, "F": F0}
    
    def _inverse_5pl(self, y_value: float) -> float:
        """Calcula x a partir de y usando el modelo 5PL."""
        params = self.fit_params.get("5pl_params", {})
        A = params.get("A", 1)
        B = params.get("B", 1)
        C = params.get("C", 1)
        D = params.get("D", 0)
        F = params.get("F", 1)
        
        if y_value <= D:
            return 0.0
        if y_value >= A:
            return 1000.0
        
        try:
            term = ((A - D) / (y_value - D)) ** (1 / F) - 1
            if term > 0:
                return C / (term ** (1 / B))
            else:
                return 1000.0
        except:
            return 1000.0
    
    def _interpolate(self, fluorescence: float) -> Optional[float]:
        """Aplica la función de interpolación construida."""
        if self.interpolation_function is None:
            return None
        try:
            return self.interpolation_function(fluorescence)
        except:
            return None
    
    # ============================================================
    #   INTERPRETACIÓN DE RESULTADOS
    # ============================================================
    
    def interpret_results(self):
        """Interpreta los resultados según el punto de corte."""
        if not self.control_valid and not (self.control_lower == 0 and self.control_upper == 0):
            for sample in self.samples:
                sample["interpretation"] = ""
            return
        
        last_calib_fluor = self.calibrators["F"]["mean"]
        
        for sample in self.samples:
            if sample["concentration"] is None:
                sample["interpretation"] = "ERROR"
                continue
            
            if sample["mean_fluor"] > last_calib_fluor:
                sample["interpretation"] = "> Ult. Punto"
                sample["concentration"] = None
                continue
            
            conc = sample["concentration"]
            if conc < self.cutoff:
                sample["interpretation"] = ""
            else:
                sample["interpretation"] = "Elevado"
    
    # ============================================================
    #   REPORTES
    # ============================================================
    
    def get_calibration_status(self) -> str:
        if not self.calibration_valid:
            return "CURVA DE CALIBRACIÓN RECHAZADA, REPITA EL ENSAYO"
        return "Curva de calibración válida"
    
    def get_control_status(self) -> str:
        if not self.control_valid and not (self.control_lower == 0 and self.control_upper == 0):
            return "SUERO CONTROL FUERA DE RANGO. SUGERIMOS REPETIR EL ENSAYO"
        return "Control válido"
    
    def get_summary(self) -> Dict:
        summary = {
            "cutoff": self.cutoff,
            "control_lower": self.control_lower,
            "control_upper": self.control_upper,
            "calibration_valid": self.calibration_valid,
            "control_valid": self.control_valid,
            "overall_valid": self.valid,
            "validation_message": self.validation_message,
            "current_method": self.current_method,
            "calibrators": {},
            "assay_control": {},
            "samples": []
        }
        
        for cal, data in self.calibrators.items():
            summary["calibrators"][cal] = {
                "concentration": data["conc"],
                "fluor1": data["well1"],
                "fluor2": data["well2"],
                "mean": data["mean"]
            }
        
        summary["assay_control"] = {
            "fluor1": self.assay_control["well1"],
            "fluor2": self.assay_control["well2"],
            "mean": self.assay_control["mean"]
        }
        
        for i, sample in enumerate(self.samples, 1):
            summary["samples"].append({
                "number": i,
                "wells": f"{sample['well1_coord']}-{sample['well2_coord']}",
                "fluor1": sample["fluor1"],
                "fluor2": sample["fluor2"],
                "mean_fluor": sample["mean_fluor"],
                "concentration": sample["concentration"],
                "interpretation": sample["interpretation"],
                "needs_repeat": sample["needs_repeat"],
                "repeat_reason": sample["repeat_reason"]
            })
        
        return summary
    
    def __repr__(self):
        status = "VÁLIDO" if self.valid else "NO VÁLIDO"
        return f"<AssayModel corte={self.cutoff} {status} muestras={len(self.samples)} método={self.current_method}>"