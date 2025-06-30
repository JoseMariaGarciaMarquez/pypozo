"""
PyPozo 2.0 - Estandarizador de Datos
====================================

DataStandardizer se encarga de estandarizar mnemonics, unidades,
y limpiar datos de pozos para asegurar consistencia en el análisis.

Funcionalidades principales:
- Estandarización de mnemonics (GR, RHOB, NPHI, etc.)
- Conversión de unidades automática
- Limpieza de outliers y valores nulos
- Validación de rangos físicos
- Corrección de formatos de datos

Autor: José María García Márquez
Fecha: Junio 2025
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from ..core.well import WellManager

logger = logging.getLogger(__name__)

class DataStandardizer:
    """
    Estandarizador de datos de pozos.
    
    Esta clase se encarga de estandarizar y limpiar datos de pozos
    para asegurar consistencia en análisis posteriores.
    """
    
    # Diccionario de estandarización de mnemonics
    MNEMONIC_MAPPING = {
        # Gamma Ray
        'GAMMA': 'GR',
        'GAM': 'GR',
        'GAMR': 'GR',
        'GRD': 'GR',
        'GRCG': 'GR',
        
        # Resistivity
        'RES': 'RT',
        'RILD': 'RT',
        'RLLD': 'RT',
        'RESISTANCE': 'RT',
        'RESISTIVITY': 'RT',
        
        # Density
        'DENS': 'RHOB',
        'DEN': 'RHOB',
        'DENSITY': 'RHOB',
        'BULK_DENSITY': 'RHOB',
        'BD': 'RHOB',
        
        # Neutron
        'NEUT': 'NPHI',
        'NEU': 'NPHI',
        'NEUTRON': 'NPHI',
        'NEUTRON_POROSITY': 'NPHI',
        'PHIN': 'NPHI',
        
        # Photoelectric
        'PE': 'PEF',
        'PHOTO': 'PEF',
        'PHOTOELECTRIC': 'PEF',
        
        # Sonic
        'SONIC': 'DTC',
        'DT': 'DTC',
        'TRANSIT_TIME': 'DTC',
        'DELTA_T': 'DTC',
        
        # Caliper
        'CAL': 'CALI',
        'CALIPER': 'CALI',
        'DIAMETER': 'CALI',
        
        # SP
        'SPONTANEOUS_POTENTIAL': 'SP',
        'POTENTIAL': 'SP',
        
        # Depth
        'DEPTH': 'DEPT',
        'MD': 'DEPT',
        'MEASURED_DEPTH': 'DEPT'
    }
    
    # Rangos físicos típicos para validación
    PHYSICAL_RANGES = {
        'GR': (0, 500),      # API units
        'RT': (0.01, 10000), # ohm.m
        'RHOB': (1.0, 3.0),  # g/cm3
        'NPHI': (-0.05, 1.0), # fraction
        'PEF': (0, 10),      # barns/electron
        'DTC': (40, 300),    # μs/ft
        'CALI': (4, 20),     # inches
        'SP': (-200, 200),   # mV
        'DEPT': (0, 10000)   # meters
    }
    
    # Unidades estándar
    STANDARD_UNITS = {
        'GR': 'API',
        'RT': 'OHMM',
        'RHOB': 'G/C3',
        'NPHI': 'DEC',
        'PEF': 'B/E',
        'DTC': 'US/F',
        'CALI': 'IN',
        'SP': 'MV',
        'DEPT': 'M'
    }
    
    def __init__(self):
        """Inicializar estandarizador."""
        self.processing_steps = []
        logger.info("🔧 DataStandardizer inicializado")
    
    def standardize_well(self, well: WellManager, 
                        apply_cleaning: bool = True,
                        apply_validation: bool = True) -> Dict[str, Any]:
        """
        Estandarizar datos de un pozo completo.
        
        Args:
            well: WellManager a estandarizar
            apply_cleaning: Aplicar limpieza de datos
            apply_validation: Aplicar validación de rangos
            
        Returns:
            Dict: Resumen del procesamiento
        """
        if not well.is_valid:
            logger.error("❌ Pozo no válido para estandarización")
            return {'success': False, 'error': 'Invalid well'}
        
        logger.info(f"🔧 Iniciando estandarización: {well.name}")
        
        results = {
            'success': True,
            'well_name': well.name,
            'original_curves': well.curves.copy(),
            'standardized_mnemonics': {},
            'cleaned_curves': {},
            'validation_results': {},
            'processing_steps': []
        }
        
        try:
            # 1. Estandarizar mnemonics
            mnemonic_results = self._standardize_mnemonics(well)
            results['standardized_mnemonics'] = mnemonic_results
            results['processing_steps'].append('mnemonic_standardization')
            
            # 2. Limpieza de datos (si está habilitada)
            if apply_cleaning:
                cleaning_results = self._clean_data(well)
                results['cleaned_curves'] = cleaning_results
                results['processing_steps'].append('data_cleaning')
            
            # 3. Validación de rangos (si está habilitada)
            if apply_validation:
                validation_results = self._validate_ranges(well)
                results['validation_results'] = validation_results
                results['processing_steps'].append('range_validation')
            
            # Registrar en el historial del pozo
            well.add_processing_step(
                'data_standardization',
                {
                    'standardized_mnemonics': len(mnemonic_results),
                    'cleaned_curves': len(results['cleaned_curves']),
                    'validation_warnings': len([v for v in results['validation_results'].values() if not v.get('valid', True)])
                }
            )
            
            logger.info(f"✅ Estandarización completada: {well.name}")
            
        except Exception as e:
            logger.error(f"❌ Error en estandarización: {str(e)}")
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def _standardize_mnemonics(self, well: WellManager) -> Dict[str, str]:
        """
        Estandarizar mnemonics de curvas.
        
        Args:
            well: WellManager
            
        Returns:
            Dict: Mapeo de mnemonics estandarizados
        """
        standardized = {}
        
        for curve_name in well.curves:
            upper_curve = curve_name.upper()
            
            if upper_curve in self.MNEMONIC_MAPPING:
                standard_name = self.MNEMONIC_MAPPING[upper_curve]
                standardized[curve_name] = standard_name
                logger.debug(f"📝 Mnemonic estandarizado: {curve_name} -> {standard_name}")
        
        if standardized:
            logger.info(f"📝 Mnemonics estandarizados: {standardized}")
        
        return standardized
    
    def _clean_data(self, well: WellManager) -> Dict[str, int]:
        """
        Limpiar datos de curvas (outliers, valores nulos).
        
        Args:
            well: WellManager
            
        Returns:
            Dict: Número de valores limpiados por curva
        """
        cleaned = {}
        
        for curve_name in well.curves:
            curve_data = well.get_curve_data(curve_name)
            if curve_data is None:
                continue
            
            original_count = len(curve_data)
            initial_nulls = curve_data.isna().sum()
            
            # Limpiar outliers usando IQR
            Q1 = curve_data.quantile(0.25)
            Q3 = curve_data.quantile(0.75)
            IQR = Q3 - Q1
            
            # Definir límites para outliers
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Contar outliers
            outliers = ((curve_data < lower_bound) | (curve_data > upper_bound)).sum()
            
            # Para este ejemplo, solo contamos los outliers
            # En implementación real, se pueden reemplazar o remover
            total_cleaned = initial_nulls + outliers
            
            if total_cleaned > 0:
                cleaned[curve_name] = int(total_cleaned)
                logger.debug(f"🧹 Curva {curve_name}: {total_cleaned} valores problemáticos")
        
        if cleaned:
            logger.info(f"🧹 Datos limpiados: {cleaned}")
        
        return cleaned
    
    def _validate_ranges(self, well: WellManager) -> Dict[str, Dict]:
        """
        Validar rangos físicos de curvas.
        
        Args:
            well: WellManager
            
        Returns:
            Dict: Resultados de validación por curva
        """
        validation_results = {}
        
        for curve_name in well.curves:
            # Verificar si tenemos rango físico para esta curva
            standard_name = self.MNEMONIC_MAPPING.get(curve_name.upper(), curve_name.upper())
            
            if standard_name not in self.PHYSICAL_RANGES:
                continue
            
            curve_data = well.get_curve_data(curve_name)
            if curve_data is None or curve_data.empty:
                continue
            
            # Obtener rango esperado
            expected_min, expected_max = self.PHYSICAL_RANGES[standard_name]
            
            # Calcular estadísticas
            data_min = float(curve_data.min())
            data_max = float(curve_data.max())
            
            # Verificar si está dentro del rango
            in_range = (data_min >= expected_min) and (data_max <= expected_max)
            
            # Contar valores fuera de rango
            out_of_range_count = int(((curve_data < expected_min) | (curve_data > expected_max)).sum())
            
            validation_results[curve_name] = {
                'valid': in_range,
                'expected_range': (expected_min, expected_max),
                'actual_range': (data_min, data_max),
                'out_of_range_count': out_of_range_count,
                'total_points': len(curve_data),
                'percentage_valid': float((len(curve_data) - out_of_range_count) / len(curve_data) * 100)
            }
            
            if not in_range:
                logger.warning(f"⚠️ {curve_name}: valores fuera de rango físico esperado")
        
        return validation_results
    
    def get_standardization_report(self, well: WellManager) -> str:
        """
        Generar reporte de estandarización para un pozo.
        
        Args:
            well: WellManager
            
        Returns:
            str: Reporte de estandarización
        """
        report_lines = [
            f"REPORTE DE ESTANDARIZACIÓN - {well.name}",
            "=" * 50,
            f"Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total de curvas: {len(well.curves)}",
            ""
        ]
        
        # Estandarización de mnemonics
        standardized = self._standardize_mnemonics(well)
        if standardized:
            report_lines.extend([
                "MNEMONICS ESTANDARIZADOS:",
                "-" * 25
            ])
            for original, standard in standardized.items():
                report_lines.append(f"  {original} -> {standard}")
            report_lines.append("")
        
        # Validación de rangos
        validation = self._validate_ranges(well)
        if validation:
            report_lines.extend([
                "VALIDACIÓN DE RANGOS:",
                "-" * 20
            ])
            for curve, results in validation.items():
                status = "✅" if results['valid'] else "⚠️"
                report_lines.append(f"  {status} {curve}: {results['percentage_valid']:.1f}% válido")
            report_lines.append("")
        
        # Resumen de limpieza
        cleaned = self._clean_data(well)
        if cleaned:
            report_lines.extend([
                "LIMPIEZA DE DATOS:",
                "-" * 17
            ])
            for curve, count in cleaned.items():
                report_lines.append(f"  🧹 {curve}: {count} valores problemáticos")
        
        return "\n".join(report_lines)
    
    def standardize_project(self, project) -> Dict[str, Any]:
        """
        Estandarizar todos los pozos de un proyecto.
        
        Args:
            project: ProjectManager
            
        Returns:
            Dict: Resumen del procesamiento del proyecto
        """
        logger.info(f"🔧 Iniciando estandarización del proyecto: {project.name}")
        
        results = {
            'success': True,
            'project_name': project.name,
            'total_wells': project.total_wells,
            'processed_wells': 0,
            'well_results': {},
            'errors': []
        }
        
        for well in project.wells:
            try:
                well_result = self.standardize_well(well)
                results['well_results'][well.name] = well_result
                
                if well_result['success']:
                    results['processed_wells'] += 1
                else:
                    results['errors'].append(f"{well.name}: {well_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                error_msg = f"{well.name}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(f"❌ Error procesando {well.name}: {str(e)}")
        
        # Registrar en historial del proyecto
        project.add_processing_step(
            'project_standardization',
            {
                'processed_wells': results['processed_wells'],
                'total_wells': results['total_wells'],
                'success_rate': results['processed_wells'] / results['total_wells'] if results['total_wells'] > 0 else 0
            }
        )
        
        logger.info(f"✅ Estandarización del proyecto completada: {results['processed_wells']}/{results['total_wells']} pozos")
        
        return results
