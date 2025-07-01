#!/usr/bin/env python3
"""
Test de diagnóstico para el problema de guardado de archivos fusionados vacíos.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from pypozo.core.well import WellManager

def test_fusion_debugging():
    """Test para diagnosticar el problema de fusión y guardado"""
    print("=== TEST DE DEBUGGING DE FUSIÓN ===")
    
    # Archivos de prueba existentes
    test_files = [
        "data/70449_abedul1_gn_1850_800_05mz79p.las",
        "data/ABEDUL1_REPROCESADO.las"
    ]
    
    # Verificar que los archivos existen
    for file_path in test_files:
        if not Path(file_path).exists():
            print(f"❌ Archivo no encontrado: {file_path}")
            return False
    
    try:
        # Cargar pozos usando from_las
        print("\n1. Cargando pozos...")
        pozos_cargados = []
        for file_path in test_files:
            print(f"   Cargando: {file_path}")
            try:
                well_manager = WellManager.from_las(file_path)
                print(f"   ✅ Cargado exitosamente")
                # Inspeccionar el pozo cargado
                print(f"      - Nombre: {well_manager.name}")
                print(f"      - Curvas: {len(well_manager.curves)} ({well_manager.curves[:5]}...)")
                depth_range = well_manager.depth_range
                print(f"      - Profundidad: {depth_range[0]:.1f} - {depth_range[1]:.1f}m")
                
                # Guardar referencia del WellManager completo
                pozos_cargados.append(well_manager)
            except Exception as e:
                print(f"   ❌ Error cargando {file_path}: {str(e)}")
                return False
        
        print(f"\n2. Total pozos cargados: {len(pozos_cargados)}")
        
        # Fusionar pozos usando el método de clase
        print("\n3. Iniciando fusión...")
        
        # Intentar fusión
        fusion_manager = WellManager.merge_wells(pozos_cargados, "POZO_FUSION_DEBUG")
        
        if fusion_manager:
            print("   ✅ Fusión exitosa")
            
            # Inspeccionar pozo fusionado
            print(f"   - Nombre fusionado: {fusion_manager.name}")
            print(f"   - Curvas fusionadas: {len(fusion_manager.curves)} ({fusion_manager.curves[:10]}...)")
            depth_range = fusion_manager.depth_range
            print(f"   - Profundidad fusionada: {depth_range[0]:.1f} - {depth_range[1]:.1f}m")
            
            # Verificar que tiene datos usando métodos públicos
            curves_list = fusion_manager.curves
            if curves_list:
                print(f"   - Datos disponibles: {len(curves_list)} curvas")
                
                # Mostrar algunas curvas 
                for curve_name in curves_list[:3]:
                    try:
                        curve_data = fusion_manager.get_curve_data(curve_name)
                        if curve_data is not None and hasattr(curve_data, '__len__'):
                            print(f"     * {curve_name}: {len(curve_data)} puntos")
                        else:
                            print(f"     * {curve_name}: datos disponibles")
                    except:
                        print(f"     * {curve_name}: no se pudo acceder a los datos")
            else:
                print("   ❌ No hay curvas en el pozo fusionado!")
                return False
            
            # Intentar guardar
            output_path = "test_fusion_debug_output.las"
            print(f"\n4. Guardando pozo fusionado en: {output_path}")
            
            if fusion_manager.save_merged_well(output_path):
                print("   ✅ Guardado exitoso")
                
                # Verificar el archivo guardado
                output_file = Path(output_path)
                if output_file.exists():
                    file_size = output_file.stat().st_size
                    print(f"   - Tamaño del archivo: {file_size} bytes")
                    
                    if file_size > 0:
                        print("   ✅ Archivo no está vacío")
                        
                        # Leer las primeras líneas del archivo para verificar contenido
                        with open(output_path, 'r') as f:
                            lines = f.readlines()[:10]
                            print(f"   - Primeras líneas del archivo:")
                            for i, line in enumerate(lines, 1):
                                print(f"     {i:2d}: {line.strip()}")
                    else:
                        print("   ❌ El archivo está vacío!")
                        return False
                else:
                    print("   ❌ El archivo no se creó!")
                    return False
            else:
                print("   ❌ Error guardando pozo fusionado")
                return False
        else:
            print("   ❌ Error en fusión")
            return False
        
        print("\n✅ Test de debugging completado exitosamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en test de debugging: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fusion_debugging()
    sys.exit(0 if success else 1)
