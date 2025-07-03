"""
Análisis Litológico
==================

Implementa métodos para identificación y análisis de litologías
desde registros petrofísicos, incluyendo:

- Crossplots clásicos (Neutron-Density, Photoelectric-Density)
- Análisis de facies petrofísicas
- Identificación de minerales
- Clasificación de rocas
- Análisis de calidad de reservorio

Basado en técnicas estándar de interpretación petrofísica.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Literal, Union, List, Tuple
import logging
from .base import PetrophysicsCalculator

logger = logging.getLogger(__name__)

class LithologyAnalyzer(PetrophysicsCalculator):
    """
    Analizador de Litología desde registros petrofísicos.
    
    Implementa técnicas estándar para identificación de tipos de roca
    y análisis de calidad de reservorio.
    """
    
    def __init__(self):
        super().__init__()
        
        # Valores de matriz para minerales comunes
        self.mineral_properties = {
            'quartz': {
                'rhob_matrix': 2.65,  # g/cm³
                'pe_matrix': 1.81,    # barns/electron
                'nphi_matrix': -0.02  # Neutron aparente
            },
            'calcite': {
                'rhob_matrix': 2.71,
                'pe_matrix': 5.08,
                'nphi_matrix': 0.00
            },
            'dolomite': {
                'rhob_matrix': 2.87,
                'pe_matrix': 3.14,
                'nphi_matrix': 0.04
            },
            'clay': {
                'rhob_matrix': 2.40,
                'pe_matrix': 2.8,
                'nphi_matrix': 0.45
            },
            'anhydrite': {
                'rhob_matrix': 2.96,
                'pe_matrix': 5.05,
                'nphi_matrix': 0.02
            }
        }
        
        # Fluidos
        self.fluid_properties = {
            'fresh_water': {
                'rhob_fluid': 1.00,
                'pe_fluid': 0.36,
                'nphi_fluid': 1.00
            },
            'salt_water': {
                'rhob_fluid': 1.10,
                'pe_fluid': 0.81,
                'nphi_fluid': 1.00
            },
            'oil': {
                'rhob_fluid': 0.85,
                'pe_fluid': 0.12,
                'nphi_fluid': 0.80
            },
            'gas': {
                'rhob_fluid': 0.20,
                'pe_fluid': 0.12,
                'nphi_fluid': 0.45
            }
        }
    
    def neutron_density_analysis(self,
                                rhob: Union[np.ndarray, List[float]],
                                nphi: Union[np.ndarray, List[float]],
                                pe: Optional[Union[np.ndarray, List[float]]] = None,
                                fluid_type: str = 'fresh_water') -> Dict:
        """
        Análisis de crossplot Neutron-Density para identificación litológica.
        
        Args:
            rhob: Densidad bulk (g/cm³)
            nphi: Porosidad neutrón (fracción)
            pe: Factor fotoeléctrico (barns/electron) - opcional
            fluid_type: Tipo de fluido ('fresh_water', 'salt_water', 'oil', 'gas')
            
        Returns:
            Dict: Análisis litológico completo
        """
        logger.info("🧮 Ejecutando análisis Neutron-Density")
        
        self.validation_warnings = []
        
        try:
            # Validar datos
            rhob = self.validate_input(rhob, "RHOB", valid_range=(1.5, 3.2))
            nphi = self.validate_input(nphi, "NPHI", valid_range=(-0.1, 0.8))
            
            if pe is not None:
                pe = self.validate_input(pe, "PE", valid_range=(0.5, 10.0))
            
            # Propiedades del fluido
            fluid_props = self.fluid_properties[fluid_type]
            
            # Calcular porosidad aparente para diferentes minerales
            mineral_analysis = {}
            
            for mineral, props in self.mineral_properties.items():
                # Porosidad desde densidad: φ = (ρma - ρb) / (ρma - ρf)
                phi_density = ((props['rhob_matrix'] - rhob) / 
                              (props['rhob_matrix'] - fluid_props['rhob_fluid']))
                
                # Corrección por arcilla si es necesario
                phi_neutron = nphi - props['nphi_matrix']
                
                # Separación Neutron-Density (indicador de litología/gas)
                nd_separation = phi_neutron - phi_density
                
                mineral_analysis[mineral] = {
                    'porosity_density': phi_density,
                    'porosity_neutron_corrected': phi_neutron,
                    'nd_separation': nd_separation
                }
            
            # Identificar mineral dominante por menor separación
            separations = {mineral: abs(np.nanmean(data['nd_separation'])) 
                          for mineral, data in mineral_analysis.items()}
            dominant_mineral = min(separations, key=separations.get)
            
            # Detectar efectos de gas (separación positiva grande)
            gas_effect = np.maximum(0, mineral_analysis['quartz']['nd_separation'])
            gas_zones = gas_effect > 0.05  # Threshold para detección de gas
            
            # Análisis de facies petrofísicas
            facies = self._classify_petrophysical_facies(rhob, nphi, pe)
            
            # Calcular porosidad total corregida
            phi_total = mineral_analysis[dominant_mineral]['porosity_density']
            phi_total = np.clip(phi_total, 0.0, 0.5)
            
            # Resultado completo
            result = {
                'dominant_mineral': dominant_mineral,
                'mineral_analysis': mineral_analysis,
                'porosity_total': phi_total,
                'gas_effect': gas_effect,
                'gas_zones': gas_zones,
                'petrophysical_facies': facies,
                'fluid_type': fluid_type,
                'nd_separation_stats': {
                    'mean': np.nanmean(mineral_analysis[dominant_mineral]['nd_separation']),
                    'std': np.nanstd(mineral_analysis[dominant_mineral]['nd_separation']),
                    'min': np.nanmin(mineral_analysis[dominant_mineral]['nd_separation']),
                    'max': np.nanmax(mineral_analysis[dominant_mineral]['nd_separation'])
                },
                'success': True
            }
            
            logger.info(f"✅ Análisis N-D completado. Mineral dominante: {dominant_mineral}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis N-D: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'validation_warnings': self.validation_warnings.copy()
            }
    
    def _classify_petrophysical_facies(self, rhob, nphi, pe=None):
        """Clasificar facies petrofísicas basado en crossplots."""
        n_points = len(rhob)
        facies = np.full(n_points, 'unknown', dtype='<U20')
        
        for i in range(n_points):
            if np.isnan(rhob[i]) or np.isnan(nphi[i]):
                continue
                
            rho = rhob[i]
            phi = nphi[i]
            
            # Clasificación simple basada en rangos típicos
            if rho > 2.6 and phi < 0.1:
                if pe is not None and not np.isnan(pe[i]):
                    if pe[i] > 4.5:
                        facies[i] = 'carbonate_tight'
                    elif pe[i] < 2.0:
                        facies[i] = 'sandstone_tight'
                    else:
                        facies[i] = 'mixed_tight'
                else:
                    facies[i] = 'tight_rock'
                    
            elif rho > 2.4 and rho < 2.8 and phi > 0.1 and phi < 0.3:
                if pe is not None and not np.isnan(pe[i]):
                    if pe[i] > 4.0:
                        facies[i] = 'carbonate_reservoir'
                    elif pe[i] < 2.5:
                        facies[i] = 'sandstone_reservoir'
                    else:
                        facies[i] = 'mixed_reservoir'
                else:
                    facies[i] = 'good_reservoir'
                    
            elif phi > 0.3:
                facies[i] = 'shale_clay'
                
            elif rho < 2.2:
                facies[i] = 'coal_organic'
                
            else:
                facies[i] = 'intermediate'
        
        return facies
    
    def reservoir_quality_assessment(self,
                                   porosity: Union[np.ndarray, List[float]],
                                   permeability: Union[np.ndarray, List[float]],
                                   vclay: Optional[Union[np.ndarray, List[float]]] = None,
                                   sw: Optional[Union[np.ndarray, List[float]]] = None) -> Dict:
        """
        Evaluación de calidad de reservorio basada en petrofísica.
        
        Args:
            porosity: Porosidad efectiva (fracción)
            permeability: Permeabilidad (mD)
            vclay: Volumen de arcilla (fracción) - opcional
            sw: Saturación de agua (fracción) - opcional
            
        Returns:
            Dict: Evaluación completa de calidad
        """
        logger.info("🧮 Evaluando calidad de reservorio")
        
        try:
            # Validar datos básicos
            porosity = self.validate_input(porosity, "POROSITY", valid_range=(0.01, 0.5))
            permeability = self.validate_input(permeability, "PERMEABILITY", valid_range=(0.001, 10000))
            
            n_points = len(porosity)
            
            # Clasificación de porosidad
            phi_quality = np.full(n_points, 'poor', dtype='<U10')
            phi_quality[(porosity >= 0.05) & (porosity < 0.1)] = 'fair'
            phi_quality[(porosity >= 0.1) & (porosity < 0.15)] = 'good'
            phi_quality[(porosity >= 0.15)] = 'excellent'
            
            # Clasificación de permeabilidad
            perm_quality = np.full(n_points, 'tight', dtype='<U10')
            perm_quality[(permeability >= 0.1) & (permeability < 1)] = 'poor'
            perm_quality[(permeability >= 1) & (permeability < 10)] = 'fair'
            perm_quality[(permeability >= 10) & (permeability < 100)] = 'good'
            perm_quality[(permeability >= 100)] = 'excellent'
            
            # Índice de calidad combinado (RQI - Reservoir Quality Index)
            # RQI = 0.0314 * sqrt(K/φ)
            rqi = 0.0314 * np.sqrt(permeability / porosity)
            
            # Clasificación RQI
            rqi_quality = np.full(n_points, 'poor', dtype='<U10')
            rqi_quality[(rqi >= 0.1) & (rqi < 0.5)] = 'fair'
            rqi_quality[(rqi >= 0.5) & (rqi < 1.0)] = 'good'
            rqi_quality[(rqi >= 1.0)] = 'excellent'
            
            # Evaluación de arcilla si disponible
            clay_impact = None
            if vclay is not None:
                vclay = self.validate_input(vclay, "VCLAY", valid_range=(0.0, 1.0))
                clay_impact = np.full(n_points, 'clean', dtype='<U15')
                clay_impact[(vclay >= 0.1) & (vclay < 0.25)] = 'slightly_shaly'
                clay_impact[(vclay >= 0.25) & (vclay < 0.5)] = 'moderately_shaly'
                clay_impact[(vclay >= 0.5)] = 'very_shaly'
            
            # Evaluación de saturación si disponible
            hc_potential = None
            if sw is not None:
                sw = self.validate_input(sw, "SW", valid_range=(0.0, 1.0))
                sh = 1.0 - sw  # Saturación de hidrocarburos
                hc_potential = np.full(n_points, 'water', dtype='<U15')
                hc_potential[(sh >= 0.1) & (sh < 0.3)] = 'low_hc'
                hc_potential[(sh >= 0.3) & (sh < 0.6)] = 'moderate_hc'
                hc_potential[(sh >= 0.6)] = 'high_hc'
            
            # Clasificación final combinada
            overall_quality = self._combine_quality_assessments(
                phi_quality, perm_quality, rqi_quality, clay_impact, hc_potential
            )
            
            # Estadísticas por zona de calidad
            quality_stats = self._calculate_quality_statistics(
                overall_quality, porosity, permeability, rqi
            )
            
            result = {
                'porosity_quality': phi_quality,
                'permeability_quality': perm_quality,
                'rqi': rqi,
                'rqi_quality': rqi_quality,
                'clay_impact': clay_impact,
                'hydrocarbon_potential': hc_potential,
                'overall_quality': overall_quality,
                'quality_statistics': quality_stats,
                'cutoffs_used': {
                    'porosity': {'poor': '<5%', 'fair': '5-10%', 'good': '10-15%', 'excellent': '>15%'},
                    'permeability': {'tight': '<0.1mD', 'poor': '0.1-1mD', 'fair': '1-10mD', 
                                   'good': '10-100mD', 'excellent': '>100mD'},
                    'rqi': {'poor': '<0.1', 'fair': '0.1-0.5', 'good': '0.5-1.0', 'excellent': '>1.0'}
                },
                'success': True
            }
            
            logger.info("✅ Evaluación de calidad completada")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en evaluación de calidad: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _combine_quality_assessments(self, phi_qual, perm_qual, rqi_qual, clay_impact, hc_potential):
        """Combinar evaluaciones individuales en calidad general."""
        n_points = len(phi_qual)
        overall = np.full(n_points, 'poor', dtype='<U15')
        
        quality_scores = {
            'poor': 1, 'tight': 1, 'clean': 0,
            'fair': 2, 'slightly_shaly': 1,
            'good': 3, 'moderately_shaly': 2,
            'excellent': 4, 'very_shaly': 3
        }
        
        for i in range(n_points):
            # Calcular score promedio
            scores = [
                quality_scores.get(phi_qual[i], 1),
                quality_scores.get(perm_qual[i], 1),
                quality_scores.get(rqi_qual[i], 1)
            ]
            
            # Penalizar por arcilla
            if clay_impact is not None:
                clay_penalty = quality_scores.get(clay_impact[i], 0)
                avg_score = (sum(scores) / len(scores)) - (clay_penalty * 0.5)
            else:
                avg_score = sum(scores) / len(scores)
            
            # Clasificar
            if avg_score >= 3.5:
                overall[i] = 'excellent'
            elif avg_score >= 2.5:
                overall[i] = 'good'
            elif avg_score >= 1.5:
                overall[i] = 'fair'
            else:
                overall[i] = 'poor'
        
        return overall
    
    def _calculate_quality_statistics(self, quality_classes, porosity, permeability, rqi):
        """Calcular estadísticas por clase de calidad."""
        unique_classes = np.unique(quality_classes)
        stats = {}
        
        for qual_class in unique_classes:
            if qual_class == 'unknown':
                continue
                
            mask = quality_classes == qual_class
            if np.any(mask):
                stats[qual_class] = {
                    'count': np.sum(mask),
                    'percentage': (np.sum(mask) / len(quality_classes)) * 100,
                    'avg_porosity': np.nanmean(porosity[mask]),
                    'avg_permeability': np.nanmean(permeability[mask]),
                    'avg_rqi': np.nanmean(rqi[mask])
                }
        
        return stats
    
    def photoelectric_analysis(self,
                              pe: Union[np.ndarray, List[float]],
                              rhob: Union[np.ndarray, List[float]],
                              nphi: Optional[Union[np.ndarray, List[float]]] = None) -> Dict:
        """
        Análisis del factor fotoeléctrico para identificación de minerales.
        
        Args:
            pe: Factor fotoeléctrico (barns/electron)
            rhob: Densidad bulk (g/cm³)
            nphi: Porosidad neutrón (fracción) - opcional
            
        Returns:
            Dict: Análisis mineralógico basado en PE
        """
        logger.info("🧮 Ejecutando análisis de factor fotoeléctrico")
        
        try:
            pe = self.validate_input(pe, "PE", valid_range=(0.5, 10.0))
            rhob = self.validate_input(rhob, "RHOB", valid_range=(1.5, 3.2))
            
            n_points = len(pe)
            mineral_id = np.full(n_points, 'unknown', dtype='<U15')
            
            # Identificación mineralógica basada en PE y densidad
            for i in range(n_points):
                if np.isnan(pe[i]) or np.isnan(rhob[i]):
                    continue
                
                pe_val = pe[i]
                rho_val = rhob[i]
                
                # Reglas de clasificación basadas en crossplot PE-RHOB
                if pe_val < 2.0 and rho_val < 2.7:
                    mineral_id[i] = 'quartz_sandstone'
                elif pe_val > 4.5 and rho_val > 2.65:
                    mineral_id[i] = 'limestone'
                elif pe_val > 2.8 and pe_val < 3.5 and rho_val > 2.8:
                    mineral_id[i] = 'dolomite'
                elif pe_val > 5.0 and rho_val > 2.9:
                    mineral_id[i] = 'anhydrite'
                elif pe_val > 2.5 and pe_val < 3.5 and rho_val < 2.5:
                    mineral_id[i] = 'clay_shale'
                elif pe_val < 1.5:
                    mineral_id[i] = 'coal_organic'
                else:
                    mineral_id[i] = 'mixed_lithology'
            
            # Estadísticas mineralógicas
            mineral_stats = {}
            unique_minerals = np.unique(mineral_id)
            
            for mineral in unique_minerals:
                if mineral != 'unknown':
                    mask = mineral_id == mineral
                    mineral_stats[mineral] = {
                        'count': np.sum(mask),
                        'percentage': (np.sum(mask) / len(mineral_id)) * 100,
                        'avg_pe': np.nanmean(pe[mask]),
                        'avg_rhob': np.nanmean(rhob[mask])
                    }
            
            result = {
                'mineral_identification': mineral_id,
                'mineral_statistics': mineral_stats,
                'pe_rhob_analysis': True,
                'success': True
            }
            
            logger.info(f"✅ Análisis PE completado. {len(unique_minerals)} minerales identificados")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis PE: {str(e)}")
            return {'success': False, 'error': str(e)}
