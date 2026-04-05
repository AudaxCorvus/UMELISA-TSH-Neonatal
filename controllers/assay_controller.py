"""
Controlador para el ensayo UMELISA TSH Neonatal.
"""

from models.assay_model import AssayModel
from models.plate_model import PlateModel


class AssayController:
    def __init__(self):
        self.current_assay = None
        self.current_method = "semilog_piecewise"

    def load_flu_file(self, filepath: str) -> PlateModel:
        rows = "ABCDEFGH"
        cols = range(1, 13)
        
        current_plate = PlateModel(plate_name=filepath)

        with open(filepath, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        normalized = []
        for line in lines:
            clean = line.replace(",", ".")
            try:
                value = float(clean)
            except ValueError:
                value = 0.0
            normalized.append(value)

        while len(normalized) < 96:
            normalized.append(0.0)

        index = 0
        for c in cols:
            for r in rows:
                well_id = f"{r}{c}"
                current_plate.set_well_value(well_id, normalized[index])
                index += 1

        return current_plate

    def new_assay(self, plate: PlateModel, cutoff: float,
                  control_lower: float, control_upper: float,
                  calibrators: dict) -> AssayModel:
        if plate.is_empty():
            raise ValueError("La placa está vacía. No se puede crear el ensayo.")

        self.current_assay = AssayModel(
            plate,
            cutoff=cutoff,
            control_lower=control_lower,
            control_upper=control_upper,
            calibrators=calibrators
        )
        return self.current_assay

    def calculate_concentrations(self, method: str = "semilog_piecewise") -> bool:
        if not self.current_assay:
            raise ValueError("No hay un ensayo cargado.")
        self.current_method = method
        return self.current_assay.calculate_concentrations(method)

    def interpret_assay(self):
        if not self.current_assay:
            raise ValueError("No hay un ensayo cargado.")
        self.current_assay.interpret_results()
        return self.current_assay.samples

    def get_summary(self) -> dict:
        if not self.current_assay:
            raise ValueError("No hay ensayo disponible para resumir.")
        return self.current_assay.get_summary()
    
    # ============================================================
    #   NUEVO: Métodos para punto de corte por percentil 99
    # ============================================================
    
    def calculate_percentile_99_cutoff(self, use_historical: bool = True):
        """
        Calcula el punto de corte usando percentil 99 de las muestras normales.
        """
        if not self.current_assay:
            raise ValueError("No hay un ensayo cargado.")
        
        from controllers.cutoff_controller import CutoffController
        cutoff_ctrl = CutoffController()
        
        return cutoff_ctrl.calculate_percentile_99_cutoff(
            self.current_assay, 
            use_historical=use_historical
        )
    
    def get_cutoff_statistics(self, use_historical: bool = True):
        """
        Obtiene estadísticas para el cálculo del punto de corte.
        """
        if not self.current_assay:
            raise ValueError("No hay un ensayo cargado.")
        
        from controllers.cutoff_controller import CutoffController
        cutoff_ctrl = CutoffController()
        
        return cutoff_ctrl.get_cutoff_statistics(
            self.current_assay,
            use_historical=use_historical
        )
    
    def apply_new_cutoff(self, new_cutoff: float) -> bool:
        """
        Aplica un nuevo punto de corte al ensayo actual.
        """
        if not self.current_assay:
            raise ValueError("No hay un ensayo cargado.")
        
        from controllers.cutoff_controller import CutoffController
        cutoff_ctrl = CutoffController()
        
        return cutoff_ctrl.apply_cutoff_to_assay(self.current_assay, new_cutoff)
    
    # ============================================================
#   NUEVO: Guardado automático al cargar placa
# ============================================================

def save_current_plate_to_history(self, plate_file: str = None) -> bool:
    """
    Guarda la placa actual en el histórico.
    Se llama automáticamente después de cargar una placa.
    """
    if not self.current_assay:
        return False
    
    from controllers.cutoff_controller import CutoffController
    cutoff_ctrl = CutoffController()
    return cutoff_ctrl.save_plate_to_history(self.current_assay, plate_file)