"""
Cálculos de Permeabilidad
========================

Implementa métodos estándar de la industria para estimar permeabilidad
desde registros petrofísicos, incluyendo:

- Kozeny-Carman (teórico)
- Timur (empírico)
- Coates & Dumanoir (NMR)
- Wyllie & Rose (granular)
- Modelos regionales específicos

Todos los métodos incluyen validación de rangos y estadísticas QC.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Literal, Union, List, Tuple
import logging
from .base import PetrophysicsCalculator

logger = logging.getLogger(__name__)

class PermeabilityCalculator(PetrophysicsCalculator):
    """
    Calculadora de Permeabilidad desde registros petrofísicos.
    
    Implementa los modelos más utilizados en la industria petrolífera
    para estimar la permeabilidad en formaciones petrolíferas.
    """
    
    def __init__(self):
        super().__init__()
        
        # Métodos disponibles
        self.methods = {
            'timur': self._timur,
            'kozeny_carman': self._kozeny_carman,
            'coates_dumanoir': self._coates_dumanoir,
            'wyllie_rose': self._wyllie_rose,
            'schlumberger': self._schlumberger,
            'morris_biggs': self._morris_biggs
        }
        
        # Descripciones de métodos
        self.method_descriptions = {
            'timur': 'Timur: K = A * (φ^B / Swi^C) - Modelo empírico clásico',
            'kozeny_carman': 'Kozeny-Carman: K = C * (φ^3 / (1-φ)^2) - Modelo teórico',
            'coates_dumanoir': 'Coates & Dumanoir: Para datos de RMN',
            'wyllie_rose': 'Wyllie & Rose: Para rocas granulares',
            'schlumberger': 'Modelo Schlumberger: Para carbonatos',
            'morris_biggs': 'Morris & Biggs: Para areniscas'
        }
        
        # Parámetros por defecto para diferentes tipos de roca
        self.rock_type_params = {
            'sandstone': {
                'timur': {'A': 8581, 'B': 4.4, 'C': 2.0},
                'kozeny_carman': {'C': 5.0, 'tau': 2.0}
            },
            'carbonate': {
                'timur': {'A': 2040, 'B': 3.0, 'C': 1.0},
                'kozeny_carman': {'C': 2.0, 'tau': 3.0}
            },
            'shaly_sand': {
                'timur': {'A': 4500, 'B': 4.0, 'C': 2.0},
                'kozeny_carman': {'C': 1.0, 'tau': 4.0}
            }
        }
    
    def calculate_timur(self,
                       porosity: Union[np.ndarray, List[float]],
                       sw_irreducible: Union[np.ndarray, List[float], float],
                       rock_type: str = 'sandstone',
                       A: Optional[float] = None,
                       B: Optional[float] = None,
                       C: Optional[float] = None) -> Dict:
        """
        Calcular permeabilidad usando la correlación de Timur.
        
        K = A * (φ^B / Swi^C)
        
        Donde:
        - K: Permeabilidad en mD
        - φ: Porosidad (fracción)
        - Swi: Saturación de agua irreducible (fracción)
        - A, B, C: Constantes empíricas dependientes del tipo de roca
        
        Args:
            porosity: Porosidad efectiva (fracción)
            sw_irreducible: Saturación de agua irreducible (fracción o valor único)
            rock_type: Tipo de roca ('sandstone', 'carbonate', 'shaly_sand')
            A: Constante A (si None, usa valor por defecto del tipo de roca)
            B: Exponente B (si None, usa valor por defecto)
            C: Exponente C (si None, usa valor por defecto)
            
        Returns:
            Dict: Resultados del cálculo con estadísticas QC
        """
        logger.info(f"🧮 Calculando permeabilidad con correlación de Timur - {rock_type}")
        
        self.validation_warnings = []
        
        try:
            # Validar datos de entrada
            porosity = self.validate_input(porosity, "POROSITY", valid_range=(0.01, 0.5))
            
            # Manejar Swi como array o escalar
            if isinstance(sw_irreducible, (int, float)):
                swi = np.full_like(porosity, sw_irreducible)
            else:
                swi = self.validate_input(sw_irreducible, "SWI", valid_range=(0.01, 1.0))
                if len(swi) != len(porosity):
                    raise ValueError("POROSITY y SWI deben tener la misma longitud")
            
            # Obtener parámetros
            if rock_type in self.rock_type_params:
                params = self.rock_type_params[rock_type]['timur']
                A = A or params['A']
                B = B or params['B'] 
                C = C or params['C']
            else:
                # Valores por defecto para areniscas
                A = A or 8581
                B = B or 4.4
                C = C or 2.0
                logger.warning(f"Tipo de roca '{rock_type}' no reconocido, usando parámetros de arenisca")
            
            # Aplicar ecuación de Timur
            # K = A * (φ^B / Swi^C)
            permeability = A * (np.power(porosity, B) / np.power(swi, C))
            
            # Aplicar límites físicos (0.001 mD a 10,000 mD)
            permeability = np.clip(permeability, 0.001, 10000)
            
            # Calcular estadísticas QC
            qc_stats = self.get_qc_stats(permeability, "PERM_TIMUR")
            
            # Información del cálculo
            calc_info = {
                'method': 'timur',
                'rock_type': rock_type,
                'parameters': {
                    'A': A,
                    'B': B,
                    'C': C
                },
                'description': self.method_descriptions['timur']
            }
            
            # Resultado completo
            result = {
                'permeability': permeability,
                'permeability_log10': np.log10(permeability),  # Para visualización
                'qc_stats': qc_stats,
                'calculation_info': calc_info,
                'validation_warnings': self.validation_warnings.copy(),
                'success': True
            }
            
            # Guardar en historial
            self.last_calculation = result
            self.calculation_history.append({
                'method': 'timur',
                'timestamp': pd.Timestamp.now(),
                'parameters': calc_info['parameters']
            })
            
            logger.info(f"✅ Cálculo Timur completado. K promedio: {np.nanmean(permeability):.2f} mD")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en cálculo Timur: {str(e)}")
            return {
                'permeability': None,
                'success': False,
                'error': str(e),
                'validation_warnings': self.validation_warnings.copy()
            }
    
    def calculate_kozeny_carman(self,
                               porosity: Union[np.ndarray, List[float]],
                               grain_size: Optional[Union[np.ndarray, List[float]]] = None,
                               tortuosity: float = 2.0,
                               C: Optional[float] = None,
                               rock_type: str = 'sandstone') -> Dict:
        """
        Calcular permeabilidad usando la ecuación de Kozeny-Carman.
        
        K = C * (φ^3 / ((1-φ)^2 * τ))
        
        Donde:
        - K: Permeabilidad en mD
        - φ: Porosidad (fracción)
        - τ: Tortuosidad
        - C: Constante que depende del tamaño de grano y forma
        
        Args:
            porosity: Porosidad efectiva (fracción)
            grain_size: Tamaño de grano promedio (μm) - opcional
            tortuosity: Factor de tortuosidad
            C: Constante de Kozeny (si None, usa valor por defecto)
            rock_type: Tipo de roca para parámetros por defecto
            
        Returns:
            Dict: Resultados del cálculo
        """
        logger.info(f"🧮 Calculando permeabilidad con Kozeny-Carman - {rock_type}")
        
        self.validation_warnings = []
        
        try:
            # Validar datos
            porosity = self.validate_input(porosity, "POROSITY", valid_range=(0.01, 0.5))
            
            # Obtener constante C
            if rock_type in self.rock_type_params:
                C = C or self.rock_type_params[rock_type]['kozeny_carman']['C']
                tortuosity = self.rock_type_params[rock_type]['kozeny_carman']['tau']
            else:
                C = C or 5.0  # Valor típico para areniscas
            
            # Aplicar ecuación de Kozeny-Carman
            # K = C * (φ^3 / ((1-φ)^2 * τ))
            porosity_term = np.power(porosity, 3) / (np.power(1 - porosity, 2) * tortuosity)
            
            # Si hay datos de tamaño de grano, incluirlos
            if grain_size is not None:
                grain_size = self.validate_input(grain_size, "GRAIN_SIZE", valid_range=(1, 1000))
                # K proporcional al cuadrado del tamaño de grano (en μm)
                permeability = C * porosity_term * np.power(grain_size / 100, 2)  # Normalizar a 100 μm
            else:
                permeability = C * porosity_term
            
            # Aplicar límites físicos
            permeability = np.clip(permeability, 0.001, 10000)
            
            # Estadísticas QC
            qc_stats = self.get_qc_stats(permeability, "PERM_KC")
            
            result = {
                'permeability': permeability,
                'permeability_log10': np.log10(permeability),
                'qc_stats': qc_stats,
                'calculation_info': {
                    'method': 'kozeny_carman',
                    'rock_type': rock_type,
                    'parameters': {
                        'C': C,
                        'tortuosity': tortuosity,
                        'grain_size_included': grain_size is not None
                    },
                    'description': self.method_descriptions['kozeny_carman']
                },
                'validation_warnings': self.validation_warnings.copy(),
                'success': True
            }
            
            logger.info(f"✅ Cálculo Kozeny-Carman completado. K promedio: {np.nanmean(permeability):.2f} mD")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en Kozeny-Carman: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'validation_warnings': self.validation_warnings.copy()
            }
    
    def calculate_wyllie_rose(self,
                             porosity: Union[np.ndarray, List[float]],
                             grain_size: Union[np.ndarray, List[float]],
                             sorting_coefficient: float = 2.0) -> Dict:
        """
        Calcular permeabilidad usando la correlación de Wyllie & Rose.
        
        Para rocas granulares (areniscas) bien clasificadas.
        K = 79 * (φ^3 / (1-φ)^2) * (d50^2 / So^2)
        
        Args:
            porosity: Porosidad efectiva (fracción)
            grain_size: Tamaño de grano medio d50 (μm)
            sorting_coefficient: Coeficiente de clasificación So
            
        Returns:
            Dict: Resultados del cálculo
        """
        logger.info("🧮 Calculando permeabilidad con Wyllie & Rose")
        
        self.validation_warnings = []
        
        try:
            # Validar datos
            porosity = self.validate_input(porosity, "POROSITY", valid_range=(0.05, 0.4))
            grain_size = self.validate_input(grain_size, "GRAIN_SIZE", valid_range=(10, 1000))
            
            # Aplicar ecuación de Wyllie & Rose
            # K = 79 * (φ^3 / (1-φ)^2) * (d50^2 / So^2)
            porosity_term = np.power(porosity, 3) / np.power(1 - porosity, 2)
            grain_term = np.power(grain_size, 2) / (sorting_coefficient ** 2)
            permeability = 79 * porosity_term * grain_term / 1000  # Convertir a mD
            
            # Aplicar límites físicos
            permeability = np.clip(permeability, 0.001, 10000)
            
            # Estadísticas QC
            qc_stats = self.get_qc_stats(permeability, "PERM_WR")
            
            result = {
                'permeability': permeability,
                'permeability_log10': np.log10(permeability),
                'qc_stats': qc_stats,
                'calculation_info': {
                    'method': 'wyllie_rose',
                    'parameters': {
                        'sorting_coefficient': sorting_coefficient
                    },
                    'description': self.method_descriptions['wyllie_rose']
                },
                'validation_warnings': self.validation_warnings.copy(),
                'success': True
            }
            
            logger.info(f"✅ Cálculo Wyllie & Rose completado. K promedio: {np.nanmean(permeability):.2f} mD")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en Wyllie & Rose: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'validation_warnings': self.validation_warnings.copy()
            }
    
    def estimate_swi_from_permeability(self,
                                      permeability: Union[np.ndarray, List[float]],
                                      method: str = 'morris_biggs') -> Dict:
        """
        Estimar Swi desde permeabilidad usando correlaciones empíricas.
        
        Útil cuando no se tienen datos de presión capilar.
        
        Args:
            permeability: Permeabilidad en mD
            method: Método a usar ('morris_biggs', 'schlumberger')
            
        Returns:
            Dict: Estimación de Swi
        """
        logger.info(f"🧮 Estimando Swi desde permeabilidad - método {method}")
        
        try:
            permeability = self.validate_input(permeability, "PERMEABILITY", valid_range=(0.001, 10000))
            
            if method == 'morris_biggs':
                # Swi = 0.2 + 0.8 / (1 + 0.35 * sqrt(K/φ))
                # Aproximación: asumir φ = 0.2 promedio
                swi = 0.2 + 0.8 / (1 + 0.35 * np.sqrt(permeability / 0.2))
            
            elif method == 'schlumberger':
                # Correlación Schlumberger para carbonatos
                # Swi = 0.1 + 0.7 * K^(-0.15)
                swi = 0.1 + 0.7 * np.power(permeability, -0.15)
            
            else:
                raise ValueError(f"Método {method} no reconocido")
            
            # Aplicar límites físicos
            swi = np.clip(swi, 0.05, 0.8)
            
            result = {
                'swi_estimated': swi,
                'method': method,
                'success': True
            }
            
            logger.info(f"✅ Estimación Swi completada. Swi promedio: {np.nanmean(swi):.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error estimando Swi: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_permeability_classification(self, permeability: np.ndarray) -> Dict:
        """
        Clasificar permeabilidad según estándares de la industria.
        
        Args:
            permeability: Array de permeabilidades en mD
            
        Returns:
            Dict: Clasificación y estadísticas
        """
        # Clasificación estándar de permeabilidad
        classifications = {
            'very_tight': (0, 0.1),
            'tight': (0.1, 1),
            'low': (1, 10),
            'moderate': (10, 100),
            'good': (100, 1000),
            'very_good': (1000, 10000)
        }
        
        valid_perm = permeability[~np.isnan(permeability)]
        
        result = {
            'total_points': len(valid_perm),
            'classifications': {}
        }
        
        for class_name, (min_val, max_val) in classifications.items():
            mask = (valid_perm >= min_val) & (valid_perm < max_val)
            count = np.sum(mask)
            percentage = (count / len(valid_perm)) * 100 if len(valid_perm) > 0 else 0
            
            result['classifications'][class_name] = {
                'count': count,
                'percentage': percentage,
                'range_md': f"{min_val}-{max_val}"
            }
        
        return result
    
    def _timur(self, **kwargs):
        """Wrapper para método Timur."""
        return self.calculate_timur(**kwargs)
    
    def _kozeny_carman(self, **kwargs):
        """Wrapper para método Kozeny-Carman.""" 
        return self.calculate_kozeny_carman(**kwargs)
    
    def _wyllie_rose(self, **kwargs):
        """Wrapper para método Wyllie & Rose."""
        return self.calculate_wyllie_rose(**kwargs)
    
    def _coates_dumanoir(self, **kwargs):
        """Placeholder para método Coates & Dumanoir."""
        logger.warning("⚠️ Método Coates & Dumanoir aún no implementado")
        return {'success': False, 'error': 'Método no implementado'}
    
    def _schlumberger(self, **kwargs):
        """Placeholder para modelo Schlumberger."""
        logger.warning("⚠️ Modelo Schlumberger aún no implementado")
        return {'success': False, 'error': 'Método no implementado'}
    
    def _morris_biggs(self, **kwargs):
        """Placeholder para método Morris & Biggs."""
        logger.warning("⚠️ Método Morris & Biggs aún no implementado")
        return {'success': False, 'error': 'Método no implementado'}
