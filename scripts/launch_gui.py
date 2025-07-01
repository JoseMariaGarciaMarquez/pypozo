#!/usr/bin/env python3
"""
Lanzador de PyPozo 2.0 GUI
==========================

Script para iniciar la interfaz gráfica de PyPozo 2.0.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from pypozo.gui.main_window import main
    print("🚀 Iniciando PyPozo 2.0 GUI...")
    main()
except ImportError as e:
    print(f"❌ Error: {e}")
    print("💡 Para usar la GUI, instale PyQt5:")
    print("   pip install PyQt5")
    print("\n📊 Ejecutando versión de consola...")
    
    # Fallback a versión de consola
    exec(open("test_visualizacion.py", "r", encoding="utf-8").read())
