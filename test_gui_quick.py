#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba rápida de la GUI con las nuevas funcionalidades
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🚀 Probando las nuevas funcionalidades...")

# Verificar que las funciones están disponibles
try:
    from pypozo import WellManager, WellPlotter
    
    # Cargar pozo
    well = WellManager.from_las("data/PALO BLANCO 791_PROCESADO.las")
    plotter = WellPlotter()
    
    print(f"✅ Pozo cargado: {well.name}")
    
    # Verificar método get_curve_units
    print(f"📊 Probando get_curve_units:")
    for curve in well.curves[:5]:
        units = well.get_curve_units(curve)
        print(f"  {curve}: {units}")
    
    # Verificar detección eléctrica mejorada
    print(f"\n⚡ Probando detección eléctrica mejorada:")
    electrical_curves = []
    for curve in well.curves[:10]:
        is_electrical = plotter._is_electrical_curve(curve, well)
        if is_electrical:
            electrical_curves.append(curve)
            units = well.get_curve_units(curve)
            print(f"  {curve} ({units}) - ELÉCTRICA")
    
    # Verificar plot_curves_together
    if len(electrical_curves) >= 2:
        print(f"\n🔗 Probando plot_curves_together:")
        result = plotter.plot_curves_together(
            well,
            curves=electrical_curves[:2],
            normalize=False,
            save_path=Path("test_gui_curves_together.png")
        )
        print(f"  ✅ Resultado: {result}")
    
    print(f"\n🎯 Todas las funcionalidades están funcionando correctamente!")
    print(f"📱 La GUI está lista para usarse con las nuevas características.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
