"""
Cálculos de Volumen de Arcilla (VCL)
====================================

Implementa métodos estándar de la industria para calcular volumen de arcilla
desde registros de Gamma Ray, incluyendo:

- Método Lineal
- Larionov (rocas antiguas y terciarias)  
- Clavier
- Steiber

Todos los métodos validan rangos y proporcionan estadísticas QC.
"""

import numpy as np
from typing import Optional, Dict, Literal, Union, List
import logging
from .base import PetrophysicsCalculator

logger = logging.getLogger(__name__)

class VclCalculator(PetrophysicsCalculator):
    """
    Calculadora de Volumen de Arcilla desde registros de Gamma Ray.
    
    Implementa los métodos más utilizados en la industria petrolífera
    para determinar el contenido de arcilla en formaciones geológicas.
    """
    
    def __init__(self):
        super().__init__()
        self.methods = {
            'linear': self._linear,
            'larionov_older': self._larionov_older,
            'larionov_tertiary': self._larionov_tertiary,
            'clavier': self._clavier,
            'steiber': self._steiber
        }
        self.method_descriptions = {
            'linear': 'Relación lineal: VCL = IGR',
            'larionov_older': 'Larionov para rocas Pre-Terciarias: VCL = 0.33*(2^(2*IGR) - 1)',
            'larionov_tertiary': 'Larionov para rocas Terciarias: VCL = 0.083*(2^(3.7*IGR) - 1)',
            'clavier': 'Clavier: VCL = 1.7 - sqrt(3.38 - (IGR + 0.7)^2)',
            'steiber': 'Steiber: VCL = IGR / (3 - 2*IGR)'
        }
    
    def calculate(self, 
                 gamma_ray: Union[np.ndarray, List[float]],
                 gr_clean: Optional[float] = None,
                 gr_clay: Optional[float] = None,
                 method: Literal['linear', 'larionov_older', 'larionov_tertiary', 
                               'clavier', 'steiber'] = 'larionov_tertiary',
                 auto_percentiles: bool = True,
                 percentiles: tuple = (5, 95)) -> Dict:
        """
        Calcula volumen de arcilla desde Gamma Ray.
        
        Args:
            gamma_ray: Valores de Gamma Ray [API units]
            gr_clean: Gamma Ray de arena limpia [API] (opcional si auto_percentiles=True)
            gr_clay: Gamma Ray de arcilla pura [API] (opcional si auto_percentiles=True)
            method: Método de cálculo a utilizar
            auto_percentiles: Si True, calcula GR_clean y GR_clay automáticamente
            percentiles: Percentiles para cálculo automático (clean, clay)
            
        Returns:
            Dict con resultados del cálculo, parámetros utilizados y estadísticas QC
            
        Raises:
            ValueError: Si los parámetros son inválidos o no hay datos suficientes
        """
        # Limpiar warnings previos
        self.clear_warnings()
        
        # Validar entrada de Gamma Ray
        gr = self.validate_input(gamma_ray, "Gamma Ray", (0, 1000))
        
        # Obtener datos válidos para cálculos de percentiles
        valid_gr = gr[~np.isnan(gr)]
        if len(valid_gr) == 0:
            raise ValueError("No hay valores válidos de Gamma Ray para calcular VCL")
        
        # Determinar GR_clean y GR_clay
        if auto_percentiles or gr_clean is None or gr_clay is None:
            p_clean, p_clay = percentiles
            calculated_gr_clean = np.percentile(valid_gr, p_clean)
            calculated_gr_clay = np.percentile(valid_gr, p_clay)
            
            # Usar valores calculados si no se proporcionaron
            gr_clean = gr_clean if gr_clean is not None else calculated_gr_clean
            gr_clay = gr_clay if gr_clay is not None else calculated_gr_clay
            
            logger.info(f"Percentiles calculados - GR_clean (P{p_clean}): {calculated_gr_clean:.2f}, "
                       f"GR_clay (P{p_clay}): {calculated_gr_clay:.2f}")
        
        # Validar parámetros
        validated_params = self.validate_parameters(
            gr_clean=gr_clean, 
            gr_clay=gr_clay
        )
        gr_clean, gr_clay = validated_params['gr_clean'], validated_params['gr_clay']
        
        # Verificar que gr_clay > gr_clean
        if gr_clay <= gr_clean:
            raise ValueError(
                f"GR_clay ({gr_clay:.2f}) debe ser mayor que GR_clean ({gr_clean:.2f}). "
                f"Diferencia actual: {gr_clay - gr_clean:.2f}"
            )
        
        # Calcular IGR (Gamma Ray Index)
        igr = self._calculate_igr(gr, gr_clean, gr_clay)
        
        # Validar método
        if method not in self.methods:
            available_methods = list(self.methods.keys())
            raise ValueError(
                f"Método '{method}' no válido. Métodos disponibles: {available_methods}"
            )
        
        # Aplicar método seleccionado para calcular VCL
        try:
            vcl = self.methods[method](igr)
        except Exception as e:
            raise ValueError(f"Error en el cálculo usando método '{method}': {str(e)}")
        
        # Asegurar que VCL esté en rango válido [0, 1]
        vcl = np.clip(vcl, 0, 1)
        
        # Generar estadísticas QC
        qc_stats = self.get_qc_stats(vcl, f"VCL_{method}")
        igr_stats = self.get_qc_stats(igr, "IGR")
        
        # Preparar resultado completo
        result = {
            'type': 'vcl_calculation',
            'vcl': vcl,
            'igr': igr,
            'parameters': {
                'method': method,
                'method_description': self.method_descriptions[method],
                'gr_clean': gr_clean,
                'gr_clay': gr_clay,
                'auto_percentiles': auto_percentiles,
                'percentiles_used': percentiles,
                'gr_range': gr_clay - gr_clean
            },
            'input_stats': {
                'gamma_ray': self.get_qc_stats(gr, "Gamma_Ray")
            },
            'qc_stats': {
                'vcl': qc_stats,
                'igr': igr_stats
            },
            'warnings': self.validation_warnings.copy(),
            'quality_flags': self._assess_quality(vcl, igr, gr_clean, gr_clay)
        }
        
        # Guardar cálculo
        self.last_calculation = result
        self.add_to_history(result)
        
        return result
    
    def _calculate_igr(self, gr: np.ndarray, gr_clean: float, gr_clay: float) -> np.ndarray:
        """
        Calcula el Índice de Gamma Ray (IGR).
        
        Args:
            gr: Valores de Gamma Ray
            gr_clean: Valor de arena limpia
            gr_clay: Valor de arcilla pura
            
        Returns:
            np.ndarray: Valores de IGR normalizados entre 0 y 1
        """
        igr = (gr - gr_clean) / (gr_clay - gr_clean)
        return np.clip(igr, 0, 1)
    
    def _linear(self, igr: np.ndarray) -> np.ndarray:
        """
        Método lineal: VCL = IGR.
        
        El más simple, asume relación lineal directa entre IGR y VCL.
        Generalmente subestima el volumen de arcilla.
        """
        return igr.copy()
    
    def _larionov_older(self, igr: np.ndarray) -> np.ndarray:
        """
        Método Larionov para rocas antiguas (Pre-Terciario).
        VCL = 0.33 * (2^(2*IGR) - 1)
        
        Apropiado para rocas consolidadas y formaciones antiguas.
        """
        return 0.33 * (2**(2*igr) - 1)
    
    def _larionov_tertiary(self, igr: np.ndarray) -> np.ndarray:
        """
        Método Larionov para rocas terciarias (jóvenes).
        VCL = 0.083 * (2^(3.7*IGR) - 1)
        
        Más apropiado para formaciones terciarias poco consolidadas.
        """
        return 0.083 * (2**(3.7*igr) - 1)
    
    def _clavier(self, igr: np.ndarray) -> np.ndarray:
        """
        Método Clavier.
        VCL = 1.7 - sqrt(3.38 - (IGR + 0.7)^2)
        
        Desarrollado empíricamente, funciona bien en muchas formaciones.
        """
        # Proteger contra valores que podrían dar raíz negativa
        discriminant = 3.38 - (igr + 0.7)**2
        discriminant = np.maximum(discriminant, 0)  # Evitar raíces negativas
        
        return 1.7 - np.sqrt(discriminant)
    
    def _steiber(self, igr: np.ndarray) -> np.ndarray:
        """
        Método Steiber.
        VCL = IGR / (3 - 2*IGR)
        
        Útil para formaciones con alta radioactividad.
        """
        # Evitar división por cero y valores negativos en denominador
        denominator = 3 - 2*igr
        denominator = np.where(denominator <= 0, 1e-10, denominator)
        
        return igr / denominator
    
    def batch_calculate(self, 
                       gamma_ray: Union[np.ndarray, List[float]], 
                       methods: Optional[List[str]] = None, 
                       **kwargs) -> Dict:
        """
        Calcula VCL usando múltiples métodos para comparación.
        
        Args:
            gamma_ray: Valores de Gamma Ray
            methods: Lista de métodos a usar (None = todos los métodos)
            **kwargs: Argumentos adicionales para calculate()
            
        Returns:
            Dict con resultados de todos los métodos solicitados
        """
        if methods is None:
            methods = list(self.methods.keys())
        
        # Validar que todos los métodos solicitados existan
        invalid_methods = [m for m in methods if m not in self.methods]
        if invalid_methods:
            raise ValueError(f"Métodos inválidos: {invalid_methods}. "
                           f"Métodos disponibles: {list(self.methods.keys())}")
        
        results = {}
        base_params = kwargs.copy()
        
        for method in methods:
            try:
                result = self.calculate(gamma_ray, method=method, **base_params)
                results[method] = result
                
                logger.info(f"Método {method} calculado exitosamente")
                
            except Exception as e:
                error_msg = f"Error en método {method}: {str(e)}"
                results[method] = {
                    'error': error_msg,
                    'method': method
                }
                logger.error(error_msg)
        
        # Agregar comparación si hay múltiples resultados exitosos
        successful_results = {k: v for k, v in results.items() 
                            if 'error' not in v}
        
        if len(successful_results) > 1:
            results['comparison'] = self._compare_methods(successful_results)
        
        return results
    
    def _compare_methods(self, results: Dict) -> Dict:
        """
        Compara resultados de múltiples métodos.
        
        Args:
            results: Resultados de diferentes métodos
            
        Returns:
            Dict con estadísticas comparativas
        """
        comparison = {
            'methods_compared': list(results.keys()),
            'vcl_statistics': {},
            'correlations': {}
        }
        
        # Recopilar todos los valores VCL
        vcl_data = {}
        for method, result in results.items():
            vcl_data[method] = result['vcl']
        
        # Calcular estadísticas comparativas
        for method, vcl in vcl_data.items():
            valid_vcl = vcl[~np.isnan(vcl)]
            if len(valid_vcl) > 0:
                comparison['vcl_statistics'][method] = {
                    'mean': float(np.mean(valid_vcl)),
                    'std': float(np.std(valid_vcl)),
                    'min': float(np.min(valid_vcl)),
                    'max': float(np.max(valid_vcl))
                }
        
        # Calcular correlaciones entre métodos
        methods = list(vcl_data.keys())
        for i, method1 in enumerate(methods):
            for method2 in methods[i+1:]:
                vcl1 = vcl_data[method1]
                vcl2 = vcl_data[method2]
                
                # Usar solo puntos válidos en ambos arrays
                valid_mask = ~(np.isnan(vcl1) | np.isnan(vcl2))
                if np.sum(valid_mask) > 1:
                    correlation = np.corrcoef(vcl1[valid_mask], vcl2[valid_mask])[0, 1]
                    comparison['correlations'][f"{method1}_vs_{method2}"] = float(correlation)
        
        return comparison
    
    def _assess_quality(self, vcl: np.ndarray, igr: np.ndarray, 
                       gr_clean: float, gr_clay: float) -> Dict:
        """
        Evalúa la calidad del cálculo de VCL.
        
        Args:
            vcl: Valores calculados de VCL
            igr: Valores de IGR
            gr_clean: Valor de arena limpia
            gr_clay: Valor de arcilla pura
            
        Returns:
            Dict con flags de calidad y recomendaciones
        """
        flags = {
            'overall_quality': 'good',
            'warnings': [],
            'recommendations': []
        }
        
        # Verificar rango de separación GR
        gr_range = gr_clay - gr_clean
        if gr_range < 30:
            flags['warnings'].append('Rango de GR muy pequeño (< 30 API)')
            flags['recommendations'].append('Considerar ajustar valores de GR_clean y GR_clay')
            flags['overall_quality'] = 'poor'
        elif gr_range < 50:
            flags['warnings'].append('Rango de GR limitado (< 50 API)')
            flags['overall_quality'] = 'fair'
        
        # Verificar distribución de VCL
        valid_vcl = vcl[~np.isnan(vcl)]
        if len(valid_vcl) > 0:
            vcl_range = np.max(valid_vcl) - np.min(valid_vcl)
            if vcl_range < 0.2:
                flags['warnings'].append('Rango de VCL muy pequeño (< 0.2)')
                flags['recommendations'].append('Verificar variabilidad litológica en los datos')
        
        # Verificar valores extremos
        high_vcl_count = np.sum(valid_vcl > 0.8)
        if high_vcl_count > len(valid_vcl) * 0.5:
            flags['warnings'].append('Más del 50% de valores VCL > 0.8')
            flags['recommendations'].append('Verificar método de cálculo y parámetros')
        
        return flags
    
    def get_method_info(self) -> Dict:
        """
        Obtiene información sobre todos los métodos disponibles.
        
        Returns:
            Dict con información detallada de cada método
        """
        return {
            'available_methods': list(self.methods.keys()),
            'descriptions': self.method_descriptions.copy(),
            'recommendations': {
                'linear': 'Uso general, pero subestima VCL',
                'larionov_older': 'Formaciones Pre-Terciarias consolidadas',
                'larionov_tertiary': 'Formaciones Terciarias poco consolidadas (RECOMENDADO)',
                'clavier': 'Aplicación general, buen balance',
                'steiber': 'Formaciones con alta radioactividad'
            }
        }
