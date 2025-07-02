"""
Clases base y utilidades para cálculos petrofísicos
===================================================

Proporciona funcionalidades comunes para todos los calculadores petrofísicos
incluyendo validación de datos, estadísticas QC y manejo de errores.
"""

import numpy as np
import pandas as pd
from typing import Union, Optional, Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)

class PetrophysicsCalculator:
    """
    Clase base para todos los calculadores petrofísicos.
    
    Proporciona:
    - Validación de datos de entrada
    - Estadísticas de control de calidad (QC)
    - Manejo consistente de errores y warnings
    - Tracking de cálculos realizados
    """
    
    def __init__(self):
        self.last_calculation = None
        self.validation_warnings = []
        self.calculation_history = []
    
    def validate_input(self, 
                      data: Union[np.ndarray, pd.Series], 
                      curve_name: str, 
                      valid_range: Optional[Tuple[float, float]] = None) -> np.ndarray:
        """
        Valida datos de entrada para cálculos petrofísicos.
        
        Args:
            data: Datos de la curva (numpy array o pandas Series)
            curve_name: Nombre de la curva para logging
            valid_range: Rango válido (min, max) opcional
            
        Returns:
            np.ndarray: Datos validados como numpy array
            
        Raises:
            ValueError: Si no hay datos válidos
        """
        # Convertir a numpy array
        if isinstance(data, pd.Series):
            data = data.values
        data = np.asarray(data, dtype=float)
        
        # Verificar datos vacíos
        if len(data) == 0:
            raise ValueError(f"No hay datos para la curva {curve_name}")
        
        # Contar valores nulos
        null_count = np.isnan(data).sum()
        total_count = len(data)
        null_percentage = (null_count / total_count) * 100
        
        if null_count > 0:
            warning = (f"Curva {curve_name}: {null_count} valores nulos "
                      f"({null_percentage:.1f}%) encontrados")
            self.validation_warnings.append(warning)
            logger.warning(warning)
        
        # Validar rango si se especifica
        if valid_range:
            min_val, max_val = valid_range
            valid_data = data[~np.isnan(data)]
            
            if len(valid_data) > 0:
                data_min, data_max = valid_data.min(), valid_data.max()
                
                if data_min < min_val or data_max > max_val:
                    warning = (f"Curva {curve_name}: valores fuera del rango válido "
                              f"[{min_val}, {max_val}]. Rango actual: "
                              f"[{data_min:.2f}, {data_max:.2f}]")
                    self.validation_warnings.append(warning)
                    logger.warning(warning)
        
        return data
    
    def get_qc_stats(self, calculated_data: np.ndarray, curve_name: str) -> Dict:
        """
        Genera estadísticas de control de calidad para datos calculados.
        
        Args:
            calculated_data: Datos calculados
            curve_name: Nombre de la curva calculada
            
        Returns:
            Dict: Estadísticas completas de QC
        """
        valid_data = calculated_data[~np.isnan(calculated_data)]
        
        if len(valid_data) == 0:
            return {
                "curve_name": curve_name,
                "error": "No hay datos válidos calculados",
                "total_points": len(calculated_data),
                "valid_points": 0
            }
        
        stats = {
            "curve_name": curve_name,
            "total_points": len(calculated_data),
            "valid_points": len(valid_data),
            "null_count": len(calculated_data) - len(valid_data),
            "null_percentage": ((len(calculated_data) - len(valid_data)) / 
                               len(calculated_data)) * 100,
            "min": float(valid_data.min()),
            "max": float(valid_data.max()),
            "mean": float(valid_data.mean()),
            "median": float(np.median(valid_data)),
            "std": float(valid_data.std()),
            "variance": float(valid_data.var()),
            "p10": float(np.percentile(valid_data, 10)),
            "p25": float(np.percentile(valid_data, 25)),
            "p50": float(np.percentile(valid_data, 50)),
            "p75": float(np.percentile(valid_data, 75)),
            "p90": float(np.percentile(valid_data, 90)),
            "range": float(valid_data.max() - valid_data.min())
        }
        
        return stats
    
    def validate_parameters(self, **params) -> Dict:
        """
        Valida parámetros de entrada para cálculos.
        
        Args:
            **params: Parámetros a validar
            
        Returns:
            Dict: Parámetros validados
        """
        validated = {}
        
        for key, value in params.items():
            if value is None:
                continue
                
            if isinstance(value, (int, float)):
                if np.isnan(value) or np.isinf(value):
                    raise ValueError(f"Parámetro {key} contiene valores no válidos")
                validated[key] = float(value)
            else:
                validated[key] = value
        
        return validated
    
    def add_to_history(self, calculation_result: Dict):
        """
        Añade un cálculo al historial.
        
        Args:
            calculation_result: Resultado del cálculo a guardar
        """
        import datetime
        
        history_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "calculation_type": calculation_result.get("type", "unknown"),
            "parameters": calculation_result.get("parameters", {}),
            "qc_stats": calculation_result.get("qc_stats", {}),
            "warnings": calculation_result.get("warnings", [])
        }
        
        self.calculation_history.append(history_entry)
        
        # Limitar historial a últimos 100 cálculos
        if len(self.calculation_history) > 100:
            self.calculation_history = self.calculation_history[-100:]
    
    def get_calculation_summary(self) -> Dict:
        """
        Obtiene un resumen de todos los cálculos realizados.
        
        Returns:
            Dict: Resumen del historial de cálculos
        """
        if not self.calculation_history:
            return {"message": "No hay cálculos en el historial"}
        
        calculation_types = [calc["calculation_type"] for calc in self.calculation_history]
        
        summary = {
            "total_calculations": len(self.calculation_history),
            "calculation_types": list(set(calculation_types)),
            "type_counts": {calc_type: calculation_types.count(calc_type) 
                           for calc_type in set(calculation_types)},
            "last_calculation": self.calculation_history[-1]["timestamp"],
            "first_calculation": self.calculation_history[0]["timestamp"]
        }
        
        return summary
    
    def clear_warnings(self):
        """Limpia las advertencias de validación."""
        self.validation_warnings.clear()
    
    def clear_history(self):
        """Limpia el historial de cálculos."""
        self.calculation_history.clear()
