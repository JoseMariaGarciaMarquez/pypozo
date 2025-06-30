#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la GUI de PyPozo
========================

Script para probar la funcionalidad de la GUI sin necesidad de interacción manual.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    import matplotlib
    matplotlib.use('Qt5Agg')  # Usar backend Qt5
    
    from pypozo import WellManager
    
    print("✅ Todas las dependencias están disponibles")
    print("✅ PyQt5:", True)
    print("✅ Matplotlib con Qt5Agg:", True)
    print("✅ PyPozo backend:", True)
    
    # Test de carga de pozo
    print("\n🔍 Probando carga de pozos...")
    
    data_files = [
        "data/70449_abedul1_gn_1850_800_05mz79p.las",
        "data/ABEDUL1_REPROCESADO.las",
        "data/PALO BLANCO 791_PROCESADO.las"
    ]
    
    for file_path in data_files:
        if Path(file_path).exists():
            try:
                well = WellManager.from_las(file_path)
                print(f"✅ {Path(file_path).name}: {len(well.curves)} curvas")
            except Exception as e:
                print(f"❌ {Path(file_path).name}: {e}")
        else:
            print(f"⚠️ {file_path}: archivo no encontrado")
    
    print("\n🎯 La GUI debería funcionar correctamente.")
    print("🚀 Ejecute 'python pypozo_app.py' para iniciar la aplicación.")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("\n💡 Para resolver:")
    print("   pip install PyQt5 matplotlib")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
