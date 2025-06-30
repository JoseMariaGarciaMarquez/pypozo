#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para PyPozo 2.0 - Visualización del pozo Abedul
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar PyPozo
from pypozo import WellManager, WellPlotter

def main():
    print("🔧 PyPozo 2.0 - Prueba de Visualización")
    print("=" * 50)
    
    # Ruta al archivo LAS
    las_file = Path("data/70449_abedul1_gn_1850_800_05mz79p.las")
    
    if not las_file.exists():
        print(f"❌ Archivo no encontrado: {las_file}")
        return
    
    try:
        # 1. Cargar el pozo
        print(f"📁 Cargando pozo: {las_file.name}")
        well = WellManager.from_las(las_file)
        
        # 2. Información básica
        print(f"✅ Pozo: {well.name}")
        print(f"📊 Curvas: {well.curves}")
        print(f"📏 Profundidad: {well.depth_range[0]:.1f} - {well.depth_range[1]:.1f} m")
        
        # 3. Datos de GR
        print(f"\n📈 Analizando curva GR...")
        gr_data = well.get_curve_data("GR")
        
        if gr_data is not None:
            print(f"  ✅ Datos de GR obtenidos:")
            print(f"    • Puntos: {len(gr_data)}")
            print(f"    • Rango: {gr_data.min():.2f} - {gr_data.max():.2f}")
            print(f"    • Promedio: {gr_data.mean():.2f}")
            
            # 4. Crear visualización
            print(f"\n🎨 Creando visualización...")
            plotter = WellPlotter()
            
            # Crear directorio de salida
            output_dir = Path("output_workflow_simple")
            output_dir.mkdir(exist_ok=True)
            
            result = plotter.plot_well_logs(
                well, 
                curves=["GR"],
                title="Registro de Rayos Gamma - Pozo Abedul",
                save_path=output_dir / "abedul_GR.png"
            )
            
            if result:
                print(f"✅ Visualización guardada en: {result}")
            else:
                print("⚠️ Visualización creada pero no guardada")
                
        else:
            print("❌ No se pudieron obtener datos de GR")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
