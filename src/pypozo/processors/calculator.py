"""
PyPozo 2.0 - Calculador Geofísico
=================================

GeophysicsCalculator realiza cálculos geofísicos estándar sobre datos de pozos,
incluyendo VSH, porosidad, saturación, zonas de interés, etc.

Cálculos disponibles:
- Volumen de lutitas (VSH) - Larionov, Steiber, Clavier
- Porosidad - Densidad, Neutrón, Combinada
- Saturación de agua - Archie, Simandoux
- Identificación de zonas acuíferas
- Detección de formaciones duras
- Análisis de correlaciones

Autor: José María García Márquez
Fecha: Junio 2025
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from scipy import stats

from ..core.well import WellManager

logger = logging.getLogger(__name__)

class GeophysicsCalculator:
    """
    Calculador de propiedades geofísicas.
    
    Esta clase implementa los cálculos geofísicos estándar
    utilizados en la interpretación de registros de pozos.
    """
    
    def __init__(self):
        """Inicializar calculador geofísico."""
        self.calculations_performed = []
        logger.info("🔬 GeophysicsCalculator inicializado")
    
    def calculate_vsh(self, well: WellManager, 
                     method: str = 'larionov', 
                     gr_clean: float = 20.0,
                     gr_clay: float = 150.0) -> Optional[pd.Series]:
        """
        Calcular Volumen de Lutitas (VSH).
        
        Args:
            well: WellManager con datos
            method: Método de cálculo ('larionov', 'steiber', 'clavier')
            gr_clean: Valor GR de arena limpia (API)
            gr_clay: Valor GR de lutita pura (API)
            
        Returns:
            pd.Series: VSH calculado
        """
        gr_data = well.get_curve_data('GR')
        if gr_data is None:
            logger.warning("⚠️ Curva GR no disponible para cálculo de VSH")
            return None
        
        # Calcular IGR (Gamma Ray Index)
        igr = (gr_data - gr_clean) / (gr_clay - gr_clean)
        igr = igr.clip(0, 1)  # Limitar entre 0 y 1
        
        # Aplicar ecuación según método
        if method.lower() == 'larionov':
            # Larionov (1969) - Para rocas paleozoicas
            vsh = 0.083 * (2**(3.7 * igr) - 1)
        elif method.lower() == 'steiber':
            # Steiber (1970) - Para rocas terciarias
            vsh = igr / (3 - 2 * igr)
        elif method.lower() == 'clavier':
            # Clavier (1971)
            vsh = 1.7 - np.sqrt(3.38 - (igr + 0.7)**2)
        else:
            logger.error(f"❌ Método VSH no reconocido: {method}")
            return None
        
        # Limitar VSH entre 0 y 1
        vsh = vsh.clip(0, 1)
        
        # Registrar cálculo
        self.calculations_performed.append({
            'calculation': 'VSH',
            'method': method,
            'well': well.name,
            'parameters': {'gr_clean': gr_clean, 'gr_clay': gr_clay}
        })
        
        logger.info(f"✅ VSH calculado usando método {method}")
        return vsh
    
    def calculate_porosity_density(self, well: WellManager,
                                  matrix_density: float = 2.65,
                                  fluid_density: float = 1.0) -> Optional[pd.Series]:
        """
        Calcular porosidad usando registro de densidad.
        
        Args:
            well: WellManager con datos
            matrix_density: Densidad de la matriz (g/cm³)
            fluid_density: Densidad del fluido (g/cm³)
            
        Returns:
            pd.Series: Porosidad calculada
        """
        rhob_data = well.get_curve_data('RHOB')
        if rhob_data is None:
            logger.warning("⚠️ Curva RHOB no disponible para cálculo de porosidad")
            return None
        
        # Ecuación de porosidad por densidad
        porosity = (matrix_density - rhob_data) / (matrix_density - fluid_density)
        porosity = porosity.clip(0, 1)  # Limitar entre 0 y 1
        
        # Registrar cálculo
        self.calculations_performed.append({
            'calculation': 'Porosity_Density',
            'well': well.name,
            'parameters': {'matrix_density': matrix_density, 'fluid_density': fluid_density}
        })
        
        logger.info("✅ Porosidad calculada usando densidad")
        return porosity
    
    def calculate_porosity_neutron(self, well: WellManager) -> Optional[pd.Series]:
        """
        Calcular porosidad usando registro de neutrón.
        
        Args:
            well: WellManager con datos
            
        Returns:
            pd.Series: Porosidad por neutrón
        """
        nphi_data = well.get_curve_data('NPHI')
        if nphi_data is None:
            logger.warning("⚠️ Curva NPHI no disponible para cálculo de porosidad")
            return None
        
        # Para este ejemplo, usamos NPHI directamente
        # En la práctica, se aplicarían correcciones por lutitas
        porosity_neutron = nphi_data.clip(0, 1)
        
        # Registrar cálculo
        self.calculations_performed.append({
            'calculation': 'Porosity_Neutron',
            'well': well.name,
            'parameters': {}
        })
        
        logger.info("✅ Porosidad calculada usando neutrón")
        return porosity_neutron
    
    def calculate_porosity_combined(self, well: WellManager,
                                   matrix_density: float = 2.65,
                                   fluid_density: float = 1.0) -> Optional[pd.Series]:
        """
        Calcular porosidad combinada (densidad + neutrón).
        
        Args:
            well: WellManager con datos
            matrix_density: Densidad de la matriz
            fluid_density: Densidad del fluido
            
        Returns:
            pd.Series: Porosidad combinada
        """
        phi_d = self.calculate_porosity_density(well, matrix_density, fluid_density)
        phi_n = self.calculate_porosity_neutron(well)
        
        if phi_d is None or phi_n is None:
            logger.warning("⚠️ No se pueden calcular ambas porosidades para combinación")
            return None
        
        # Promedio geométrico (común en la industria)
        porosity_combined = np.sqrt(phi_d * phi_n)
        porosity_combined = porosity_combined.clip(0, 1)
        
        # Registrar cálculo
        self.calculations_performed.append({
            'calculation': 'Porosity_Combined',
            'well': well.name,
            'parameters': {'matrix_density': matrix_density, 'fluid_density': fluid_density}
        })
        
        logger.info("✅ Porosidad combinada calculada")
        return porosity_combined
    
    def calculate_water_saturation_archie(self, well: WellManager,
                                         porosity: Optional[pd.Series] = None,
                                         a: float = 1.0, m: float = 2.0, n: float = 2.0,
                                         rw: float = 0.1) -> Optional[pd.Series]:
        """
        Calcular saturación de agua usando ecuación de Archie.
        
        Args:
            well: WellManager con datos
            porosity: Porosidad (se calcula si no se proporciona)
            a: Constante de tortuosidad
            m: Exponente de cementación
            n: Exponente de saturación
            rw: Resistividad del agua de formación
            
        Returns:
            pd.Series: Saturación de agua
        """
        rt_data = well.get_curve_data('RT')
        if rt_data is None:
            logger.warning("⚠️ Curva RT no disponible para cálculo de saturación")
            return None
        
        if porosity is None:
            porosity = self.calculate_porosity_combined(well)
            if porosity is None:
                logger.warning("⚠️ No se puede calcular porosidad para saturación")
                return None
        
        # Ecuación de Archie: Sw = ((a * Rw) / (phi^m * Rt))^(1/n)
        sw = ((a * rw) / (porosity**m * rt_data))**(1/n)
        sw = sw.clip(0, 1)  # Limitar entre 0 y 1
        
        # Registrar cálculo
        self.calculations_performed.append({
            'calculation': 'Water_Saturation_Archie',
            'well': well.name,
            'parameters': {'a': a, 'm': m, 'n': n, 'rw': rw}
        })
        
        logger.info("✅ Saturación de agua calculada (Archie)")
        return sw
    
    def identify_reservoir_zones(self, well: WellManager,
                                vsh_cutoff: float = 0.5,
                                porosity_cutoff: float = 0.08,
                                saturation_cutoff: float = 0.6) -> Dict[str, Any]:
        """
        Identificar zonas de yacimiento potencial.
        
        Args:
            well: WellManager con datos
            vsh_cutoff: Corte de VSH (menor = mejor)
            porosity_cutoff: Corte de porosidad (mayor = mejor)
            saturation_cutoff: Corte de saturación de agua (menor = mejor)
            
        Returns:
            Dict: Información de zonas identificadas
        """
        # Calcular propiedades necesarias
        vsh = self.calculate_vsh(well)
        porosity = self.calculate_porosity_combined(well)
        sw = self.calculate_water_saturation_archie(well, porosity)
        
        if any(prop is None for prop in [vsh, porosity, sw]):
            logger.warning("⚠️ No se pueden calcular todas las propiedades para identificación de zonas")
            return {'zones_identified': 0, 'total_thickness': 0}
        
        # Identificar zonas que cumplen criterios
        good_zones = (
            (vsh <= vsh_cutoff) & 
            (porosity >= porosity_cutoff) & 
            (sw <= saturation_cutoff)
        )
        
        # Calcular estadísticas
        zones_count = good_zones.sum()
        total_thickness = zones_count * 0.5  # Asumiendo paso de 0.5m
        
        # Profundidades de zonas buenas
        good_depths = vsh.index[good_zones].tolist()
        
        result = {
            'zones_identified': int(zones_count),
            'total_thickness': float(total_thickness),
            'good_depths': good_depths[:10],  # Primeras 10 profundidades
            'criteria': {
                'vsh_cutoff': vsh_cutoff,
                'porosity_cutoff': porosity_cutoff,
                'saturation_cutoff': saturation_cutoff
            },
            'statistics': {
                'avg_vsh_in_zones': float(vsh[good_zones].mean()) if zones_count > 0 else 0,
                'avg_porosity_in_zones': float(porosity[good_zones].mean()) if zones_count > 0 else 0,
                'avg_saturation_in_zones': float(sw[good_zones].mean()) if zones_count > 0 else 0
            }
        }
        
        logger.info(f"🏔️ Zonas identificadas: {zones_count} zonas")
        return result
    
    def identify_hard_formations(self, well: WellManager,
                                pe_threshold: float = 4.0,
                                density_threshold: float = 2.7) -> Dict[str, Any]:
        """
        Identificar formaciones duras (carbonatos, evaporitas).
        
        Args:
            well: WellManager con datos
            pe_threshold: Umbral de PEF para formaciones duras
            density_threshold: Umbral de densidad
            
        Returns:
            Dict: Información de formaciones duras
        """
        pe_data = well.get_curve_data('PEF')
        rhob_data = well.get_curve_data('RHOB')
        
        if pe_data is None or rhob_data is None:
            logger.warning("⚠️ Insuficientes registros para identificar formaciones duras")
            return {'hard_formations': 0, 'total_thickness': 0}
        
        # Identificar formaciones duras
        hard_formations = (pe_data >= pe_threshold) & (rhob_data >= density_threshold)
        
        formations_count = hard_formations.sum()
        total_thickness = formations_count * 0.5  # Asumiendo paso de 0.5m
        
        result = {
            'hard_formations': int(formations_count),
            'total_thickness': float(total_thickness),
            'criteria': {
                'pe_threshold': pe_threshold,
                'density_threshold': density_threshold
            }
        }
        
        logger.info(f"🗿 Formaciones duras identificadas: {formations_count}")
        return result
    
    def calculate_curve_correlation(self, well: WellManager,
                                   curve1: str, curve2: str) -> Optional[Dict[str, float]]:
        """
        Calcular correlación entre dos curvas.
        
        Args:
            well: WellManager con datos
            curve1: Nombre de la primera curva
            curve2: Nombre de la segunda curva
            
        Returns:
            Dict: Estadísticas de correlación
        """
        data1 = well.get_curve_data(curve1)
        data2 = well.get_curve_data(curve2)
        
        if data1 is None or data2 is None:
            logger.warning(f"⚠️ No se pueden obtener datos para correlación: {curve1}, {curve2}")
            return None
        
        # Alinear datos y remover NaN
        combined = pd.DataFrame({curve1: data1, curve2: data2}).dropna()
        
        if len(combined) < 10:
            logger.warning(f"⚠️ Insuficientes datos para correlación: {len(combined)} puntos")
            return None
        
        # Calcular correlación
        correlation, p_value = stats.pearsonr(combined[curve1], combined[curve2])
        
        result = {
            'correlation': float(correlation),
            'p_value': float(p_value),
            'data_points': len(combined),
            'significant': p_value < 0.05
        }
        
        logger.info(f"📊 Correlación {curve1}-{curve2}: r={correlation:.3f}, p={p_value:.3f}")
        return result
    
    def perform_complete_analysis(self, well: WellManager) -> Dict[str, Any]:
        """
        Realizar análisis geofísico completo de un pozo.
        
        Args:
            well: WellManager con datos
            
        Returns:
            Dict: Resultados del análisis completo
        """
        logger.info(f"🔬 Iniciando análisis geofísico completo: {well.name}")
        
        results = {
            'well_name': well.name,
            'success': True,
            'calculations_performed': 0,
            'results': {}
        }
        
        try:
            # 1. Calcular VSH
            vsh = self.calculate_vsh(well)
            if vsh is not None:
                results['results']['vsh'] = {
                    'calculated': True,
                    'mean': float(vsh.mean()),
                    'std': float(vsh.std()),
                    'min': float(vsh.min()),
                    'max': float(vsh.max())
                }
                results['calculations_performed'] += 1
            
            # 2. Calcular porosidad
            porosity = self.calculate_porosity_combined(well)
            if porosity is not None:
                results['results']['porosity'] = {
                    'calculated': True,
                    'mean': float(porosity.mean()),
                    'std': float(porosity.std()),
                    'min': float(porosity.min()),
                    'max': float(porosity.max())
                }
                results['calculations_performed'] += 1
            
            # 3. Calcular saturación de agua
            sw = self.calculate_water_saturation_archie(well, porosity)
            if sw is not None:
                results['results']['water_saturation'] = {
                    'calculated': True,
                    'mean': float(sw.mean()),
                    'std': float(sw.std()),
                    'min': float(sw.min()),
                    'max': float(sw.max())
                }
                results['calculations_performed'] += 1
            
            # 4. Identificar zonas de yacimiento
            reservoir_zones = self.identify_reservoir_zones(well)
            results['results']['reservoir_zones'] = reservoir_zones
            
            # 5. Identificar formaciones duras
            hard_formations = self.identify_hard_formations(well)
            results['results']['hard_formations'] = hard_formations
            
            # 6. Correlaciones importantes
            correlations = {}
            important_pairs = [('GR', 'RHOB'), ('GR', 'NPHI'), ('RHOB', 'NPHI')]
            
            for curve1, curve2 in important_pairs:
                corr_result = self.calculate_curve_correlation(well, curve1, curve2)
                if corr_result:
                    correlations[f'{curve1}_{curve2}'] = corr_result
            
            results['results']['correlations'] = correlations
            
            # Registrar en historial del pozo
            well.add_processing_step(
                'complete_geophysical_analysis',
                {
                    'calculations_performed': results['calculations_performed'],
                    'reservoir_zones': reservoir_zones['zones_identified'],
                    'hard_formations': hard_formations['hard_formations']
                }
            )
            
            logger.info(f"✅ Análisis completado: {results['calculations_performed']} cálculos")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis geofísico: {str(e)}")
            results['success'] = False
            results['error'] = str(e)
        
        return results
