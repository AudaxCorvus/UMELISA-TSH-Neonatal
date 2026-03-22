class PlateModel:
    """
    Modelo de datos para representar una placa de laboratorio ya leída.
    Cada pocillo contiene un valor de fluorescencia.
    """

    def __init__(self, plate_name: str):
        self.plate_name = plate_name
        self.wells = {}
        
        self._create_empty_wells()

    # ============================================================
    # MÉTODOS DE INICIALIZACIÓN
    # ============================================================

    def _create_empty_wells(self):
        self.wells = {}
        for col in range(1, 13):
            for row in "ABCDEFGH":
                self.wells[f"{row}{col}"] = 0.0
        return self.wells

    # ============================================================
    # MÉTODOS DE ACCESO Y MANIPULACIÓN
    # ============================================================

    def set_well_value(self, well_id: str, value: float):
        if well_id in self.wells:
            self.wells[well_id] = value
        else:
            raise ValueError(f"Identificador de pocillo inválido: {well_id}")

    def get_well_value(self, well_id: str):
        if well_id in self.wells:
            return self.wells[well_id]
        else:
            raise ValueError(f"Identificador de pocillo inválido: {well_id}")

    def get_all_wells(self):
        return list(self.wells.items())

    def reset_plate(self):
        self.wells = self._create_empty_wells()

    def is_empty(self):
        return all(value == 0.0 for value in self.wells.values())

    # ============================================================
    # REPRESENTACIÓN
    # ============================================================

    def __repr__(self):
        return f"<Plate {self.plate_name}>"