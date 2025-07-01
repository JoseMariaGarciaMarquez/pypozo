#!/usr/bin/env python3
"""
Test de fusión completa con GUI para verificar el flujo completo.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from pypozo.core.well import WellManager

def test_complete_fusion_workflow():
    """Test completo del flujo de fusión como se usa en la GUI"""
    print("=== TEST DE FLUJO COMPLETO DE FUSIÓN ===")
    
    # Archivos de Palo Blanco (otro conjunto de datos)
    test_files = [
        "data/PALO BLANCO 791_PROCESADO.las",
        "data/PALOBLANCO791_REPROCESADO.las"
    ]
    
    # Verificar que los archivos existen
    existing_files = []
    for file_path in test_files:
        if Path(file_path).exists():
            existing_files.append(file_path)
            print(f"✅ Archivo encontrado: {file_path}")
        else:
            print(f"⚠️ Archivo no encontrado: {file_path}")
    
    if len(existing_files) < 2:
        print("❌ Se necesitan al menos 2 archivos para fusión")
        return False
    
    try:
        print("\n1. Cargando pozos para fusión...")
        pozos_para_fusion = []
        
        for file_path in existing_files:
            try:
                well_manager = WellManager.from_las(file_path)
                print(f"   📊 {well_manager.name}: {len(well_manager.curves)} curvas, "
                      f"profundidad {well_manager.depth_range[0]:.1f}-{well_manager.depth_range[1]:.1f}m")
                pozos_para_fusion.append(well_manager)
            except Exception as e:
                print(f"   ❌ Error cargando {file_path}: {str(e)}")
                continue
        
        if len(pozos_para_fusion) < 2:
            print("❌ No se pudieron cargar suficientes pozos para fusión")
            return False
        
        print(f"\n2. Fusionando {len(pozos_para_fusion)} pozos...")
        
        # Obtener el nombre común (normalmente sería el mismo en la GUI)
        well_name = pozos_para_fusion[0].name
        print(f"   🎯 Nombre del pozo fusionado: {well_name}")
        
        # Realizar la fusión
        pozo_fusionado = WellManager.merge_wells(pozos_para_fusion, well_name)
        
        if pozo_fusionado is None:
            print("❌ Error en la fusión")
            return False
        
        print("   ✅ Fusión completada")
        print(f"   📊 Curvas fusionadas: {len(pozo_fusionado.curves)}")
        print(f"   🎯 Rango fusionado: {pozo_fusionado.depth_range}")
        
        # Mostrar estadísticas detalladas
        print("\n3. Estadísticas del pozo fusionado:")
        for curve_name in pozo_fusionado.curves:
            curve_data = pozo_fusionado.get_curve_data(curve_name)
            if curve_data is not None:
                valid_points = (~curve_data.isna()).sum()
                print(f"   📈 {curve_name}: {valid_points} puntos válidos")
        
        print("\n4. Guardando pozo fusionado...")
        output_file = "test_fusion_gui_output.las"
        
        success = pozo_fusionado.save_merged_well(output_file)
        
        if success:
            output_path = Path(output_file)
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"   ✅ Archivo guardado: {output_file}")
                print(f"   📁 Tamaño: {file_size:,} bytes")
                
                if file_size > 0:
                    print("   ✅ Archivo no está vacío")
                    
                    # Leer las primeras líneas para verificar formato
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            lines = [f.readline().strip() for _ in range(15)]
                        
                        print("   📄 Contenido inicial:")
                        for i, line in enumerate(lines, 1):
                            if line:
                                print(f"      {i:2d}: {line[:60]}...")
                    except Exception as e:
                        print(f"   ⚠️ Error leyendo archivo: {e}")
                else:
                    print("   ❌ El archivo está vacío")
                    return False
            else:
                print("   ❌ El archivo no se creó")
                return False
        else:
            print("   ❌ Error guardando el archivo")
            return False
        
        print("\n✅ Test de flujo completo exitoso")
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_fusion_workflow()
    sys.exit(0 if success else 1)
