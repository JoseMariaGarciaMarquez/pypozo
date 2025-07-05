"""
PyPozo Premium DLC - Funciones Experimentales
=============================================

Este módulo contiene funcionalidades avanzadas disponibles exclusivamente 
para suscriptores de Patreon nivel 3 ($15/mes).

Funciones incluidas:
- Completado inteligente de registros con IA
- Análisis petrofísico avanzado
- Redes neuronales para clasificación litológica
- Predicción de propiedades faltantes

Para obtener acceso: https://www.patreon.com/pypozo

Autor: José María García Márquez
Versión: 1.0.0 (Premium)
"""

__version__ = "1.0.0"
__author__ = "José María García Márquez"
__license__ = "Patreon Exclusive"

# Importar módulos DLC
from . import neural_completion
from . import advanced_lithology
from . import ai_interpreter

__all__ = ['neural_completion', 'advanced_lithology', 'ai_interpreter']
