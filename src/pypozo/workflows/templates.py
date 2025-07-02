"""
Workflow Templates
================

Templates predefinidos para diferentes tipos de análisis petrofísico.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from .base import BaseWorkflow, WorkflowStep
from ..petrophysics import VclCalculator, PorosityCalculator

class BasicPetrophysicsWorkflow(BaseWorkflow):
    """
    Workflow básico de petrofísica: VCL y PHIE.
    
    Pasos:
    1. Calcular VCL desde GR
    2. Calcular PHIE desde RHOB/NPHI
    3. Aplicar correcciones
    4. Generar reporte QC
    """
    
    def __init__(self):
        super().__init__(
            name="Petrofísica Básica",
            description="Cálculo de VCL y PHIE con controles de calidad"
        )
        self.vcl_calculator = VclCalculator()
        self.porosity_calculator = PorosityCalculator()
        self.setup_steps()
    
    def setup_steps(self):
        """Configurar pasos del workflow."""
        
        # Paso 1: VCL
        vcl_step = WorkflowStep(
            name="Calcular VCL",
            description="Cálculo de volumen de arcilla desde Gamma Ray",
            required_curves=["GR"],
            output_curves=["VCL_LINEAR", "VCL_LARIONOV"],
            parameters={
                "methods": ["linear", "larionov_tertiary"],
                "gr_min": 15,
                "gr_max": 150
            }
        )
        self.add_step(vcl_step)
        
        # Paso 2: PHIE
        phie_step = WorkflowStep(
            name="Calcular PHIE",
            description="Cálculo de porosidad efectiva",
            required_curves=["RHOB", "NPHI"],
            output_curves=["PHIE_DENSITY", "PHIE_NEUTRON", "PHIE_COMBINED"],
            parameters={
                "methods": ["density", "neutron", "combined"],
                "rho_ma": 2.65,
                "rho_fl": 1.0
            }
        )
        self.add_step(phie_step)
        
        # Paso 3: QC
        qc_step = WorkflowStep(
            name="Control de Calidad",
            description="Validación y reportes de QC",
            required_curves=["VCL_LARIONOV", "PHIE_COMBINED"],
            output_curves=[],
            parameters={}
        )
        self.add_step(qc_step)
    
    def validate_well(self, well_manager) -> bool:
        """Validar curvas mínimas requeridas."""
        required = ["GR", "RHOB", "NPHI"]
        available = well_manager.curves
        
        missing = [curve for curve in required if curve not in available]
        
        if missing:
            self.execution_log.append(f"❌ Curvas faltantes: {missing}")
            return False
        
        return True
    
    def _execute_step(self, step: WorkflowStep, well_manager) -> Dict[str, Any]:
        """Ejecutar paso específico."""
        
        if step.name == "Calcular VCL":
            return self._execute_vcl_step(step, well_manager)
        elif step.name == "Calcular PHIE":
            return self._execute_phie_step(step, well_manager)
        elif step.name == "Control de Calidad":
            return self._execute_qc_step(step, well_manager)
        else:
            raise ValueError(f"Paso desconocido: {step.name}")
    
    def _execute_vcl_step(self, step: WorkflowStep, well_manager) -> Dict[str, Any]:
        """Ejecutar cálculo de VCL."""
        gr_data = well_manager.get_curve_data("GR")
        results = {}
        
        for method in step.parameters["methods"]:
            vcl_result = self.vcl_calculator.calculate(
                gr_data,
                method=method,
                gr_clean=step.parameters["gr_min"],
                gr_clay=step.parameters["gr_max"]
            )
            
            curve_name = f"VCL_{method.upper()}"
            well_manager.add_curve(curve_name, vcl_result['vcl'])
            results[method] = vcl_result
        
        return results
    
    def _execute_phie_step(self, step: WorkflowStep, well_manager) -> Dict[str, Any]:
        """Ejecutar cálculo de PHIE."""
        rhob_data = well_manager.get_curve_data("RHOB")
        nphi_data = well_manager.get_curve_data("NPHI")
        results = {}
        
        # Porosidad densidad
        density_result = self.porosity_calculator.calculate_density_porosity(
            rhob_data, 
            matrix_density=step.parameters["rho_ma"],
            fluid_density=step.parameters["rho_fl"]
        )
        well_manager.add_curve("PHIE_DENSITY", density_result['phid'])
        results['density'] = density_result
        
        # Porosidad neutrón
        neutron_result = self.porosity_calculator.calculate_neutron_porosity(nphi_data)
        well_manager.add_curve("PHIE_NEUTRON", neutron_result['phin'])
        results['neutron'] = neutron_result
        
        # Porosidad combinada (densidad-neutrón)
        combined_result = self.porosity_calculator.calculate_density_neutron_porosity(
            rhob_data, nphi_data,
            matrix_density=step.parameters["rho_ma"],
            fluid_density=step.parameters["rho_fl"]
        )
        well_manager.add_curve("PHIE_COMBINED", combined_result['phie'])
        results['combined'] = combined_result
        
        return results
    
    def _execute_qc_step(self, step: WorkflowStep, well_manager) -> Dict[str, Any]:
        """Ejecutar control de calidad."""
        results = {}
        
        # QC de VCL (usar la curva larionov_tertiary que se generó)
        vcl_data = well_manager.get_curve_data("VCL_LARIONOV_TERTIARY")
        vcl_stats = {
            'mean': np.nanmean(vcl_data),
            'std': np.nanstd(vcl_data),
            'min': np.nanmin(vcl_data),
            'max': np.nanmax(vcl_data),
            'valid_count': np.sum(~np.isnan(vcl_data))
        }
        results['vcl_qc'] = vcl_stats
        
        # QC de PHIE
        phie_data = well_manager.get_curve_data("PHIE_COMBINED")
        phie_stats = {
            'mean': np.nanmean(phie_data),
            'std': np.nanstd(phie_data),
            'min': np.nanmin(phie_data),
            'max': np.nanmax(phie_data),
            'valid_count': np.sum(~np.isnan(phie_data))
        }
        results['phie_qc'] = phie_stats
        
        # Banderas de calidad
        quality_flags = {
            'vcl_range_ok': 0 <= vcl_stats['min'] and vcl_stats['max'] <= 1,
            'phie_range_ok': 0 <= phie_stats['min'] and phie_stats['max'] <= 0.5,
            'data_completeness': (vcl_stats['valid_count'] / len(vcl_data)) > 0.8
        }
        results['quality_flags'] = quality_flags
        
        return results

class SandstoneAnalysisWorkflow(BasicPetrophysicsWorkflow):
    """
    Workflow especializado para análisis de areniscas.
    
    Extiende el workflow básico con:
    - Parámetros optimizados para areniscas
    - Análisis de saturación de agua
    - Estimación de permeabilidad
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Análisis de Areniscas"
        self.description = "Análisis petrofísico completo para formaciones de areniscas"
        
        # Agregar pasos específicos
        self._add_sandstone_steps()
    
    def _add_sandstone_steps(self):
        """Agregar pasos específicos para areniscas."""
        
        # Paso adicional: Análisis litológico
        lithology_step = WorkflowStep(
            name="Análisis Litológico",
            description="Identificación de facies de areniscas",
            required_curves=["RHOB", "NPHI", "VCL_LARIONOV"],
            output_curves=["LITHOLOGY", "FACIES"],
            parameters={
                "min_sand_cutoff": 0.35,  # VCL < 0.35 = arena limpia
                "max_shale_cutoff": 0.65  # VCL > 0.65 = lutita
            }
        )
        self.add_step(lithology_step)
        
        # Actualizar parámetros para areniscas
        for step in self.steps:
            if step.name == "Calcular PHIE":
                step.parameters.update({
                    "rho_ma": 2.65,  # Cuarzo
                    "rho_fl": 1.0    # Agua dulce
                })

