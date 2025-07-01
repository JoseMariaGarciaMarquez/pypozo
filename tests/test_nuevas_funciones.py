#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de las nuevas funcionalidades de PyPozo 2.0
===============================================

Prueba específica de:
1. plot_curves_together - Graficar curvas juntas
2. Detección automática de curvas eléctricas por unidades
3. Aplicación automática de escala logarítmica
4. Visualización de unidades en las etiquetas
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pypozo import WellManager, WellPlotter

def main():
    print("🚀 PyPozo 2.0 - Test de Nuevas Funcionalidades")
    print("=" * 60)
    
    # Cargar pozo con curvas eléctricas
    pozo_file = "data/PALO BLANCO 791_PROCESADO.las"
    
    try:
        well = WellManager.from_las(pozo_file)
        plotter = WellPlotter()
        
        print(f"✅ Pozo cargado: {well.name}")
        print(f"📊 Total de curvas: {len(well.curves)}")
        
        # 1. Mostrar información de unidades y detección eléctrica
        print(f"\n📋 Análisis de Unidades y Detección Eléctrica:")
        print("-" * 50)
        
        electrical_curves = []
        for curve in well.curves[:15]:  # Primeras 15 curvas
            units = well.get_curve_units(curve)
            is_electrical = plotter._is_electrical_curve(curve, well)
            
            status = "⚡ ELÉCTRICA" if is_electrical else ""
            print(f"  {curve:12s} | {units:15s} | {status}")
            
            if is_electrical:
                electrical_curves.append(curve)
        
        print(f"\n⚡ Curvas eléctricas detectadas: {electrical_curves}")
        
        # 2. Probar plot_curves_together sin normalizar (con unidades originales)
        if len(electrical_curves) >= 2:
            print(f"\n🔗 Test 1: Graficando curvas eléctricas juntas (valores originales)")
            result = plotter.plot_curves_together(
                well,
                curves=electrical_curves[:3],  # Máximo 3
                title="Curvas Eléctricas - Valores Originales con Escala Log",
                normalize=False,
                use_log_scale=True,
                save_path=Path("test_electricas_originales.png")
            )
            if result:
                print(f"✅ Guardado: {result}")
            
            # 3. Probar plot_curves_together normalizado
            print(f"\n🔗 Test 2: Graficando curvas eléctricas juntas (normalizadas)")
            result = plotter.plot_curves_together(
                well,
                curves=electrical_curves[:3],
                title="Curvas Eléctricas - Normalizadas",
                normalize=True,
                use_log_scale=False,
                save_path=Path("test_electricas_normalizadas.png")
            )
            if result:
                print(f"✅ Guardado: {result}")
        
        # 4. Probar plot_well_logs_enhanced (detección automática)
        if electrical_curves:
            print(f"\n📊 Test 3: plot_well_logs_enhanced (detección automática de log)")
            result = plotter.plot_well_logs_enhanced(
                well,
                curves=electrical_curves[:4],  # Máximo 4 subplots
                title="Registros Eléctricos - Escala Log Automática",
                save_path=Path("test_enhanced_auto.png")
            )
            if result:
                print(f"✅ Guardado: {result}")
        
        # 5. Probar con curvas no eléctricas para contrastar
        non_electrical = ["GR", "SP", "CAL", "DPHI"]
        available_non_elec = [c for c in non_electrical if c in well.curves]
        
        if available_non_elec:
            print(f"\n📊 Test 4: Curvas no eléctricas (sin escala log)")
            result = plotter.plot_curves_together(
                well,
                curves=available_non_elec,
                title="Curvas No Eléctricas - Escala Lineal",
                normalize=False,
                save_path=Path("test_no_electricas.png")
            )
            if result:
                print(f"✅ Guardado: {result}")
        
        print(f"\n🎯 Test Completado")
        print("Las imágenes muestran:")
        print("• Curvas eléctricas con escala logarítmica automática")
        print("• Unidades en las etiquetas del eje X")
        print("• Opción de normalización para comparación visual")
        print("• Detección automática basada en unidades y nombres")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
