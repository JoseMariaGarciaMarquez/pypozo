"""
PyPozo 2.0 - Sistema Profesional de Análisis de Pozos
=====================================================

PyPozo 2.0 es un sistema completo para el procesamiento, análisis y visualización
de registros geofísicos de pozos, diseñado desde cero con:

- Arquitectura modular y extensible
- Interfaz gráfica profesional (PyQt5)
- Integración robusta con Welly
- Workflows automatizados
- Exportación a múltiples formatos
- Integración GIS

Autor: José María García Márquez
Fecha: Junio 2025
Versión: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "José María García Márquez"
__license__ = "MIT"

# Importaciones principales
try:
    from .core.well import WellManager
    from .core.project import ProjectManager
    from .visualization.plotter import WellPlotter
    
    __all__ = [
        "WellManager",
        "ProjectManager",
        "WellPlotter"
    ]
except ImportError as e:
    # Permite importar el paquete incluso si algunos módulos no están disponibles
    __all__ = []
    print(f"Warning: Some modules could not be imported: {e}")

def get_version():
    """Obtener versión de PyPozo."""
    return __version__