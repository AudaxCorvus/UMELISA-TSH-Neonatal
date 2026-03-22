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