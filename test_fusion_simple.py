#!/usr/bin/env python3
"""
Test Simple de Fusión - PyPozo 2.0
==================================

Test rápido para verificar que la fusión de pozos funciona
correctamente tanto programáticamente como desde la GUI.

Autor: José María García Márquez
Fecha: Enero 2025
"""

import sys
import logging
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pypozo.core.well import WellManager, WellDataFrame

def test_basic_functionality():
    """Test básico de funcionalidad."""
    
    print("🧪 TEST BÁSICO DE FUSIÓN DE POZOS")
    print("=" * 50)
    
    try:
        # Verificar que los archivos de prueba existen
        test_dir = Path("test_merger_output")
        if not test_dir.exists():
            print("❌ Directorio test_merger_output no existe")
            print("   Ejecute primero: python test_real_merger.py")
            return False
        
        # Buscar archivos LAS de prueba
        las_files = list(test_dir.glob("test_well_*.las"))
        if len(las_files) < 2:
            print("❌ Se necesitan al menos 2 archivos de prueba")
            print("   Ejecute primero: python test_real_merger.py")
            return False
        
        print(f"📁 Encontrados {len(las_files)} archivos de prueba")
        
        # Cargar pozos
        wells = []
        for file in las_files[:2]:  # Solo usar los primeros 2
            print(f"   📂 Cargando: {file.name}")
            well = WellManager.from_las(file)
            wells.append(well)
            print(f"      ✅ {well.name}: {len(well.curves)} curvas")
        
        # Fusionar pozos
        print(f"\n🔗 Fusionando {len(wells)} pozos...")
        merged_well = WellDataFrame.merge_wells(wells, "TEST_FUSION")
        
        if merged_well is None:
            print("❌ Error en la fusión")
            return False
        
        print(f"✅ Fusión exitosa:")
        print(f"   📋 Nombre: {merged_well.name}")
        print(f"   📊 Curvas: {len(merged_well.curves)}")
        print(f"   🎯 Rango: {merged_well.depth_range[0]:.1f}-{merged_well.depth_range[1]:.1f}m")
        
        # Probar guardado
        output_file = test_dir / "fusion_test_output.las"
        print(f"\n💾 Guardando pozo fusionado...")
        success = merged_well.export_to_las(output_file)
        
        if success:
            file_size = output_file.stat().st_size
            print(f"✅ Archivo guardado: {output_file.name} ({file_size} bytes)")
        else:
            print("❌ Error guardando archivo")
            return False
        
        print(f"\n🎉 TODAS LAS PRUEBAS EXITOSAS")
        print(f"💡 La funcionalidad de fusión y guardado está funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        return False

def main():
    """Función principal."""
    
    # Configurar logging mínimo
    logging.basicConfig(level=logging.WARNING)
    
    success = test_basic_functionality()
    
    if success:
        print(f"\n✅ CONCLUSIÓN: La fusión de pozos está funcionando correctamente")
        print(f"   🔧 Para probar en la GUI:")
        print(f"      1. Ejecute: python pypozo_app.py")
        print(f"      2. Cargue múltiples pozos LAS")
        print(f"      3. Vaya al tab 'Comparar'")
        print(f"      4. Seleccione pozos a fusionar")
        print(f"      5. Haga clic en 'Fusionar Seleccionados'")
        print(f"      6. Confirme el guardado cuando se le pregunte")
    else:
        print(f"\n❌ CONCLUSIÓN: Hay problemas con la fusión de pozos")
        print(f"   🔧 Verifique los logs para más detalles")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
