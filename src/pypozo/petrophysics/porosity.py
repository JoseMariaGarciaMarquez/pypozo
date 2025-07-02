"""
Cálculos de Porosidad Efectiva (PHIE)
=====================================

Implementa métodos estándar de la industria para calcular porosidad efectiva
desde registros de densidad, neutrón y volumen de arcilla.

Incluye:
- Porosidad desde densidad (RHOB)
- Porosidad desde neutrón (NPHI)
- Porosidad densidad-neutrón combinada
- Corrección por arcilla
- Corrección por gas
- Análisis de litología
"""

import numpy as np
from typing import Optional, Dict, Literal, Union, List, Tuple
import logging
from .base import PetrophysicsCalculator

logger = logging.getLogger(__name__)

class PorosityCalculator(PetrophysicsCalculator):
    """
    Calculadora de Porosidad Efectiva desde registros de densidad y neutrón.
    
    Implementa métodos estándar para calcular porosidad efectiva considerando:
    - Corrección por volumen de arcilla
    - Efectos de gas
    - Variaciones litológicas
    - Control de calidad automático
    """
    
    def __init__(self):
        super().__init__()
        
        # Densidades de matriz típicas [g/cm³]
        self.matrix_densities = {
            'sandstone': 2.65,      # Arenisca (cuarzo)
            'limestone': 2.71,      # Caliza
            'dolomite': 2.87,       # Dolomita
            'anhydrite': 2.98,      # Anhidrita
            'halite': 2.16,         # Sal
            'coal': 1.30,           # Carbón
            'custom': None          # Definido por usuario
        }
        
        # Porosidades aparentes de arcilla
        self.clay_properties = {
            'density_apparent_porosity': 0.40,    # Porosidad aparente en densidad
            'neutron_apparent_porosity': 0.45,    # Porosidad aparente en neutrón
            'density': 2.20                       # Densidad de arcilla típica [g/cm³]
        }
        
        # Densidad de fluidos
        self.fluid_densities = {
            'fresh_water': 1.00,      # Agua dulce
            'salt_water': 1.10,       # Agua salada
            'oil': 0.85,              # Petróleo típico
            'gas': 0.20,              # Gas (aproximado a condiciones de pozo)
            'mud_filtrate': 1.05      # Filtrado de lodo
        }
    
    def calculate_density_porosity(self,
                                 bulk_density: Union[np.ndarray, List[float]],
                                 matrix_density: float = 2.65,
                                 fluid_density: float = 1.00,
                                 vcl: Optional[Union[np.ndarray, List[float]]] = None) -> Dict:
        """
        Calcula porosidad desde densidad volumétrica (RHOB).
        
        Fórmula: PHID = (RHOMA - RHOB) / (RHOMA - RHOF)
        Con corrección por arcilla si se proporciona VCL.
        
        Args:
            bulk_density: Densidad volumétrica [g/cm³]
            matrix_density: Densidad de la matriz [g/cm³]
            fluid_density: Densidad del fluido [g/cm³]
            vcl: Volumen de arcilla [fracción] (opcional)
            
        Returns:
            Dict con resultados del cálculo y estadísticas QC
        """
        # Validar entradas
        rhob = self.validate_input(bulk_density, "Bulk_Density", (1.0, 3.5))
        
        if vcl is not None:
            vcl_array = self.validate_input(vcl, "VCL", (0.0, 1.0))
            if len(vcl_array) != len(rhob):
                raise ValueError("VCL y densidad deben tener la misma longitud")
        else:
            vcl_array = None
        
        # Validar parámetros
        params = self.validate_parameters(
            matrix_density=matrix_density,
            fluid_density=fluid_density
        )
        
        # Calcular porosidad básica desde densidad
        phid_raw = (matrix_density - rhob) / (matrix_density - fluid_density)
        
        # Aplicar corrección por arcilla si está disponible
        if vcl_array is not None:
            # Corrección por arcilla usando propiedades aparentes
            clay_correction = vcl_array * self.clay_properties['density_apparent_porosity']
            phid = phid_raw - clay_correction
        else:
            phid = phid_raw.copy()
        
        # Limitar a rango físicamente razonable
        phid = np.clip(phid, 0, 0.5)  # 0-50% porosidad
        
        # Preparar resultado
        result = {
            'type': 'density_porosity_calculation',
            'phid': phid,
            'phid_raw': phid_raw,
            'clay_correction': vcl_array * self.clay_properties['density_apparent_porosity'] if vcl_array is not None else None,
            'parameters': {
                'matrix_density': matrix_density,
                'fluid_density': fluid_density,
                'clay_correction_applied': vcl_array is not None,
                'clay_apparent_porosity': self.clay_properties['density_apparent_porosity']
            },
            'input_stats': {
                'bulk_density': self.get_qc_stats(rhob, "Bulk_Density"),
                'vcl': self.get_qc_stats(vcl_array, "VCL") if vcl_array is not None else None
            },
            'qc_stats': {
                'phid': self.get_qc_stats(phid, "PHID"),
                'phid_raw': self.get_qc_stats(phid_raw, "PHID_Raw")
            },
            'warnings': self.validation_warnings.copy(),
            'quality_flags': self._assess_density_porosity_quality(phid, rhob, matrix_density)
        }
        
        self.last_calculation = result
        self.add_to_history(result)
        self.clear_warnings()
        
        return result
    
    def calculate_neutron_porosity(self,
                                 neutron_porosity: Union[np.ndarray, List[float]],
                                 vcl: Optional[Union[np.ndarray, List[float]]] = None,
                                 lithology: Literal['sandstone', 'limestone', 'dolomite'] = 'sandstone') -> Dict:
        """
        Calcula porosidad corregida desde neutrón (NPHI).
        
        Args:
            neutron_porosity: Porosidad neutrón aparente [fracción]
            vcl: Volumen de arcilla [fracción] (opcional)
            lithology: Tipo de litología para corrección
            
        Returns:
            Dict con resultados del cálculo y estadísticas QC
        """
        # Validar entradas
        nphi = self.validate_input(neutron_porosity, "Neutron_Porosity", (0.0, 1.0))
        
        if vcl is not None:
            vcl_array = self.validate_input(vcl, "VCL", (0.0, 1.0))
            if len(vcl_array) != len(nphi):
                raise ValueError("VCL y NPHI deben tener la misma longitud")
        else:
            vcl_array = None
        
        # Corrección litológica (simplificada)
        lithology_corrections = {
            'sandstone': 1.00,    # Sin corrección (base)
            'limestone': 0.95,    # Ligera reducción
            'dolomite': 0.90      # Mayor reducción
        }
        
        litho_factor = lithology_corrections.get(lithology, 1.00)
        nphi_corrected = nphi * litho_factor
        
        # Aplicar corrección por arcilla si está disponible
        if vcl_array is not None:
            clay_correction = vcl_array * self.clay_properties['neutron_apparent_porosity']
            phin = nphi_corrected - clay_correction
        else:
            phin = nphi_corrected.copy()
        
        # Limitar a rango físicamente razonable
        phin = np.clip(phin, 0, 0.5)
        
        # Preparar resultado
        result = {
            'type': 'neutron_porosity_calculation',
            'phin': phin,
            'phin_raw': nphi,
            'phin_lithology_corrected': nphi_corrected,
            'clay_correction': vcl_array * self.clay_properties['neutron_apparent_porosity'] if vcl_array is not None else None,
            'parameters': {
                'lithology': lithology,
                'lithology_factor': litho_factor,
                'clay_correction_applied': vcl_array is not None,
                'clay_apparent_porosity': self.clay_properties['neutron_apparent_porosity']
            },
            'input_stats': {
                'neutron_porosity': self.get_qc_stats(nphi, "Neutron_Porosity"),
                'vcl': self.get_qc_stats(vcl_array, "VCL") if vcl_array is not None else None
            },
            'qc_stats': {
                'phin': self.get_qc_stats(phin, "PHIN"),
                'phin_raw': self.get_qc_stats(nphi, "PHIN_Raw"),
                'phin_lithology_corrected': self.get_qc_stats(nphi_corrected, "PHIN_Litho_Corrected")
            },
            'warnings': self.validation_warnings.copy(),
            'quality_flags': self._assess_neutron_porosity_quality(phin, nphi)
        }
        
        self.last_calculation = result
        self.add_to_history(result)
        self.clear_warnings()
        
        return result
    
    def calculate_density_neutron_porosity(self,
                                         bulk_density: Union[np.ndarray, List[float]],
                                         neutron_porosity: Union[np.ndarray, List[float]],
                                         matrix_density: float = 2.65,
                                         fluid_density: float = 1.00,
                                         vcl: Optional[Union[np.ndarray, List[float]]] = None,
                                         lithology: Literal['sandstone', 'limestone', 'dolomite'] = 'sandstone',
                                         combination_method: Literal['arithmetic', 'geometric', 'harmonic'] = 'arithmetic') -> Dict:
        """
        Calcula porosidad efectiva combinando densidad y neutrón.
        
        Args:
            bulk_density: Densidad volumétrica [g/cm³]
            neutron_porosity: Porosidad neutrón [fracción]
            matrix_density: Densidad de matriz [g/cm³]
            fluid_density: Densidad de fluido [g/cm³]
            vcl: Volumen de arcilla [fracción] (opcional)
            lithology: Tipo de litología
            combination_method: Método de combinación
            
        Returns:
            Dict con resultados del cálculo completo
        """
        # Calcular porosidades individuales
        phid_result = self.calculate_density_porosity(
            bulk_density=bulk_density,
            matrix_density=matrix_density,
            fluid_density=fluid_density,
            vcl=vcl
        )
        
        phin_result = self.calculate_neutron_porosity(
            neutron_porosity=neutron_porosity,
            vcl=vcl,
            lithology=lithology
        )
        
        phid = phid_result['phid']
        phin = phin_result['phin']
        
        # Combinar porosidades según método seleccionado
        if combination_method == 'arithmetic':
            phie = (phid + phin) / 2
        elif combination_method == 'geometric':
            phie = np.sqrt(phid * phin)
        elif combination_method == 'harmonic':
            # Evitar divisiones por cero
            safe_phid = np.where(phid <= 0, 1e-6, phid)
            safe_phin = np.where(phin <= 0, 1e-6, phin)
            phie = 2 / (1/safe_phid + 1/safe_phin)
        else:
            raise ValueError(f"Método de combinación '{combination_method}' no válido")
        
        # Limitar resultado
        phie = np.clip(phie, 0, 0.5)
        
        # Detectar zonas con gas (NPHI << PHID)
        gas_effect = self._detect_gas_effect(phid, phin)
        
        # Preparar resultado combinado
        result = {
            'type': 'density_neutron_porosity_calculation',
            'phie': phie,
            'phid': phid,
            'phin': phin,
            'gas_effect': gas_effect,
            'parameters': {
                'combination_method': combination_method,
                'matrix_density': matrix_density,
                'fluid_density': fluid_density,
                'lithology': lithology,
                'clay_correction_applied': vcl is not None
            },
            'individual_results': {
                'density_porosity': phid_result,
                'neutron_porosity': phin_result
            },
            'qc_stats': {
                'phie': self.get_qc_stats(phie, "PHIE"),
                'phid': self.get_qc_stats(phid, "PHID"),
                'phin': self.get_qc_stats(phin, "PHIN")
            },
            'warnings': self.validation_warnings.copy(),
            'quality_flags': self._assess_combined_porosity_quality(phie, phid, phin, gas_effect)
        }
        
        self.last_calculation = result
        self.add_to_history(result)
        self.clear_warnings()
        
        return result
    
    def _detect_gas_effect(self, phid: np.ndarray, phin: np.ndarray, 
                          threshold: float = 0.05) -> Dict:
        """
        Detecta efectos de gas comparando PHID vs PHIN.
        
        Args:
            phid: Porosidad densidad
            phin: Porosidad neutrón
            threshold: Umbral para detección de gas
            
        Returns:
            Dict con información sobre efectos de gas
        """
        # Diferencia PHID - PHIN (positiva indica posible gas)
        gas_indicator = phid - phin
        
        # Identificar zonas con posible gas
        gas_zones = gas_indicator > threshold
        
        # Estadísticas
        gas_effect = {
            'gas_indicator': gas_indicator,
            'gas_zones': gas_zones,
            'gas_points_count': int(np.sum(gas_zones)),
            'gas_percentage': float(np.sum(gas_zones) / len(gas_zones) * 100),
            'max_gas_effect': float(np.max(gas_indicator)),
            'threshold_used': threshold
        }
        
        return gas_effect
    
    def _assess_density_porosity_quality(self, phid: np.ndarray, 
                                       rhob: np.ndarray, 
                                       matrix_density: float) -> Dict:
        """Evalúa calidad del cálculo de porosidad densidad."""
        flags = {
            'overall_quality': 'good',
            'warnings': [],
            'recommendations': []
        }
        
        # Verificar densidades físicamente razonables
        unrealistic_density = np.sum((rhob < 1.5) | (rhob > 3.0))
        if unrealistic_density > 0:
            flags['warnings'].append(f'{unrealistic_density} puntos con densidad no realista')
            flags['overall_quality'] = 'poor'
        
        # Verificar porosidades negativas
        negative_porosity = np.sum(phid < 0)
        if negative_porosity > len(phid) * 0.1:  # >10%
            flags['warnings'].append('Muchas porosidades negativas (>10%)')
            flags['recommendations'].append('Revisar densidad de matriz')
            flags['overall_quality'] = 'poor'
        
        # Verificar rango de porosidad
        valid_phid = phid[~np.isnan(phid)]
        if len(valid_phid) > 0:
            max_porosity = np.max(valid_phid)
            if max_porosity > 0.4:
                flags['warnings'].append('Porosidades muy altas (>40%)')
                flags['recommendations'].append('Verificar parámetros de cálculo')
        
        return flags
    
    def _assess_neutron_porosity_quality(self, phin: np.ndarray, 
                                       nphi_raw: np.ndarray) -> Dict:
        """Evalúa calidad del cálculo de porosidad neutrón."""
        flags = {
            'overall_quality': 'good',
            'warnings': [],
            'recommendations': []
        }
        
        # Verificar valores negativos después de corrección
        negative_after_correction = np.sum(phin < 0)
        if negative_after_correction > 0:
            flags['warnings'].append(f'{negative_after_correction} valores negativos tras corrección')
            flags['recommendations'].append('Revisar corrección por arcilla')
        
        # Verificar corrección excesiva
        over_corrected = np.sum(phin < nphi_raw * 0.5)  # Más de 50% de reducción
        if over_corrected > len(phin) * 0.1:
            flags['warnings'].append('Posible sobre-corrección por arcilla')
            flags['overall_quality'] = 'fair'
        
        return flags
    
    def _assess_combined_porosity_quality(self, phie: np.ndarray, 
                                        phid: np.ndarray, 
                                        phin: np.ndarray, 
                                        gas_effect: Dict) -> Dict:
        """Evalúa calidad del cálculo de porosidad combinada."""
        flags = {
            'overall_quality': 'good',
            'warnings': [],
            'recommendations': []
        }
        
        # Verificar consistencia entre PHID y PHIN
        valid_mask = ~(np.isnan(phid) | np.isnan(phin))
        if np.sum(valid_mask) > 0:
            correlation = np.corrcoef(phid[valid_mask], phin[valid_mask])[0, 1]
            
            if correlation < 0.5:
                flags['warnings'].append(f'Baja correlación PHID-PHIN ({correlation:.2f})')
                flags['recommendations'].append('Revisar calibración de herramientas')
                flags['overall_quality'] = 'fair'
        
        # Verificar efectos de gas
        if gas_effect['gas_percentage'] > 20:
            flags['warnings'].append(f"Posibles efectos de gas en {gas_effect['gas_percentage']:.1f}% de puntos")
            flags['recommendations'].append('Considerar corrección por gas')
        
        # Verificar rango final de porosidad
        valid_phie = phie[~np.isnan(phie)]
        if len(valid_phie) > 0:
            if np.max(valid_phie) > 0.35:
                flags['warnings'].append('Porosidades finales muy altas (>35%)')
            if np.std(valid_phie) > 0.15:
                flags['warnings'].append('Alta variabilidad en porosidad')
        
        return flags
    
    def get_lithology_recommendations(self, phid: np.ndarray, phin: np.ndarray) -> Dict:
        """
        Proporciona recomendaciones de litología basadas en crossplot PHID-PHIN.
        
        Args:
            phid: Porosidad densidad
            phin: Porosidad neutrón
            
        Returns:
            Dict con análisis litológico
        """
        # Calcular diferencias promedio
        valid_mask = ~(np.isnan(phid) | np.isnan(phin))
        if np.sum(valid_mask) == 0:
            return {'error': 'No hay datos válidos para análisis litológico'}
        
        phid_clean = phid[valid_mask]
        phin_clean = phin[valid_mask]
        
        # Análisis basado en separación PHIN-PHID
        separation = phin_clean - phid_clean
        avg_separation = np.mean(separation)
        
        # Interpretación litológica simplificada
        if avg_separation > 0.05:
            primary_lithology = 'clay/shale'
            confidence = 'high'
        elif avg_separation > 0.02:
            primary_lithology = 'sandy_shale'
            confidence = 'medium'
        elif abs(avg_separation) <= 0.02:
            primary_lithology = 'clean_sandstone'
            confidence = 'high'
        elif avg_separation < -0.02:
            primary_lithology = 'carbonate'
            confidence = 'medium'
        else:
            primary_lithology = 'mixed'
            confidence = 'low'
        
        recommendations = {
            'primary_lithology': primary_lithology,
            'confidence': confidence,
            'avg_separation': float(avg_separation),
            'separation_std': float(np.std(separation)),
            'analysis': {
                'clean_sandstone_percentage': float(np.sum(abs(separation) <= 0.02) / len(separation) * 100),
                'clay_percentage': float(np.sum(separation > 0.05) / len(separation) * 100),
                'carbonate_percentage': float(np.sum(separation < -0.02) / len(separation) * 100)
            },
            'recommendations': self._get_lithology_specific_recommendations(primary_lithology)
        }
        
        return recommendations
    
    def _get_lithology_specific_recommendations(self, lithology: str) -> List[str]:
        """Obtiene recomendaciones específicas por litología."""
        recommendations_map = {
            'clay/shale': [
                'Usar corrección agresiva por arcilla',
                'Considerar métodos específicos para lutitas',
                'Validar con datos de núcleos si están disponibles'
            ],
            'sandy_shale': [
                'Aplicar corrección moderada por arcilla',
                'Usar matriz de arenisca para cálculos',
                'Considerar efectos de minerales arcillosos'
            ],
            'clean_sandstone': [
                'Usar parámetros estándar de arenisca',
                'Matriz density = 2.65 g/cm³',
                'Buscar efectos de hidrocarburos'
            ],
            'carbonate': [
                'Usar densidad de matriz carbonática (2.71-2.87)',
                'Considerar efectos de dolomitización',
                'Validar porosidad con imaging logs'
            ],
            'mixed': [
                'Analizar intervalos por separado',
                'Usar múltiples modelos litológicos',
                'Validar con datos adicionales'
            ]
        }
        
        return recommendations_map.get(lithology, ['Realizar análisis detallado'])
    
    def get_matrix_density_info(self) -> Dict:
        """Obtiene información sobre densidades de matriz disponibles."""
        return {
            'available_lithologies': list(self.matrix_densities.keys()),
            'densities': self.matrix_densities.copy(),
            'recommendations': {
                'sandstone': 'Formaciones clásticas, reservorios convencionales',
                'limestone': 'Carbonatos marinos, plataformas carbonáticas',
                'dolomite': 'Carbonatos diagenéticamente alterados',
                'anhydrite': 'Evaporitas, sellos',
                'halite': 'Domos salinos, sellos',
                'coal': 'Capas de carbón',
                'custom': 'Definir según análisis específico'
            }
        }
    
    def apply_clay_correction(self, 
                            porosity_result: Dict,
                            vcl: Union[np.ndarray, List[float]],
                            clay_porosity_density: float = 0.40,
                            clay_porosity_neutron: float = 0.45) -> Dict:
        """
        Aplica corrección por arcilla a los resultados de porosidad.
        
        Utiliza el modelo de Thomas-Stieber para corregir el efecto de arcilla
        en las mediciones de porosidad.
        
        Args:
            porosity_result: Resultado de cálculo de porosidad
            vcl: Volumen de arcilla [fracción]
            clay_porosity_density: Porosidad aparente de arcilla en densidad
            clay_porosity_neutron: Porosidad aparente de arcilla en neutrón
            
        Returns:
            Dict con resultados corregidos por arcilla
        """
        # Validar entradas
        vcl_array = self.validate_input(vcl, "VCL", (0.0, 1.0))
        
        result = porosity_result.copy()
        
        # Corrección por arcilla según el tipo de porosidad
        if 'porosity' in result:
            # Para porosidad densidad o combinada
            porosity = result['porosity']
            
            # Detectar tipo de porosidad por el rango de valores típicos
            if np.nanmax(porosity) > 0.8:  # Probablemente densidad sin corregir
                clay_correction = clay_porosity_density
            else:
                clay_correction = clay_porosity_neutron
            
            # Aplicar corrección: PHIE = PHI_raw - VCL * PHI_clay_apparent
            corrected_porosity = porosity - vcl_array * clay_correction
            
            # Asegurar valores físicamente posibles
            corrected_porosity = np.clip(corrected_porosity, 0.0, 0.5)
            
            result['porosity_corrected'] = corrected_porosity
            result['clay_correction_applied'] = True
            result['clay_correction_parameters'] = {
                'clay_porosity_used': clay_correction,
                'max_vcl': np.nanmax(vcl_array),
                'avg_correction': np.nanmean(vcl_array * clay_correction)
            }
            
        if 'phid' in result and 'phin' in result:
            # Para porosidad combinada densidad-neutrón
            phid = result['phid']
            phin = result['phin']
            
            # Aplicar correcciones específicas
            phid_corrected = phid - vcl_array * clay_porosity_density
            phin_corrected = phin - vcl_array * clay_porosity_neutron
            
            # Recalcular porosidad efectiva
            phie_corrected = np.sqrt((phid_corrected**2 + phin_corrected**2) / 2)
            
            # Asegurar valores físicamente posibles
            phid_corrected = np.clip(phid_corrected, 0.0, 0.5)
            phin_corrected = np.clip(phin_corrected, 0.0, 0.5)
            phie_corrected = np.clip(phie_corrected, 0.0, 0.5)
            
            result['phid_corrected'] = phid_corrected
            result['phin_corrected'] = phin_corrected
            result['phie_corrected'] = phie_corrected
            result['clay_correction_applied'] = True
        
        return result
    
    def apply_gas_correction(self, 
                           porosity_result: Dict,
                           gas_correction_factor: float = 0.15) -> Dict:
        """
        Aplica corrección básica por gas a los resultados de porosidad.
        
        Implementa corrección simplificada para el efecto de gas en registros
        de densidad y neutrón. Para análisis detallado se requieren datos adicionales.
        
        Args:
            porosity_result: Resultado de cálculo de porosidad
            gas_correction_factor: Factor de corrección por gas [fracción]
            
        Returns:
            Dict con resultados corregidos por gas
        """
        result = porosity_result.copy()
        
        # Detectar posible presencia de gas usando separación PHID-PHIN
        if 'phid' in result and 'phin' in result:
            phid = result['phid']
            phin = result['phin']
            
            # Detectar zonas con posible gas (PHID << PHIN)
            gas_indicator = phin - phid
            gas_zones = gas_indicator > 0.05  # Umbral básico
            
            if np.any(gas_zones):
                # Aplicar corrección en zonas con indicación de gas
                phid_corrected = phid.copy()
                phin_corrected = phin.copy()
                
                # Corrección conservadora en zonas de gas
                phid_corrected[gas_zones] = phid[gas_zones] + gas_correction_factor * gas_indicator[gas_zones]
                
                # Recalcular porosidad efectiva
                phie_corrected = np.sqrt((phid_corrected**2 + phin_corrected**2) / 2)
                
                result['phid_gas_corrected'] = phid_corrected
                result['phin_gas_corrected'] = phin_corrected
                result['phie_gas_corrected'] = phie_corrected
                result['gas_zones_detected'] = gas_zones
                result['gas_correction_applied'] = True
                result['gas_correction_parameters'] = {
                    'correction_factor': gas_correction_factor,
                    'gas_zones_percentage': np.sum(gas_zones) / len(gas_zones) * 100,
                    'max_gas_effect': np.nanmax(gas_indicator[gas_zones]) if np.any(gas_zones) else 0
                }
        
        elif 'porosity' in result:
            # Para porosidad simple, aplicar corrección conservadora
            porosity = result['porosity']
            
            # Detectar posibles valores anómalos que podrían indicar gas
            median_porosity = np.nanmedian(porosity)
            anomalous_low = porosity < median_porosity * 0.7
            
            if np.any(anomalous_low):
                corrected_porosity = porosity.copy()
                corrected_porosity[anomalous_low] = porosity[anomalous_low] + gas_correction_factor
                
                result['porosity_gas_corrected'] = np.clip(corrected_porosity, 0.0, 0.5)
                result['gas_correction_applied'] = True
        
        return result
