"""
Controlador para cálculo y gestión del punto de corte.
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

from models.plate_model import PlateModel
from models.assay_model import AssayModel


class CutoffController:
    """
    Controlador para recalcular el punto de corte usando percentil 99.
    Guarda automáticamente todas las placas cargadas en un histórico.
    """
    
    def __init__(self, historical_file: str = "historical_data.json"):
        """
        Inicializa el controlador.
        
        Args:
            historical_file: Ruta al archivo JSON con datos históricos
        """
        # Obtener la ruta completa en el directorio del usuario
        self.data_dir = Path.home() / ".umelisa_tsh"
        self.historical_file = self.data_dir / historical_file
        self.historical_data = self._load_historical_data()
    
    def _ensure_data_dir(self):
        """Asegura que el directorio de datos existe."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_historical_data(self) -> Dict:
        """Carga todos los datos históricos desde archivo JSON."""
        self._ensure_data_dir()
        
        if self.historical_file.exists():
            try:
                with open(self.historical_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Verificar estructura
                    if 'plates' not in data:
                        data = {'plates': [], 'all_concentrations': []}
                    if 'all_concentrations' not in data:
                        # Recalcular desde plates si es necesario
                        data['all_concentrations'] = self._extract_normal_concentrations(data.get('plates', []))
                    return data
            except Exception as e:
                print(f"Error cargando datos históricos: {e}")
                return {'plates': [], 'all_concentrations': []}
        return {'plates': [], 'all_concentrations': []}
    
    def _extract_normal_concentrations(self, plates: List[Dict]) -> List[float]:
        """
        Extrae SOLO las concentraciones de muestras NORMALES (no elevadas).
        Esta es la lógica correcta que funcionaba antes.
        """
        concentrations = []
        for plate in plates:
            for sample in plate.get('normal_samples', []):  # Usar 'normal_samples' no 'all_samples'
                conc = sample.get('concentration')
                if conc is not None and conc > 0:
                    concentrations.append(conc)
        return concentrations
    
    def _update_all_concentrations(self):
        """Actualiza la lista completa de concentraciones normales."""
        self.historical_data['all_concentrations'] = self._extract_normal_concentrations(
            self.historical_data.get('plates', [])
        )
    
    def save_plate_to_history(self, assay: AssayModel, plate_file: str = None) -> bool:
        """
        Guarda una placa completa en el histórico.
        SOLO guarda muestras NORMALES para el cálculo del percentil.
        
        Args:
            assay: Modelo de ensayo actual
            plate_file: Nombre del archivo original (opcional)
        
        Returns:
            True si se guardó correctamente
        """
        if not assay or not assay.samples:
            return False
        
        # Separar muestras normales de las elevadas
        normal_samples = []
        all_samples = []
        
        for sample in assay.samples:
            conc = sample.get('concentration')
            interpretation = sample.get('interpretation', '')
            
            sample_info = {
                'well1': sample.get('well1_coord'),
                'well2': sample.get('well2_coord'),
                'fluor1': sample.get('fluor1'),
                'fluor2': sample.get('fluor2'),
                'mean_fluor': sample.get('mean_fluor'),
                'concentration': conc,
                'interpretation': interpretation
            }
            all_samples.append(sample_info)
            
            # SOLO guardar muestras NORMALES para el percentil
            # Excluir "Elevado" y "> Ult. Punto" (misma lógica que funcionaba)
            if conc is not None and interpretation not in ['Elevado', '> Ult. Punto']:
                normal_samples.append(sample_info)
        
        # Crear registro de la placa
        plate_record = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S_%f'),
            'date': datetime.now().isoformat(),
            'file': plate_file,
            'cutoff_used': assay.cutoff,
            'method': assay.current_method,
            'total_samples': len(all_samples),
            'normal_samples': normal_samples,  # Solo las normales
            'all_samples': all_samples,
            'calibration_valid': assay.calibration_valid,
            'control_valid': assay.control_valid
        }
        
        # Agregar al histórico
        self.historical_data['plates'].append(plate_record)
        self._update_all_concentrations()
        self._save_historical_data()
        
        return True
    
    def _save_historical_data(self):
        """Guarda los datos históricos en archivo JSON."""
        self._ensure_data_dir()
        
        data_to_save = {
            'last_updated': datetime.now().isoformat(),
            'total_plates': len(self.historical_data.get('plates', [])),
            'total_normal_samples': len(self.historical_data.get('all_concentrations', [])),
            'plates': self.historical_data.get('plates', []),
            'all_concentrations': self.historical_data.get('all_concentrations', [])
        }
        
        try:
            with open(self.historical_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando datos históricos: {e}")
    
    def load_multiple_flu_files(self, filepaths: List[str], 
                                 cutoff: float = 30.0,
                                 calibrators: Dict = None) -> Tuple[List[Dict], List[str]]:
        """
        Carga múltiples archivos .flu y extrae SOLO muestras NORMALES.
        
        Args:
            filepaths: Lista de rutas de archivos .flu
            cutoff: Punto de corte para interpretación
            calibrators: Concentraciones de calibradores
        
        Returns:
            Tupla con (lista de datos de placas, lista de errores)
        """
        plates_data = []
        errors = []
        
        # Usar calibradores por defecto si no se proporcionan
        if calibrators is None:
            calibrators = {
                "A": 0.520, "B": 10.750, "C": 25.200,
                "D": 49.850, "E": 96.150, "F": 194.000
            }
        
        for filepath in filepaths:
            try:
                # Cargar placa
                plate = self._load_flu_file(filepath)
                if plate.is_empty():
                    errors.append(f"{os.path.basename(filepath)}: Placa vacía")
                    continue
                
                # Crear ensayo con el cutoff proporcionado
                assay = AssayModel(
                    plate,
                    cutoff=cutoff,
                    control_lower=0,
                    control_upper=0,
                    calibrators=calibrators
                )
                
                # Calcular concentraciones con método por defecto
                assay.calculate_concentrations("semilog_piecewise")
                assay.interpret_results()
                
                # SOLO extraer muestras NORMALES (no elevadas, no > Ult. Punto)
                normal_concentrations = []
                normal_samples_info = []
                
                for sample in assay.samples:
                    conc = sample.get('concentration')
                    interpretation = sample.get('interpretation', '')
                    
                    if conc is not None:
                        # Solo incluir si NO es elevada y NO es > Ult. Punto
                        if interpretation not in ['Elevado', '> Ult. Punto']:
                            normal_concentrations.append(conc)
                            normal_samples_info.append({
                                'wells': f"{sample.get('well1_coord')}-{sample.get('well2_coord')}",
                                'concentration': conc,
                                'interpretation': interpretation,
                                'mean_fluor': sample.get('mean_fluor')
                            })
                
                plates_data.append({
                    'file': os.path.basename(filepath),
                    'filepath': filepath,
                    'date_loaded': datetime.now().isoformat(),
                    'normal_concentrations': normal_concentrations,  # Solo normales
                    'normal_samples': normal_samples_info,
                    'total_samples': len(assay.samples),
                    'normal_count': len(normal_concentrations),
                    'elevated_count': sum(1 for s in assay.samples if s.get('interpretation') == 'Elevado'),
                    'above_last_count': sum(1 for s in assay.samples if s.get('interpretation') == '> Ult. Punto')
                })
                
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {str(e)}")
        
        return plates_data, errors
    
    def _load_flu_file(self, filepath: str) -> PlateModel:
        """Carga un archivo .flu y devuelve un PlateModel."""
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
    
    def calculate_percentile_from_loaded_plates(self, plates_data: List[Dict], 
                                                  percentile: float = 99) -> Dict:
        """
        Calcula percentil a partir de las CONCENTRACIONES NORMALES de múltiples placas.
        
        Args:
            plates_data: Lista de datos de placas (de load_multiple_flu_files)
            percentile: Percentil a calcular (default: 99)
        
        Returns:
            Diccionario con resultados del cálculo
        """
        import numpy as np
        
        # Recolectar SOLO concentraciones NORMALES
        all_normal_concentrations = []
        plates_summary = []
        
        for plate in plates_data:
            all_normal_concentrations.extend(plate['normal_concentrations'])
            plates_summary.append({
                'file': plate['file'],
                'total_samples': plate['total_samples'],
                'normal_count': plate['normal_count'],
                'elevated_count': plate.get('elevated_count', 0),
                'above_last_count': plate.get('above_last_count', 0),
                'min_conc': min(plate['normal_concentrations']) if plate['normal_concentrations'] else 0,
                'max_conc': max(plate['normal_concentrations']) if plate['normal_concentrations'] else 0,
                'mean_conc': np.mean(plate['normal_concentrations']) if plate['normal_concentrations'] else 0
            })
        
        if len(all_normal_concentrations) < 10:
            return {
                'success': False,
                'message': f'Se necesitan al menos 10 muestras NORMALES. Actuales: {len(all_normal_concentrations)}',
                'total_normal_samples': len(all_normal_concentrations),
                'total_plates': len(plates_data)
            }
        
        # Calcular estadísticas
        data = np.array(all_normal_concentrations)
        
        result = {
            'success': True,
            'percentile_value': round(np.percentile(data, percentile), 2),
            'percentile': percentile,
            'total_normal_samples': len(all_normal_concentrations),
            'total_plates': len(plates_data),
            'total_samples': sum(p['total_samples'] for p in plates_data),
            'total_elevated': sum(p.get('elevated_count', 0) for p in plates_data),
            'total_above_last': sum(p.get('above_last_count', 0) for p in plates_data),
            'statistics': {
                'mean': round(np.mean(data), 2),
                'std': round(np.std(data), 2),
                'min': round(np.min(data), 2),
                'max': round(np.max(data), 2),
                'median': round(np.median(data), 2),
                'percentile_95': round(np.percentile(data, 95), 2),
                'percentile_97_5': round(np.percentile(data, 97.5), 2),
                'percentile_99': round(np.percentile(data, 99), 2),
                'percentile_99_5': round(np.percentile(data, 99.5), 2)
            },
            'plates_summary': plates_summary
        }
        
        return result
    
    def calculate_percentile_from_history(self, percentile: float = 99) -> Dict:
        """
        Calcula percentil a partir de los datos históricos (SOLO muestras normales).
        
        Args:
            percentile: Percentil a calcular (default: 99)
        
        Returns:
            Diccionario con resultados del cálculo
        """
        import numpy as np
        
        concentrations = self.historical_data.get('all_concentrations', [])
        
        if len(concentrations) < 10:
            return {
                'success': False,
                'message': f'Se necesitan al menos 10 muestras NORMALES en el historial. Actuales: {len(concentrations)}',
                'total_normal_samples': len(concentrations),
                'total_plates': len(self.historical_data.get('plates', []))
            }
        
        data = np.array(concentrations)
        
        result = {
            'success': True,
            'percentile_value': round(np.percentile(data, percentile), 2),
            'percentile': percentile,
            'total_normal_samples': len(concentrations),
            'total_plates': len(self.historical_data.get('plates', [])),
            'statistics': {
                'mean': round(np.mean(data), 2),
                'std': round(np.std(data), 2),
                'min': round(np.min(data), 2),
                'max': round(np.max(data), 2),
                'median': round(np.median(data), 2),
                'percentile_95': round(np.percentile(data, 95), 2),
                'percentile_97_5': round(np.percentile(data, 97.5), 2),
                'percentile_99': round(np.percentile(data, 99), 2),
                'percentile_99_5': round(np.percentile(data, 99.5), 2)
            },
            'history_summary': {
                'oldest_plate': self.historical_data['plates'][0]['date'] if self.historical_data['plates'] else None,
                'newest_plate': self.historical_data['plates'][-1]['date'] if self.historical_data['plates'] else None
            }
        }
        
        return result
    
    def get_history_summary(self) -> Dict:
        """Obtiene un resumen del historial guardado."""
        plates = self.historical_data.get('plates', [])
        concentrations = self.historical_data.get('all_concentrations', [])
        
        return {
            'total_plates': len(plates),
            'total_normal_samples': len(concentrations),
            'plates_list': [
                {
                    'id': p.get('id'),
                    'date': p.get('date'),
                    'file': p.get('file'),
                    'normal_count': len(p.get('normal_samples', [])),
                    'total_count': len(p.get('all_samples', []))
                }
                for p in plates
            ],
            'statistics': self._calculate_basic_stats(concentrations) if concentrations else None
        }
    
    def _calculate_basic_stats(self, concentrations: List[float]) -> Dict:
        """Calcula estadísticas básicas."""
        if not concentrations:
            return None
        import numpy as np
        data = np.array(concentrations)
        return {
            'mean': round(np.mean(data), 2),
            'std': round(np.std(data), 2),
            'min': round(np.min(data), 2),
            'max': round(np.max(data), 2),
            'percentile_99': round(np.percentile(data, 99), 2)
        }
    
    def clear_history(self) -> bool:
        """Limpia todo el historial de datos."""
        self.historical_data = {'plates': [], 'all_concentrations': []}
        self._save_historical_data()
        return True
    
    def delete_plate_from_history(self, plate_id: str) -> bool:
        """Elimina una placa específica del historial."""
        plates = self.historical_data.get('plates', [])
        initial_count = len(plates)
        
        self.historical_data['plates'] = [p for p in plates if p.get('id') != plate_id]
        
        if len(self.historical_data['plates']) < initial_count:
            self._update_all_concentrations()
            self._save_historical_data()
            return True
        return False
    
    def get_historical_concentrations(self) -> List[float]:
        """Devuelve todas las concentraciones normales del historial."""
        return self.historical_data.get('all_concentrations', [])
    
    # ============================================================
    #   MÉTODOS PARA COMPATIBILIDAD CON LA VERSIÓN ANTERIOR
    # ============================================================
    
    def get_cutoff_statistics(self, assay: Optional[AssayModel] = None,
                               use_historical: bool = True) -> Dict:
        """
        Obtiene estadísticas para el cálculo del punto de corte.
        Compatible con la versión anterior que funcionaba.
        """
        concentrations = []
        
        # Agregar muestras NORMALES del ensayo actual
        if assay and assay.samples:
            for sample in assay.samples:
                conc = sample.get('concentration')
                interpretation = sample.get('interpretation', '')
                
                # SOLO muestras no elevadas y no > Ult. Punto
                if conc is not None and interpretation not in ['Elevado', '> Ult. Punto']:
                    concentrations.append(conc)
        
        # Agregar datos históricos si se solicita
        if use_historical:
            concentrations.extend(self.historical_data.get('all_concentrations', []))
        
        if not concentrations:
            return {
                "available": False,
                "message": "No hay datos disponibles para calcular estadísticas"
            }
        
        import numpy as np
        data = np.array(concentrations)
        
        return {
            "available": True,
            "n_samples": len(data),
            "mean": round(np.mean(data), 2),
            "std": round(np.std(data), 2),
            "min": round(np.min(data), 2),
            "max": round(np.max(data), 2),
            "percentile_95": round(np.percentile(data, 95), 2),
            "percentile_97_5": round(np.percentile(data, 97.5), 2),
            "percentile_99": round(np.percentile(data, 99), 2),
            "percentile_99_5": round(np.percentile(data, 99.5), 2),
            "historical_included": use_historical and len(self.historical_data.get('all_concentrations', [])) > 0,
            "historical_count": len(self.historical_data.get('all_concentrations', [])),
            "current_count": len(concentrations) - len(self.historical_data.get('all_concentrations', [])) if use_historical else len(concentrations)
        }
    
    def suggest_cutoff(self, assay: Optional[AssayModel] = None) -> Dict:
        """
        Sugiere un punto de corte basado en percentil 99.
        Compatible con la versión anterior que funcionaba.
        """
        stats = self.get_cutoff_statistics(assay, use_historical=True)
        
        if not stats.get("available"):
            return {
                "success": False,
                "message": "No hay suficientes datos. Se necesitan al menos 30 muestras normales.",
                "suggested_cutoff": None
            }
        
        if stats["n_samples"] < 30:
            return {
                "success": False,
                "message": f"Solo {stats['n_samples']} muestras disponibles. Se necesitan al menos 30.",
                "suggested_cutoff": None,
                "statistics": stats
            }
        
        suggested_cutoff = stats["percentile_99"]
        
        # Validar rango razonable
        if suggested_cutoff < 10:
            suggested_cutoff = 10.0
            warning = "El cálculo resultó muy bajo, se sugiere 10.0 como mínimo."
        elif suggested_cutoff > 100:
            suggested_cutoff = 100.0
            warning = "El cálculo resultó muy alto, se sugiere 100.0 como máximo."
        else:
            warning = None
        
        return {
            "success": True,
            "suggested_cutoff": suggested_cutoff,
            "current_cutoff": assay.cutoff if assay else None,
            "method": "Percentil 99 (población normal)",
            "statistics": stats,
            "warning": warning,
            "message": f"Punto de corte sugerido: {suggested_cutoff:.2f} mUI/L basado en {stats['n_samples']} muestras normales"
        }
    
    def apply_cutoff_to_assay(self, assay: AssayModel, new_cutoff: float) -> bool:
        """Aplica un nuevo punto de corte a un ensayo."""
        if not assay:
            return False
        assay.cutoff = new_cutoff
        assay.interpret_results()
        return True