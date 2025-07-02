"""
PyPozo 2.0 - Módulo de Cálculos Petrofísicos
============================================

Módulo principal para cálculos petrofísicos estándar de la industria.
Incluye:
- Volumen de Arcilla (VCL)
- Porosidad Efectiva (PHIE) 
- Saturación de Agua (SW)
- Permeabilidad

Autor: JoseMariaGarciaMarquez
Versión: 2.0.0
"""

from .vcl import VclCalculator
from .porosity import PorosityCalculator
from .base import PetrophysicsCalculator

__version__ = "2.0.0"
__all__ = [
    'VclCalculator',
    'PorosityCalculator',
    'PetrophysicsCalculator'
]
