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

# Importaciones principales del núcleo
from .core.well import WellManager
from .core.project import ProjectManager
from .workflows.standard import StandardWorkflow

# Importaciones de procesamiento
from .processors.standardizer import DataStandardizer
from .processors.calculator import GeophysicsCalculator

# Importaciones de visualización
from .visualization.plotter import WellPlotter

# Importaciones de integración (opcional)
try:
    from .integration.gis import GISExporter
    from .integration.formats import FormatExporter
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

# Importaciones de GUI (opcional)
try:
    from .gui.main_window import PyPozoMainWindow
    from .gui.well_viewer import WellViewerWidget
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# API pública
__all__ = [
    # Core
    "WellManager",
    "ProjectManager", 
    "StandardWorkflow",
    
    # Procesamiento
    "DataStandardizer",
    "GeophysicsCalculator",
    
    # Visualización
    "WellPlotter",
    
    # Integración (si está disponible)
    "GISExporter" if INTEGRATION_AVAILABLE else None,
    "FormatExporter" if INTEGRATION_AVAILABLE else None,
    
    # GUI (si está disponible)
    "PyPozoMainWindow" if GUI_AVAILABLE else None,
    "WellViewerWidget" if GUI_AVAILABLE else None,
]

# Remover None de la lista
__all__ = [item for item in __all__ if item is not None]

def get_version():
    """Obtener versión de PyPozo."""
    return __version__

def check_dependencies():
    """Verificar dependencias principales."""
    dependencies = {
        'welly': False,
        'lasio': False,
        'pandas': False,
        'matplotlib': False,
        'numpy': False,
        'scipy': False,
        'pyqt5': False,
        'geopandas': False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies

def show_info():
    """Mostrar información de PyPozo 2.0."""
    print(f"PyPozo {__version__}")
    print(f"Autor: {__author__}")
    print(f"Licencia: {__license__}")
    print(f"GUI disponible: {'Sí' if GUI_AVAILABLE else 'No (instalar PyQt5)'}")
    
    deps = check_dependencies()
    print("\nDependencias:")
    for dep, available in deps.items():
        status = "✅" if available else "❌"
        print(f"  {status} {dep}")
