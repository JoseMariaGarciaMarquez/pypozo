"""
Base Classes for Workflows
=========================

Clases base para el sistema de workflows petrofísicos automatizados.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class WorkflowStep:
    """
    Representa un paso individual en un workflow.
    """
    
    def __init__(self, 
                 name: str,
                 description: str,
                 required_curves: List[str],
                 output_curves: List[str],
                 parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.required_curves = required_curves
        self.output_curves = output_curves
        self.parameters = parameters or {}
        self.is_executed = False
        self.execution_time = None
        self.errors = []

class BaseWorkflow(ABC):
    """
    Clase base para todos los workflows.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.current_step = 0
        self.is_completed = False
        self.execution_log = []
        self.results = {}
        
    @abstractmethod
    def setup_steps(self) -> None:
        """Configurar los pasos del workflow."""
        pass
    
    @abstractmethod
    def validate_well(self, well_manager) -> bool:
        """Validar que el pozo tiene las curvas necesarias."""
        pass
    
    def add_step(self, step: WorkflowStep) -> None:
        """Agregar un paso al workflow."""
        self.steps.append(step)
    
    def get_required_curves(self) -> List[str]:
        """Obtener todas las curvas requeridas por el workflow."""
        required = set()
        for step in self.steps:
            required.update(step.required_curves)
        return list(required)
    
    def get_output_curves(self) -> List[str]:
        """Obtener todas las curvas que genera el workflow."""
        output = set()
        for step in self.steps:
            output.update(step.output_curves)
        return list(output)
    
    def execute(self, well_manager, progress_callback=None) -> Dict[str, Any]:
        """
        Ejecutar el workflow completo.
        
        Args:
            well_manager: Gestor del pozo
            progress_callback: Función callback para reportar progreso
            
        Returns:
            Dict con resultados del workflow
        """
        self.execution_log.clear()
        self.results.clear()
        
        # Validar pozo
        if not self.validate_well(well_manager):
            raise ValueError(f"El pozo no tiene las curvas requeridas: {self.get_required_curves()}")
        
        try:
            total_steps = len(self.steps)
            
            for i, step in enumerate(self.steps):
                self.current_step = i
                
                logger.info(f"Ejecutando paso {i+1}/{total_steps}: {step.name}")
                self.execution_log.append(f"Iniciando: {step.name}")
                
                # Reportar progreso
                if progress_callback:
                    progress_callback(int((i / total_steps) * 100), step.name)
                
                # Ejecutar paso específico
                step_result = self._execute_step(step, well_manager)
                step.is_executed = True
                
                # Guardar resultados
                self.results[step.name] = step_result
                self.execution_log.append(f"Completado: {step.name}")
                
            # Workflow completado
            self.is_completed = True
            if progress_callback:
                progress_callback(100, "Workflow completado")
                
            self.execution_log.append("✅ Workflow completado exitosamente")
            
            return self.results
            
        except Exception as e:
            error_msg = f"Error en paso {self.current_step + 1}: {str(e)}"
            self.execution_log.append(f"❌ {error_msg}")
            logger.error(error_msg)
            raise
    
    @abstractmethod
    def _execute_step(self, step: WorkflowStep, well_manager) -> Dict[str, Any]:
        """Ejecutar un paso específico del workflow."""
        pass
    
    def get_progress(self) -> Dict[str, Any]:
        """Obtener información del progreso actual."""
        total_steps = len(self.steps)
        completed_steps = sum(1 for step in self.steps if step.is_executed)
        
        return {
            'current_step': self.current_step + 1,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'progress_percent': (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            'is_completed': self.is_completed,
            'current_step_name': self.steps[self.current_step].name if self.current_step < total_steps else "Completado"
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen del workflow."""
        return {
            'name': self.name,
            'description': self.description,
            'total_steps': len(self.steps),
            'required_curves': self.get_required_curves(),
            'output_curves': self.get_output_curves(),
            'is_completed': self.is_completed,
            'execution_log': self.execution_log,
            'results_summary': {name: type(result).__name__ for name, result in self.results.items()}
        }
