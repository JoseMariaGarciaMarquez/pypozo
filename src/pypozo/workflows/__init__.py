"""
Workflows de PyPozo 2.0
=======================

Sistema completo de workflows automatizados para análisis petrofísico.
Incluye templates predefinidos y gestor de workflows.
"""

from .standard import StandardWorkflow
from .base import BaseWorkflow, WorkflowStep
from .templates import (
    BasicPetrophysicsWorkflow,
    SandstoneAnalysisWorkflow,
    CarbonateAnalysisWorkflow,
    CompletionOptimizationWorkflow
)
from .manager import WorkflowManager

__version__ = "2.0.0"
__all__ = [
    'StandardWorkflow',
    'BaseWorkflow', 
    'WorkflowStep',
    'BasicPetrophysicsWorkflow',
    'SandstoneAnalysisWorkflow',
    'CarbonateAnalysisWorkflow', 
    'CompletionOptimizationWorkflow',
    'WorkflowManager'
]
