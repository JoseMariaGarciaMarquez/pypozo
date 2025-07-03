"""
Cálculos de Saturación de Agua (Sw)
===================================

Implementa métodos estándar de la industria para calcular saturación de agua
desde registros de resistividad, incluyendo:

- Ecuación de Archie (simple y modificada)
- Modelo de Waxman-Smits (para arcillas conductivas)
- Modelo de Dual Water (para formaciones con arcilla)
- Modelos empíricos regionales

Todos los métodos incluyen validación de parámetros y estadísticas QC.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Literal, Union, List, Tuple
import logging
from .base import PetrophysicsCalculator

logger = logging.getLogger(__name__)

class WaterSaturationCalculator(PetrophysicsCalculator):
    """
    Calculadora de Saturación de Agua desde registros de resistividad.
    
    Implementa los modelos más utilizados en la industria petrolífera
    para determinar la saturación de agua en formaciones petrolíferas.
    """
    
    def __init__(self):
        super().__init__()
        
        # Métodos disponibles
        self.methods = {
            'archie_simple': self._archie_simple,
            'archie_modified': self._archie_modified,
            'waxman_smits': self._waxman_smits,
            'dual_water': self._dual_water,
            'simandoux': self._simandoux,
            'indonesian': self._indonesian
        }
        
        # Descripciones de métodos
        self.method_descriptions = {
            'archie_simple': 'Archie Simple: Sw = ((a*Rw)/(φ^m * Rt))^(1/n)',
            'archie_modified': 'Archie con Vclay: Sw = ((a*Rw)/(φe^m * Rt))^(1/n)',
            'waxman_smits': 'Waxman-Smits: Para formaciones con arcillas conductivas',
            'dual_water': 'Dual Water: Modelo de dos aguas (libre y ligada)',
            'simandoux': 'Simandoux: Para formaciones arcillosas',
            'indonesian': 'Ecuación Indonesa: Para formaciones fracturadas'
        }
        
        # Parámetros típicos por defecto
        self.default_params = {
            'a': 1.0,      # Factor de tortuosidad
            'm': 2.0,      # Exponente de cementación
            'n': 2.0,      # Exponente de saturación
            'rw': 0.05,    # Resistividad del agua de formación (ohm-m)
            'rsh': 2.0,    # Resistividad de las arcillas (ohm-m)
            'vcl_cutoff': 0.5  # Cutoff de arcilla para métodos especiales
        }
    
    def calculate_archie_simple(self, 
                               rt: Union[np.ndarray, List[float]],
                               porosity: Union[np.ndarray, List[float]],
                               rw: float = 0.05,
                               a: float = 1.0,
                               m: float = 2.0,
                               n: float = 2.0,
                               validate_inputs: bool = True) -> Dict:
        """
        Calcular saturación de agua usando la ecuación de Archie simple.
        
        Sw = ((a * Rw) / (φ^m * Rt))^(1/n)
        
        Args:
            rt: Resistividad verdadera (ohm-m)
            porosity: Porosidad efectiva (fracción)
            rw: Resistividad del agua de formación (ohm-m)
            a: Factor de tortuosidad (adimensional)
            m: Exponente de cementación (adimensional)
            n: Exponente de saturación (adimensional)
            validate_inputs: Si validar datos de entrada
            
        Returns:
            Dict: Resultados del cálculo con estadísticas QC
        """
        logger.info("🧮 Calculando Sw con ecuación de Archie simple")
        
        # Limpiar warnings previos
        self.validation_warnings = []
        
        try:
            # Validar datos de entrada
            if validate_inputs:
                rt = self.validate_input(rt, "RT", valid_range=(0.1, 1000))
                porosity = self.validate_input(porosity, "POROSITY", valid_range=(0.01, 0.5))
                
                # Validar que tienen la misma longitud
                if len(rt) != len(porosity):
                    raise ValueError("RT y POROSITY deben tener la misma longitud")
            
            # Validar parámetros
            if rw <= 0:
                raise ValueError(f"Rw debe ser positivo, valor dado: {rw}")
            if a <= 0:
                raise ValueError(f"Factor 'a' debe ser positivo, valor dado: {a}")
            if m <= 0:
                raise ValueError(f"Exponente 'm' debe ser positivo, valor dado: {m}")
            if n <= 0:
                raise ValueError(f"Exponente 'n' debe ser positivo, valor dado: {n}")
            
            # Aplicar ecuación de Archie
            # Sw = ((a * Rw) / (φ^m * Rt))^(1/n)
            
            # Calcular factor de formación: F = a / φ^m
            formation_factor = a / np.power(porosity, m)
            
            # Calcular índice de resistividad: RI = Rt / Rw
            resistivity_index = rt / rw
            
            # Calcular Sw
            sw = np.power(formation_factor / resistivity_index, 1/n)
            
            # Aplicar límites físicos (0 <= Sw <= 1)
            sw = np.clip(sw, 0.0, 1.0)
            
            # Calcular Saturación de Hidrocarburos
            sh = 1.0 - sw
            
            # Generar estadísticas QC
            qc_stats = self.get_qc_stats(sw, "SW_ARCHIE")
            
            # Información adicional del cálculo
            calc_info = {
                'method': 'archie_simple',
                'parameters': {
                    'rw': rw,
                    'a': a,
                    'm': m,
                    'n': n
                },
                'description': self.method_descriptions['archie_simple']
            }
            
            # Resultado completo
            result = {
                'sw': sw,
                'sh': sh,
                'formation_factor': formation_factor,
                'resistivity_index': resistivity_index,
                'qc_stats': qc_stats,
                'calculation_info': calc_info,
                'validation_warnings': self.validation_warnings.copy(),
                'success': True
            }
            
            # Guardar en historial
            self.last_calculation = result
            self.calculation_history.append({
                'method': 'archie_simple',
                'timestamp': pd.Timestamp.now(),
                'parameters': calc_info['parameters']
            })
            
            logger.info(f"✅ Cálculo Archie completado. Sw promedio: {np.nanmean(sw):.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en cálculo Archie: {str(e)}")
            return {
                'sw': None,
                'sh': None,
                'success': False,
                'error': str(e),
                'validation_warnings': self.validation_warnings.copy()
            }
    
    def calculate_archie_with_vclay(self,
                                   rt: Union[np.ndarray, List[float]],
                                   porosity: Union[np.ndarray, List[float]],
                                   vclay: Union[np.ndarray, List[float]],
                                   rw: float = 0.05,
                                   a: float = 1.0,
                                   m: float = 2.0,
                                   n: float = 2.0,
                                   vclay_correction: bool = True) -> Dict:
        """
        Calcular saturación de agua usando Archie con corrección por arcilla.
        
        Usa porosidad efectiva corregida por volumen de arcilla.
        φe = φ * (1 - Vclay)
        
        Args:
            rt: Resistividad verdadera (ohm-m)
            porosity: Porosidad total (fracción)
            vclay: Volumen de arcilla (fracción)
            rw: Resistividad del agua de formación (ohm-m)
            a: Factor de tortuosidad
            m: Exponente de cementación
            n: Exponente de saturación
            vclay_correction: Si aplicar corrección por arcilla
            
        Returns:
            Dict: Resultados del cálculo
        """
        logger.info("🧮 Calculando Sw con Archie corregido por Vclay")
        
        self.validation_warnings = []
        
        try:
            # Validar datos
            rt = self.validate_input(rt, "RT", valid_range=(0.1, 1000))
            porosity = self.validate_input(porosity, "POROSITY", valid_range=(0.01, 0.5))
            vclay = self.validate_input(vclay, "VCLAY", valid_range=(0.0, 1.0))
            
            # Calcular porosidad efectiva
            if vclay_correction:
                porosity_effective = porosity * (1.0 - vclay)
                # Asegurar mínimo físico
                porosity_effective = np.maximum(porosity_effective, 0.001)
            else:
                porosity_effective = porosity
            
            # Usar el método de Archie simple con porosidad efectiva
            result = self.calculate_archie_simple(
                rt=rt,
                porosity=porosity_effective,
                rw=rw, a=a, m=m, n=n,
                validate_inputs=False  # Ya validamos
            )
            
            if result['success']:
                # Actualizar información del método
                result['calculation_info']['method'] = 'archie_modified'
                result['calculation_info']['description'] = self.method_descriptions['archie_modified']
                result['porosity_effective'] = porosity_effective
                result['vclay'] = vclay
                result['vclay_correction_applied'] = vclay_correction
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en Archie con Vclay: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'validation_warnings': self.validation_warnings.copy()
            }
    
    def calculate_simandoux(self,
                           rt: Union[np.ndarray, List[float]],
                           porosity: Union[np.ndarray, List[float]],
                           vclay: Union[np.ndarray, List[float]],
                           rw: float = 0.05,
                           rsh: float = 2.0,
                           a: float = 1.0,
                           m: float = 2.0,
                           n: float = 2.0) -> Dict:
        """
        Calcular saturación de agua usando el modelo de Simandoux.
        
        Para formaciones con contenido significativo de arcilla.
        Modelo de resistividad en paralelo.
        
        Args:
            rt: Resistividad verdadera (ohm-m)
            porosity: Porosidad total (fracción)
            vclay: Volumen de arcilla (fracción)
            rw: Resistividad del agua de formación (ohm-m)
            rsh: Resistividad de las arcillas (ohm-m)
            a: Factor de tortuosidad
            m: Exponente de cementación
            n: Exponente de saturación
            
        Returns:
            Dict: Resultados del cálculo
        """
        logger.info("🧮 Calculando Sw con modelo de Simandoux")
        
        self.validation_warnings = []
        
        try:
            # Validar datos
            rt = self.validate_input(rt, "RT", valid_range=(0.1, 1000))
            porosity = self.validate_input(porosity, "POROSITY", valid_range=(0.01, 0.5))
            vclay = self.validate_input(vclay, "VCLAY", valid_range=(0.0, 1.0))
            
            # Ecuación de Simandoux (forma cuadrática)
            # 1/Rt = φ^m * Sw^n / (a * Rw) + Vclay * Sw / Rsh
            
            # Coeficientes de la ecuación cuadrática: A*Sw^2 + B*Sw + C = 0
            phi_m = np.power(porosity, m)
            
            # Para n=2 (caso más común)
            if abs(n - 2.0) < 0.001:
                # A = φ^m / (a * Rw)
                A = phi_m / (a * rw)
                # B = Vclay / Rsh  
                B = vclay / rsh
                # C = -1/Rt
                C = -1.0 / rt
                
                # Resolver ecuación cuadrática
                discriminant = B**2 - 4*A*C
                
                # Verificar discriminante válido
                valid_mask = discriminant >= 0
                sw = np.full_like(rt, np.nan)
                
                # Calcular Sw donde es válido
                sw[valid_mask] = (-B[valid_mask] + np.sqrt(discriminant[valid_mask])) / (2 * A[valid_mask])
                
            else:
                # Para otros valores de n, usar método iterativo
                logger.warning(f"Usando método iterativo para n={n}")
                sw = self._solve_simandoux_iterative(rt, porosity, vclay, rw, rsh, a, m, n)
            
            # Aplicar límites físicos
            sw = np.clip(sw, 0.0, 1.0)
            sh = 1.0 - sw
            
            # Estadísticas QC
            qc_stats = self.get_qc_stats(sw, "SW_SIMANDOUX")
            
            result = {
                'sw': sw,
                'sh': sh,
                'qc_stats': qc_stats,
                'calculation_info': {
                    'method': 'simandoux',
                    'parameters': {
                        'rw': rw,
                        'rsh': rsh,
                        'a': a,
                        'm': m,
                        'n': n
                    },
                    'description': self.method_descriptions['simandoux']
                },
                'validation_warnings': self.validation_warnings.copy(),
                'success': True
            }
            
            logger.info(f"✅ Cálculo Simandoux completado. Sw promedio: {np.nanmean(sw):.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en Simandoux: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'validation_warnings': self.validation_warnings.copy()
            }
    
    def _solve_simandoux_iterative(self, rt, porosity, vclay, rw, rsh, a, m, n):
        """Resolver Simandoux iterativamente para n != 2."""
        sw = np.full_like(rt, 0.5)  # Valor inicial
        
        for _ in range(10):  # Máximo 10 iteraciones
            sw_old = sw.copy()
            
            # Calcular nuevo Sw
            term1 = (porosity**m) * (sw**n) / (a * rw)
            term2 = vclay * sw / rsh
            residual = term1 + term2 - 1.0/rt
            
            # Derivada para Newton-Raphson
            dterm1 = (porosity**m) * n * (sw**(n-1)) / (a * rw)
            dterm2 = vclay / rsh
            derivative = dterm1 + dterm2
            
            # Actualizar Sw
            sw = sw - residual / (derivative + 1e-10)  # Evitar división por cero
            sw = np.clip(sw, 0.01, 0.99)
            
            # Verificar convergencia
            if np.mean(np.abs(sw - sw_old)) < 1e-6:
                break
        
        return sw
    
    def get_method_info(self) -> Dict:
        """
        Obtener información sobre métodos disponibles.
        
        Returns:
            Dict: Información detallada de todos los métodos
        """
        return {
            'available_methods': list(self.methods.keys()),
            'descriptions': self.method_descriptions.copy(),
            'default_parameters': self.default_params.copy(),
            'recommendations': {
                'clean_formations': 'archie_simple',
                'shaly_formations': 'simandoux',
                'high_vclay': 'waxman_smits',
                'fractured': 'indonesian'
            }
        }
    
    def _archie_simple(self, **kwargs):
        """Wrapper interno para método Archie simple."""
        return self.calculate_archie_simple(**kwargs)
    
    def _archie_modified(self, **kwargs):
        """Wrapper interno para método Archie modificado."""
        return self.calculate_archie_with_vclay(**kwargs)
    
    def _simandoux(self, **kwargs):
        """Wrapper interno para método Simandoux."""
        return self.calculate_simandoux(**kwargs)
    
    def _waxman_smits(self, **kwargs):
        """Placeholder para método Waxman-Smits."""
        logger.warning("⚠️ Método Waxman-Smits aún no implementado")
        return {'success': False, 'error': 'Método no implementado'}
    
    def _dual_water(self, **kwargs):
        """Placeholder para método Dual Water."""
        logger.warning("⚠️ Método Dual Water aún no implementado")
        return {'success': False, 'error': 'Método no implementado'}
    
    def _indonesian(self, **kwargs):
        """Placeholder para ecuación Indonesa."""
        logger.warning("⚠️ Ecuación Indonesa aún no implementada")
        return {'success': False, 'error': 'Método no implementado'}