class CarbonateAnalysisWorkflow(BasicPetrophysicsWorkflow):
    """
    Workflow especializado para análisis de carbonatos.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Análisis de Carbonatos"
        self.description = "Análisis petrofísico para formaciones carbonáticas"
        
        # Ajustar parámetros para carbonatos
        self._adjust_for_carbonates()
    
    def _adjust_for_carbonates(self):
        """Ajustar parámetros para carbonatos."""
        
        for step in self.steps:
            if step.name == "Calcular VCL":
                # Carbonatos tienen menor respuesta GR
                step.parameters.update({
                    "gr_min": 10,
                    "gr_max": 80
                })
            elif step.name == "Calcular PHIE":
                # Densidad matriz de caliza
                step.parameters.update({
                    "rho_ma": 2.71,  # Calcita
                    "rho_fl": 1.0
                })

class CompletionOptimizationWorkflow(SandstoneAnalysisWorkflow):
    """
    Workflow para optimización de completación.
    
    Incluye análisis de:
    - Calidad de roca
    - Zonas de interés
    - Recomendaciones de fractura
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Optimización de Completación"
        self.description = "Análisis para optimizar diseño de completación"
        
        self._add_completion_steps()
    
    def _add_completion_steps(self):
        """Agregar pasos para optimización de completación."""
        
        # Índice de calidad de roca
        rqi_step = WorkflowStep(
            name="Índice de Calidad",
            description="Cálculo de índice de calidad de roca",
            required_curves=["PHIE_CORRECTED", "VCL_LARIONOV"],
            output_curves=["RQI", "COMPLETION_ZONES"],
            parameters={
                "min_porosity": 0.08,
                "max_vcl": 0.35,
                "zone_thickness": 5.0  # metros
            }
        )
        self.add_step(rqi_step)
