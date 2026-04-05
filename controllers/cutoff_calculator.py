"""
Calculadora de punto de corte usando percentil 99.
"""

import numpy as np
from typing import List, Dict, Optional


class CutoffCalculator:
    """
    Calcula el punto de corte utilizando el percentil 99 de los valores de TSH.
    """
    
    @staticmethod
    def calculate_from_samples(samples: List[Dict], 
                               exclude_elevated: bool = True,
                               min_samples: int = 30) -> Optional[float]:
        """
        Calcula el percentil 99 a partir de las concentraciones de las muestras.
        
        Args:
            samples: Lista de muestras del ensayo (cada una con 'concentration')
            exclude_elevated: Si es True, excluye muestras marcadas como "Elevado"
            min_samples: Número mínimo de muestras requeridas para el cálculo
        
        Returns:
            Valor del percentil 99 o None si no hay suficientes muestras
        """
        # Extraer concentraciones válidas
        concentrations = []
        
        for sample in samples:
            conc = sample.get('concentration')
            interpretation = sample.get('interpretation', '')
            
            # Solo incluir concentraciones válidas y no nulas
            if conc is None:
                continue
            
            # Excluir muestras elevadas si se solicita
            if exclude_elevated and interpretation == "Elevado":
                continue
            
            # Excluir muestras > Ult. Punto
            if interpretation == "> Ult. Punto":
                continue
            
            concentrations.append(conc)
        
        if len(concentrations) < min_samples:
            return None
        
        # Calcular percentil 99
        percentile_99 = np.percentile(concentrations, 99)
        
        return round(percentile_99, 2)
    
    @staticmethod
    def calculate_from_normal_distribution(mean: float, 
                                            std: float,
                                            percentile: float = 99) -> float:
        """
        Calcula el percentil a partir de una distribución normal.
        
        Args:
            mean: Media de la población normal
            std: Desviación estándar
            percentile: Percentil deseado (default: 99)
        
        Returns:
            Valor del percentil calculado
        """
        from scipy import stats
        z_score = stats.norm.ppf(percentile / 100)
        return round(mean + z_score * std, 2)
    
    @staticmethod
    def get_recommended_cutoff(historical_data: List[float],
                                method: str = "percentile_99") -> Dict:
        """
        Calcula punto de corte recomendado basado en datos históricos.
        
        Args:
            historical_data: Lista de concentraciones históricas de población normal
            method: Método de cálculo ('percentile_99' o 'mean_3sd')
        
        Returns:
            Diccionario con el punto de corte y estadísticas
        """
        if not historical_data:
            return {"cutoff": None, "message": "No hay datos históricos"}
        
        data = np.array(historical_data)
        
        if method == "percentile_99":
            cutoff = np.percentile(data, 99)
            method_name = "Percentil 99"
        elif method == "mean_3sd":
            mean = np.mean(data)
            std = np.std(data)
            cutoff = mean + 3 * std
            method_name = "Media + 3DS"
        else:
            cutoff = np.percentile(data, 99)
            method_name = "Percentil 99"
        
        return {
            "cutoff": round(cutoff, 2),
            "method": method_name,
            "n_samples": len(data),
            "mean": round(np.mean(data), 2),
            "std": round(np.std(data), 2),
            "min_value": round(np.min(data), 2),
            "max_value": round(np.max(data), 2),
            "percentile_95": round(np.percentile(data, 95), 2),
            "percentile_99": round(np.percentile(data, 99), 2)
        }
    
    @staticmethod
    def validate_cutoff(cutoff: float, 
                        samples: List[Dict],
                        expected_negative_rate: float = 0.99) -> Dict:
        """
        Valida un punto de corte evaluando la tasa de negativos esperada.
        
        Args:
            cutoff: Punto de corte a validar
            samples: Lista de muestras
            expected_negative_rate: Tasa esperada de negativos (default: 99%)
        
        Returns:
            Diccionario con la validación
        """
        if not samples:
            return {"valid": False, "message": "No hay muestras para validar"}
        
        # Excluir muestras > Ult. Punto para el cálculo
        valid_samples = [s for s in samples 
                        if s.get('concentration') is not None 
                        and s.get('interpretation') != "> Ult. Punto"]
        
        if not valid_samples:
            return {"valid": False, "message": "No hay muestras válidas"}
        
        negatives = sum(1 for s in valid_samples 
                       if s.get('concentration', float('inf')) < cutoff)
        
        negative_rate = negatives / len(valid_samples)
        
        return {
            "valid": abs(negative_rate - expected_negative_rate) < 0.05,
            "negative_rate": round(negative_rate * 100, 2),
            "expected_rate": expected_negative_rate * 100,
            "negatives": negatives,
            "total_valid": len(valid_samples),
            "cutoff": cutoff,
            "message": f"Tasa de negativos: {negative_rate*100:.1f}% (esperado: {expected_negative_rate*100:.0f}%)"
        }