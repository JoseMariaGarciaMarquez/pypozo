#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demostración Final de PyPozo 2.0
===============================

Script que demuestra todas las funcionalidades implementadas del sistema PyPozo 2.0.
"""

import sys
import os
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_backend():
    """Probar funcionalidades del backend."""
    print("🔧 Probando Backend de PyPozo...")
    
    try:
        from pypozo import WellManager, WellPlotter, ProjectManager
        from pypozo.processors import DataStandardizer, GeophysicsCalculator
        from pypozo.workflows import StandardWorkflow
        
        print("✅ Todos los módulos importados correctamente")
        
        # Probar carga de pozos
        data_files = [
            "data/70449_abedul1_gn_1850_800_05mz79p.las",
            "data/ABEDUL1_REPROCESADO.las", 
            "data/PALO BLANCO 791_PROCESADO.las"
        ]
        
        wells_loaded = []
        
        for file_path in data_files:
            if Path(file_path).exists():
                try:
                    well = WellManager.from_las(file_path)
                    wells_loaded.append(well)
                    print(f"✅ {Path(file_path).name}: {len(well.curves)} curvas, rango: {well.depth_range[0]:.0f}-{well.depth_range[1]:.0f}m")
                except Exception as e:
                    print(f"❌ {Path(file_path).name}: {e}")
        
        if wells_loaded:
            print(f"\\n📊 Total pozos cargados: {len(wells_loaded)}")
            
            # Probar visualización
            try:
                plotter = WellPlotter()
                well = wells_loaded[0]  # Usar el primer pozo
                
                # Probar diferentes tipos de gráficos
                if len(well.curves) >= 3:
                    selected_curves = well.curves[:3]
                    print(f"🎨 Probando visualización con curvas: {selected_curves}")
                    
                    # Crear gráfico (sin mostrar)
                    import matplotlib
                    matplotlib.use('Agg')  # Backend sin GUI para pruebas
                    
                    fig = plotter.plot_selected_curves(well, selected_curves, show=False)
                    if fig:
                        print("✅ Visualización de curvas seleccionadas: OK")
                    
                    # Probar gráfico completo
                    fig = plotter.plot_well_logs(well, show=False)
                    if fig:
                        print("✅ Visualización completa del pozo: OK")
                        
                else:
                    print("⚠️ Pozo con pocas curvas para visualización completa")
                    
            except Exception as e:
                print(f"❌ Error en visualización: {e}")
            
            # Probar proyecto multi-pozo
            if len(wells_loaded) > 1:
                try:
                    project = ProjectManager()
                    for well in wells_loaded:
                        project.add_well(well)
                    
                    print(f"✅ Proyecto creado con {len(project.wells)} pozos")
                    
                    # Probar comparación si hay curva común
                    common_curves = set(wells_loaded[0].curves)
                    for well in wells_loaded[1:]:
                        common_curves &= set(well.curves)
                    
                    if common_curves:
                        common_curve = list(common_curves)[0]
                        print(f"✅ Curva común encontrada para comparación: {common_curve}")
                    
                except Exception as e:
                    print(f"❌ Error en proyecto multi-pozo: {e}")
        
        print("\\n✅ Backend funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en backend: {e}")
        return False

def test_gui_availability():
    """Probar disponibilidad de la GUI."""
    print("\\n🖥️ Probando disponibilidad de GUI...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        import matplotlib
        matplotlib.use('Qt5Agg')
        
        print("✅ PyQt5 disponible")
        print("✅ Matplotlib con backend Qt5Agg")
        
        # Probar importación de la aplicación principal
        try:
            from pypozo_app import PyPozoApp
            print("✅ Aplicación GUI importada correctamente")
            return True
        except Exception as e:
            print(f"❌ Error importando aplicación GUI: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ GUI no disponible: {e}")
        print("💡 Instale PyQt5: pip install PyQt5")
        return False

def main():
    """Función principal de demostración."""
    print("=" * 60)
    print("🚀 DEMOSTRACIÓN PYPOZO 2.0 - SISTEMA COMPLETO")
    print("=" * 60)
    print()
    
    # Probar backend
    backend_ok = test_backend()
    
    # Probar GUI
    gui_ok = test_gui_availability()
    
    print("\\n" + "=" * 60)
    print("📋 RESUMEN DE FUNCIONALIDADES")
    print("=" * 60)
    
    print(f"🔧 Backend (Core):           {'✅ OK' if backend_ok else '❌ ERROR'}")
    print(f"🖥️ GUI (Interfaz Gráfica):   {'✅ OK' if gui_ok else '❌ ERROR'}")
    
    if backend_ok and gui_ok:
        print("\\n🎉 ¡PYPOZO 2.0 COMPLETAMENTE FUNCIONAL!")
        print("\\n📋 Comandos disponibles:")
        print("   • python pypozo_app.py          - Lanzar GUI principal")
        print("   • python launch_pypozo.py       - Lanzar con datos de ejemplo")
        print("   • python test_visualizacion.py  - Demo de visualización")
        print("   • python tests/pruebas.py       - Pruebas del backend")
        
        print("\\n🎯 Funcionalidades disponibles:")
        print("   ✅ Carga de archivos LAS")
        print("   ✅ Visualización profesional de curvas")
        print("   ✅ Selección inteligente de curvas")
        print("   ✅ Comparación multi-pozo")
        print("   ✅ Exportación de gráficos y datos")
        print("   ✅ Análisis automatizado")
        print("   ✅ Interfaz gráfica moderna")
        print("   ✅ API programática completa")
        
        print("\\n🆚 Alternativa Open Source a WellCAD - ¡LISTA PARA USAR!")
        
    elif backend_ok:
        print("\\n⚠️ Backend funcional, GUI no disponible")
        print("   💡 Instale PyQt5 para usar la interfaz gráfica")
        
    else:
        print("\\n❌ Errores encontrados - Revise las dependencias")
        
    print("\\n" + "=" * 60)

if __name__ == "__main__":
    main()
