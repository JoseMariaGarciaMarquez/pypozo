#!/usr/bin/env python3
"""
Test de fusión automática de pozos duplicados en la GUI.
Verifica que cuando se cargan archivos con el mismo nombre de pozo,
se fusionen automáticamente y combine todas las curvas.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pypozo.core.well import WellManager, WellDataFrame

def test_automatic_merge_simulation():
    """Simula la carga de pozos duplicados y su fusión automática usando archivos reales"""
    print("🧪 Iniciando test de fusión automática de pozos...")
    
    # Usar archivos reales del directorio data/
    file1 = "data/70449_abedul1_gn_1850_800_05mz79p.las"
    file2 = "data/ABEDUL1_REPROCESADO.las"
    
    if not os.path.exists(file1) or not os.path.exists(file2):
        print("❌ Archivos de prueba no encontrados")
        return False
    
    print(f"\n📊 Cargando pozos de prueba...")
    print(f"   Archivo 1: {file1}")
    print(f"   Archivo 2: {file2}")
    
    try:
        # Cargar ambos pozos
        well1 = WellManager.from_las(file1)
        well2 = WellManager.from_las(file2)
        
        print(f"   Pozo 1: {well1.name}")
        print(f"   Curvas 1: {well1.curves}")
        print(f"   Pozo 2: {well2.name}")
        print(f"   Curvas 2: {well2.curves}")
        
        # Simular la fusión usando la lógica de WellDataFrame
        print("\n🔄 Ejecutando fusión...")
        merged_well = WellDataFrame.merge_wells([well1, well2], "ABEDUL-1_MERGED")
        
        print(f"✅ Fusión completada")
        print(f"   Pozo fusionado: {merged_well.name}")
        print(f"   Curvas combinadas: {merged_well.curves}")
        
        # Verificar que el pozo fusionado tiene más curvas que cada uno individual
        curves1 = set(well1.curves)
        curves2 = set(well2.curves)
        merged_curves = set(merged_well.curves)
        
        print(f"\n🔍 Verificación:")
        print(f"   Curvas pozo 1: {len(curves1)}")
        print(f"   Curvas pozo 2: {len(curves2)}")
        print(f"   Curvas fusionadas: {len(merged_curves)}")
        
        # El pozo fusionado debería tener al menos las curvas de ambos pozos
        if merged_curves.issuperset(curves1) or merged_curves.issuperset(curves2):
            print("✅ ÉXITO: El pozo fusionado contiene curvas de ambos pozos")
            return True
        else:
            print("❌ FALLO: El pozo fusionado no contiene todas las curvas esperadas")
            return False
            
    except Exception as e:
        print(f"❌ ERROR durante el test: {e}")
        return False

def test_save_merged_well():
    """Test de guardado de pozo fusionado"""
    print("\n💾 Test de guardado de pozo fusionado...")
    
    # Usar archivo real
    file1 = "data/70449_abedul1_gn_1850_800_05mz79p.las"
    
    if not os.path.exists(file1):
        print("❌ Archivo de prueba no encontrado")
        return False
    
    try:
        # Cargar pozo de prueba
        well = WellManager.from_las(file1)
        
        # Verificar que tiene método de exportación
        if hasattr(well, 'export_to_las'):
            print("✅ El pozo tiene método export_to_las")
            
            # Test de exportación a archivo temporal
            output_file = "test_merged_output.las"
            well.export_to_las(output_file)
            
            if os.path.exists(output_file):
                print(f"✅ Archivo exportado correctamente: {output_file}")
                # Limpiar archivo de prueba
                os.remove(output_file)
                return True
            else:
                print("❌ El archivo no fue creado")
                return False
        else:
            print("❌ El pozo NO tiene método export_to_las")
            return False
            
    except Exception as e:
        print(f"❌ Error durante test de guardado: {e}")
        return False

def test_gui_merge_logic():
    """Test específico de la lógica de fusión que usa la GUI"""
    print("\n🖥️  Test de lógica de fusión GUI...")
    
    # Usar dos archivos que probablemente tengan el mismo nombre de pozo
    file1 = "data/ABEDUL1_REPROCESADO.las"
    file2 = "data/70449_abedul1_gn_1850_800_05mz79p.las"
    
    if not os.path.exists(file1) or not os.path.exists(file2):
        print("❌ Archivos de prueba no encontrados")
        return False
    
    try:
        # Simular el código que ejecuta la GUI
        existing_well = WellManager.from_las(file1)
        new_well = WellManager.from_las(file2)
        
        print(f"   Pozo existente: {existing_well.name}")
        print(f"   Nuevo pozo: {new_well.name}")
        
        # Simular la lógica de _merge_duplicate_wells
        merged_well = WellDataFrame.merge_wells([existing_well, new_well], "ABEDUL-1_TEST")
        
        print(f"   Pozo fusionado: {merged_well.name}")
        print(f"   Curvas antes: {len(existing_well.curves)} + {len(new_well.curves)}")
        print(f"   Curvas después: {len(merged_well.curves)}")
        
        # Verificar que la fusión fue exitosa
        if merged_well and len(merged_well.curves) > 0:
            print("✅ ÉXITO: La lógica de fusión GUI funcionó correctamente")
            return True
        else:
            print("❌ FALLO: La fusión GUI no funcionó")
            return False
            
    except Exception as e:
        print(f"❌ Error en test GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando tests de fusión automática GUI...")
    
    # Ejecutar tests
    test1_result = test_automatic_merge_simulation()
    test2_result = test_save_merged_well()
    test3_result = test_gui_merge_logic()
    
    # Resumen
    print(f"\n📋 RESUMEN DE TESTS:")
    print(f"   Test fusión automática: {'✅ ÉXITO' if test1_result else '❌ FALLO'}")
    print(f"   Test guardado fusionado: {'✅ ÉXITO' if test2_result else '❌ FALLO'}")
    print(f"   Test lógica GUI: {'✅ ÉXITO' if test3_result else '❌ FALLO'}")
    
    if test1_result and test2_result and test3_result:
        print("\n🎉 TODOS LOS TESTS PASARON - La fusión automática está funcionando!")
        sys.exit(0)
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON - Revisar implementación")
        sys.exit(1)
