"""
PyPozo 2.0 - Workflows System
============================

Sistema de workflows automatizados para análisis petrofísico estándar.
Incluye templates predefinidos para diferentes tipos de análisis.

Autor: JoseMariaGarciaMarquez
Versión: 2.0.0
"""

from .templates import (
    BasicPetrophysicsWorkflow,
    SandstoneAnalysisWorkflow,
    CarbonateAnalysisWorkflow,
    CompletionOptimizationWorkflow
)

from .manager import WorkflowManager

__version__ = "2.0.0"
__all__ = [
    'BasicPetrophysicsWorkflow',
    'SandstoneAnalysisWorkflow', 
    'CarbonateAnalysisWorkflow',
    'CompletionOptimizationWorkflow',
    'WorkflowManager'
]
