#!/usr/bin/env python3
"""
Script de prueba rápida para verificar que PyPozo App funciona.
"""

import sys
import os

def test_imports():
    """Probar todos los imports necesarios."""
    print("🔍 Probando imports...")
    
    try:
        # Imports básicos
        import sys
        import os
        from pathlib import Path
        import logging
        import numpy as np
        print("✅ Imports básicos OK")
        
        # PyQt5
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 OK")
        
        # Matplotlib
        import matplotlib
        matplotlib.use('Qt5Agg')
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        print("✅ Matplotlib OK")
        
        # PyPozo modules
        from src.pypozo.core.well import WellManager, WellDataFrame
        from src.pypozo.visualization.plotter import WellPlotter
        from src.pypozo.petrophysics import VclCalculator, PorosityCalculator
        from src.pypozo.petrophysics import WaterSaturationCalculator, PermeabilityCalculator, LithologyAnalyzer
        print("✅ PyPozo modules OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False

def test_app_init():
    """Probar inicialización de la aplicación."""
    print("\n🚀 Probando inicialización de la aplicación...")
    
    try:
        # Import the app and required PyQt5
        from PyQt5.QtWidgets import QApplication
        from pypozo_app import PyPozoApp, PYQT5_AVAILABLE
        
        if not PYQT5_AVAILABLE:
            print("❌ PyQt5 no disponible")
            return False
        
        # Create QApplication
        app = QApplication([])
        
        # Create main window
        window = PyPozoApp()
        print("✅ Ventana principal creada")
        
        # Basic checks
        assert hasattr(window, 'wells'), "Debe tener atributo wells"
        assert hasattr(window, 'current_well'), "Debe tener atributo current_well"
        assert hasattr(window, 'figure'), "Debe tener atributo figure"
        print("✅ Atributos básicos presentes")
        
        # Check UI components
        assert hasattr(window, 'wells_tree'), "Debe tener wells_tree"
        assert hasattr(window, 'curves_list'), "Debe tener curves_list"
        assert hasattr(window, 'petro_tabs'), "Debe tener petro_tabs"
        print("✅ Componentes UI presentes")
        
        print("✅ Inicialización exitosa!")
        
        # Don't show the window in test mode
        # window.show()
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de prueba."""
    print("🧪 PRUEBA RÁPIDA DE PYPOZO APP")
    print("=" * 40)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ FALLO: Problemas con imports")
        return False
    
    # Test 2: App initialization
    if not test_app_init():
        print("\n❌ FALLO: Problemas inicializando aplicación")
        return False
    
    print("\n🎉 TODAS LAS PRUEBAS EXITOSAS!")
    print("La aplicación PyPozo está lista para usar.")
    print("\nPara ejecutar la GUI:")
    print("python pypozo_app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
