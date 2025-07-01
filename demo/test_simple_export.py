#!/usr/bin/env python3
"""
Test simple para verificar el problema del guardado de archivos fusionados.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from pypozo.core.well import WellManager

def test_simple_export():
    """Test simple de exportación"""
    print("=== TEST SIMPLE DE EXPORTACIÓN ===")
    
    # Usar un archivo que sabemos que funciona
    test_file = "data/70449_abedul1_gn_1850_800_05mz79p.las"
    
    if not Path(test_file).exists():
        print(f"❌ Archivo no encontrado: {test_file}")
        return False
    
    try:
        # Cargar un pozo simple
        print(f"1. Cargando pozo: {test_file}")
        well_manager = WellManager.from_las(test_file)
        print(f"   ✅ Cargado: {well_manager.name}")
        print(f"   - Curvas: {well_manager.curves}")
        print(f"   - Profundidad: {well_manager.depth_range}")
        
        # Intentar exportar directamente (sin fusión)
        output_path = "test_simple_export.las"
        print(f"\n2. Exportando a: {output_path}")
        
        success = well_manager.export_to_las(output_path)
        
        if success:
            # Verificar el archivo
            output_file = Path(output_path)
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"   ✅ Archivo creado: {file_size} bytes")
                
                # Leer las primeras líneas
                with open(output_path, 'r') as f:
                    lines = f.readlines()[:15]
                    print(f"   - Primeras líneas:")
                    for i, line in enumerate(lines, 1):
                        print(f"     {i:2d}: {line.strip()}")
                
                return True
            else:
                print("   ❌ Archivo no creado")
                return False
        else:
            print("   ❌ Error en exportación")
            return False
            
    except Exception as e:
        print(f"\n❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_export()
    sys.exit(0 if success else 1)
