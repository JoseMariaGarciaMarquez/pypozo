"""
PyPozo 2.0 - Módulo de Cálculos Petrofísicos
============================================

Módulo principal para cálculos petrofísicos estándar de la industria.
Incluye:
- Volumen de Arcilla (VCL)
- Porosidad Efectiva (PHIE) 
- Saturación de Agua (SW)
- Permeabilidad
- Análisis Litológico

Autor: JoseMariaGarciaMarquez
Versión: 2.0.0
"""

from .vcl import VclCalculator
from .porosity import PorosityCalculator
from .water_saturation import WaterSaturationCalculator
from .permeability import PermeabilityCalculator
from .lithology import LithologyAnalyzer
from .base import PetrophysicsCalculator

__version__ = "2.0.0"
__all__ = [
    'VclCalculator',
    'PorosityCalculator',
    'WaterSaturationCalculator',
    'PermeabilityCalculator',
    'LithologyAnalyzer',
    'PetrophysicsCalculator'
]
