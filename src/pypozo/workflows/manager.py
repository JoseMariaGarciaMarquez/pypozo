"""
Workflow Manager
===============

Gestor para ejecutar y administrar workflows de análisis petrofísico.
"""

from typing import Dict, List, Optional, Any, Callable
import json
from pathlib import Path
import logging
from datetime import datetime

from .base import BaseWorkflow
from .templates import (
    BasicPetrophysicsWorkflow,
    SandstoneAnalysisWorkflow, 
    CarbonateAnalysisWorkflow,
    CompletionOptimizationWorkflow
)

logger = logging.getLogger(__name__)

class WorkflowManager:
    """
    Gestor de workflows petrofísicos.
    
    Permite:
    - Registrar workflows personalizados
    - Ejecutar workflows con seguimiento
    - Guardar/cargar configuraciones
    - Generar reportes
    """
    
    def __init__(self):
        self.available_workflows = {}
        self.executed_workflows = {}
        self.current_workflow = None
        
        # Registrar workflows predefinidos
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Registrar workflows predefinidos."""
        self.register_workflow("basic_petrophysics", BasicPetrophysicsWorkflow)
        self.register_workflow("sandstone_analysis", SandstoneAnalysisWorkflow)
        self.register_workflow("carbonate_analysis", CarbonateAnalysisWorkflow)
        self.register_workflow("completion_optimization", CompletionOptimizationWorkflow)
    
    def register_workflow(self, key: str, workflow_class: type):
        """Registrar un nuevo tipo de workflow."""
        self.available_workflows[key] = workflow_class
        logger.info(f"Workflow registrado: {key}")
    
    def get_available_workflows(self) -> Dict[str, str]:
        """Obtener lista de workflows disponibles."""
        workflows = {}
        for key, workflow_class in self.available_workflows.items():
            # Crear instancia temporal para obtener información
            temp_instance = workflow_class()
            workflows[key] = {
                'name': temp_instance.name,
                'description': temp_instance.description,
                'required_curves': temp_instance.get_required_curves(),
                'output_curves': temp_instance.get_output_curves(),
                'total_steps': len(temp_instance.steps)
            }
        return workflows
    
    def create_workflow(self, workflow_type: str) -> BaseWorkflow:
        """Crear una instancia de workflow."""
        if workflow_type not in self.available_workflows:
            raise ValueError(f"Workflow type '{workflow_type}' not available")
        
        workflow_class = self.available_workflows[workflow_type]
        return workflow_class()
    
    def execute_workflow(self, 
                        workflow_type: str,
                        well_manager,
                        progress_callback: Optional[Callable] = None,
                        save_results: bool = True) -> Dict[str, Any]:
        """
        Ejecutar un workflow completo.
        
        Args:
            workflow_type: Tipo de workflow a ejecutar
            well_manager: Gestor del pozo
            progress_callback: Función para reportar progreso
            save_results: Si guardar resultados para referencia
            
        Returns:
            Resultados del workflow
        """
        
        # Crear workflow
        workflow = self.create_workflow(workflow_type)
        self.current_workflow = workflow
        
        logger.info(f"Iniciando workflow: {workflow.name} para pozo {well_manager.name}")
        
        try:
            # Ejecutar
            results = workflow.execute(well_manager, progress_callback)
            
            # Guardar historial si se solicita
            if save_results:
                execution_record = {
                    'workflow_type': workflow_type,
                    'workflow_name': workflow.name,
                    'well_name': well_manager.name,
                    'execution_time': datetime.now().isoformat(),
                    'is_completed': workflow.is_completed,
                    'summary': workflow.get_summary(),
                    'results_keys': list(results.keys())
                }
                
                self.executed_workflows[f"{well_manager.name}_{workflow_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = execution_record
            
            logger.info(f"Workflow completado exitosamente: {workflow.name}")
            return results
            
        except Exception as e:
            logger.error(f"Error ejecutando workflow {workflow.name}: {str(e)}")
            raise
    
    def validate_well_for_workflow(self, well_manager, workflow_type: str) -> Dict[str, Any]:
        """
        Validar si un pozo tiene las curvas necesarias para un workflow.
        
        Returns:
            Dict con información de validación
        """
        workflow = self.create_workflow(workflow_type)
        required_curves = workflow.get_required_curves()
        available_curves = well_manager.curves
        
        missing_curves = [curve for curve in required_curves if curve not in available_curves]
        
        validation = {
            'is_valid': len(missing_curves) == 0,
            'required_curves': required_curves,
            'available_curves': available_curves,
            'missing_curves': missing_curves,
            'workflow_name': workflow.name,
            'can_proceed': len(missing_curves) == 0
        }
        
        return validation
    
    def get_workflow_recommendations(self, well_manager) -> List[Dict[str, Any]]:
        """
        Obtener recomendaciones de workflows basadas en las curvas disponibles.
        """
        recommendations = []
        available_curves = set(well_manager.curves)
        
        for workflow_type, workflow_class in self.available_workflows.items():
            workflow = workflow_class()
            required_curves = set(workflow.get_required_curves())
            
            # Calcular compatibilidad
            missing_curves = required_curves - available_curves
            compatibility = len(required_curves - missing_curves) / len(required_curves)
            
            recommendation = {
                'workflow_type': workflow_type,
                'workflow_name': workflow.name,
                'description': workflow.description,
                'compatibility': compatibility,
                'missing_curves': list(missing_curves),
                'can_execute': len(missing_curves) == 0,
                'priority': self._calculate_priority(workflow_type, compatibility)
            }
            
            recommendations.append(recommendation)
        
        # Ordenar por prioridad y compatibilidad
        recommendations.sort(key=lambda x: (x['priority'], x['compatibility']), reverse=True)
        
        return recommendations
    
    def _calculate_priority(self, workflow_type: str, compatibility: float) -> float:
        """Calcular prioridad de recomendación."""
        # Prioridades base por tipo
        priorities = {
            'basic_petrophysics': 1.0,
            'sandstone_analysis': 0.9,
            'carbonate_analysis': 0.9,
            'completion_optimization': 0.8
        }
        
        base_priority = priorities.get(workflow_type, 0.5)
        return base_priority * compatibility
    
    def export_workflow_results(self, 
                               workflow_results: Dict[str, Any],
                               output_path: Path,
                               format: str = 'json') -> None:
        """Exportar resultados de workflow."""
        
        if format == 'json':
            # Convertir numpy arrays a listas para serialización
            serializable_results = self._make_serializable(workflow_results)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        elif format == 'report':
            # Generar reporte en texto
            self._generate_text_report(workflow_results, output_path)
        
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def _make_serializable(self, obj):
        """Convertir objetos a formato serializable."""
        if hasattr(obj, 'tolist'):  # numpy array
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj
    
    def _generate_text_report(self, workflow_results: Dict[str, Any], output_path: Path):
        """Generar reporte en texto."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Reporte de Workflow - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            if self.current_workflow:
                f.write(f"Workflow: {self.current_workflow.name}\n")
                f.write(f"Descripción: {self.current_workflow.description}\n")
                f.write(f"Estado: {'Completado' if self.current_workflow.is_completed else 'En progreso'}\n\n")
                
                # Log de ejecución
                f.write("Log de Ejecución:\n")
                f.write("-" * 40 + "\n")
                for log_entry in self.current_workflow.execution_log:
                    f.write(f"• {log_entry}\n")
                f.write("\n")
            
            # Resumen de resultados
            f.write("Resumen de Resultados:\n")
            f.write("-" * 40 + "\n")
            for step_name, step_results in workflow_results.items():
                f.write(f"\n{step_name}:\n")
                if isinstance(step_results, dict):
                    for key, value in step_results.items():
                        if isinstance(value, dict) and 'statistics' in value:
                            stats = value['statistics']
                            f.write(f"  {key}: μ={stats.get('mean', 'N/A'):.3f}, σ={stats.get('std', 'N/A'):.3f}\n")
                        else:
                            f.write(f"  {key}: {type(value).__name__}\n")
    
    def get_execution_history(self) -> Dict[str, Any]:
        """Obtener historial de ejecuciones."""
        return self.executed_workflows
    
    def clear_history(self):
        """Limpiar historial de ejecuciones."""
        self.executed_workflows.clear()
        logger.info("Historial de workflows limpiado")
