"""
Test de entrada rápida para PyPozo
==================================

Test básico que verifica que la instalación y configuración están correctas.
Este test debe ejecutarse primero para validar el entorno.
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test versión de Python."""
    assert sys.version_info >= (3, 7), f"Python 3.7+ requerido, encontrado: {sys.version}"
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def test_basic_imports():
    """Test imports básicos."""
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError:
        assert False, "NumPy no disponible"
    
    try:
        import pandas as pd
        print(f"✓ Pandas {pd.__version__}")
    except ImportError:
        assert False, "Pandas no disponible"
    
    try:
        import matplotlib
        print(f"✓ Matplotlib {matplotlib.__version__}")
    except ImportError:
        assert False, "Matplotlib no disponible"

def test_project_structure():
    """Test estructura del proyecto."""
    project_root = Path(__file__).parent.parent
    
    # Verificar directorios principales
    assert (project_root / "src").exists(), "Directorio src no encontrado"
    assert (project_root / "data").exists(), "Directorio data no encontrado"
    assert (project_root / "tests").exists(), "Directorio tests no encontrado"
    
    print("✓ Estructura del proyecto correcta")

def test_pypozo_imports():
    """Test imports de PyPozo."""
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Test import del módulo principal
        import pypozo
        print("✓ Módulo pypozo importado")
    except ImportError as e:
        print(f"⚠️ Import directo falló: {e}")
        
        # Intentar imports individuales
        try:
            from pypozo.core import well
            print("✓ Módulo core.well importado")
        except ImportError:
            try:
                sys.path.insert(0, str(project_root))
                import pypozo_app
                print("✓ pypozo_app importado")
            except ImportError as app_error:
                print(f"⚠️ Imports de PyPozo fallaron: {app_error}")

def test_data_files():
    """Test archivos de datos disponibles."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    las_files = list(data_dir.glob("*.las"))
    print(f"📁 Archivos LAS encontrados: {len(las_files)}")
    
    if las_files:
        print("✓ Datos de prueba disponibles")
        for i, las_file in enumerate(las_files[:3]):  # Mostrar primeros 3
            print(f"  - {las_file.name}")
    else:
        print("⚠️ No hay archivos LAS para tests")

def test_gui_dependencies():
    """Test dependencias de GUI."""
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 disponible")
    except ImportError:
        print("⚠️ PyQt5 no disponible - tests de GUI se saltarán")

def test_optional_dependencies():
    """Test dependencias opcionales."""
    optional_packages = {
        'welly': 'Manejo de archivos LAS',
        'lasio': 'Lectura de archivos LAS',
        'psutil': 'Monitoreo de sistema',
        'scipy': 'Funciones científicas adicionales'
    }
    
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"✓ {package} disponible - {description}")
        except ImportError:
            print(f"⚠️ {package} no disponible - {description}")

if __name__ == "__main__":
    print("🧪 VERIFICACIÓN RÁPIDA DE PYPOZO")
    print("=" * 40)
    
    try:
        test_python_version()
        test_basic_imports() 
        test_project_structure()
        test_pypozo_imports()
        test_data_files()
        test_gui_dependencies()
        test_optional_dependencies()
        
        print("\n🎉 VERIFICACIÓN COMPLETADA")
        print("✅ El entorno está listo para ejecutar tests")
        
    except Exception as e:
        print(f"\n❌ ERROR EN VERIFICACIÓN: {e}")
        sys.exit(1)
