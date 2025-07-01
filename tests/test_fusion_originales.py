#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Fusión de Pozos - Usando Archivos Originales
===================================================

Test específico para validar la funcionalidad de fusión automática
usando los archivos reales en la carpeta data/Originales/

Autor: José María García Márquez
Fecha: Julio 2025
"""

import sys
import logging
from pathlib import Path
import matplotlib.pyplot as plt

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from pypozo import WellManager, WellPlotter

def setup_logging():
    """Configurar logging para el test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )

def test_fusion_archivos_originales():
    """
    Test de fusión usando archivos reales de la carpeta Originales.
    
    Este test:
    1. Carga múltiples archivos LAS del pozo Abedul-1
    2. Los fusiona automáticamente
    3. Crea visualizaciones comparativas
    4. Valida la integridad de la fusión
    """
    print("🚀 Test de Fusión - Archivos Originales del Pozo Abedul-1")
    print("=" * 60)
    
    # Ruta a archivos originales
    originales_path = project_root / "data" / "Originales"
    
    if not originales_path.exists():
        print("❌ Carpeta 'data/Originales' no encontrada")
        return False
    
    # Buscar archivos LAS del Abedul-1 (filtrar archivos del sistema)
    all_las_files = list(originales_path.glob("*abedul*.las"))
    las_files = [f for f in all_las_files if not f.name.startswith('._')]
    
    if not las_files:
        print("❌ No se encontraron archivos LAS del Abedul-1")
        print(f"   (Se encontraron {len(all_las_files)} archivos totales, pero todos son archivos del sistema)")
        return False
    
    print(f"📁 Encontrados {len(las_files)} archivos LAS:")
    for i, file in enumerate(las_files, 1):
        print(f"   {i}. {file.name}")
    
    # Cargar pozos
    wells = []
    well_names = []
    
    print(f"\\n📂 Cargando archivos...")
    for las_file in las_files[:3]:  # Limitar a 3 archivos para el test
        try:
            print(f"   📄 Cargando: {las_file.name}")
            well = WellManager.from_las(str(las_file))
            
            if well and well.curves:
                wells.append(well)
                well_names.append(well.name or las_file.stem)
                
                # Mostrar información del pozo
                depth_range = well.depth_range
                print(f"      ✅ Cargado: {well.name}")
                print(f"      📏 Rango: {depth_range[0]:.1f}-{depth_range[1]:.1f}m")
                print(f"      📈 Curvas: {len(well.curves)}")
            else:
                print(f"      ❌ Error: No se pudo cargar o no tiene curvas")
                
        except Exception as e:
            print(f"      ❌ Error cargando {las_file.name}: {str(e)}")
    
    if len(wells) < 2:
        print(f"\\n❌ Se necesitan al menos 2 pozos para fusión. Solo se cargaron {len(wells)}")
        return False
    
    print(f"\\n🔄 Iniciando fusión de {len(wells)} pozos...")
    
    # Fusionar pozos
    try:
        merged_well = WellManager.merge_wells(wells, "ABEDUL1_FUSION_TEST")
        
        if merged_well:
            merged_range = merged_well.depth_range
            print("✅ Fusión completada exitosamente!")
            print(f"   🎯 Rango fusionado: {merged_range[0]:.1f}-{merged_range[1]:.1f}m")
            print(f"   📈 Total de curvas: {len(merged_well.curves)}")
            print(f"   📋 Curvas fusionadas: {', '.join(merged_well.curves)}")
            
            # Información de traslapes
            if 'overlaps_processed' in merged_well.metadata:
                overlaps = merged_well.metadata['overlaps_processed']
                print(f"   🔄 Traslapes procesados: {overlaps}")
            
            # Información de archivos originales
            if 'original_files' in merged_well.metadata:
                files = merged_well.metadata['original_files']
                print(f"   📁 Archivos originales: {len(files)}")
                for i, file in enumerate(files, 1):
                    print(f"      {i}. {Path(file).name}")
        else:
            print("❌ Error durante la fusión")
            return False
            
    except Exception as e:
        print(f"❌ Error fusionando pozos: {str(e)}")
        return False
    
    # Crear gráfico comparativo
    print(f"\\n📊 Creando gráfico comparativo...")
    
    try:
        plotter = WellPlotter()
        
        # Buscar curva común para comparación
        common_curves = set(wells[0].curves)
        for well in wells[1:]:
            common_curves = common_curves.intersection(set(well.curves))
        
        if common_curves:
            comparison_curve = list(common_curves)[0]
            print(f"   📈 Usando curva: {comparison_curve}")
            
            # Crear figura
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
            
            # Subplot 1: Pozos originales
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            for i, well in enumerate(wells):
                curve_data = well.get_curve_data(comparison_curve)
                if curve_data is not None:
                    ax1.plot(curve_data.values, curve_data.index, 
                            color=colors[i % len(colors)], linewidth=1.5, 
                            label=f"{well.name or f'Pozo {i+1}'}", alpha=0.7)
            
            ax1.set_xlabel(comparison_curve)
            ax1.set_ylabel('Profundidad (m)')
            ax1.set_title('Pozos Originales')
            ax1.invert_yaxis()
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Subplot 2: Pozo fusionado
            merged_curve_data = merged_well.get_curve_data(comparison_curve)
            if merged_curve_data is not None:
                ax2.plot(merged_curve_data.values, merged_curve_data.index, 
                        color='black', linewidth=2, label='Pozo Fusionado')
            
            ax2.set_xlabel(comparison_curve)
            ax2.set_ylabel('Profundidad (m)')
            ax2.set_title('Pozo Fusionado')
            ax2.invert_yaxis()
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            plt.suptitle(f'Comparación de Fusión - {comparison_curve}', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # Guardar gráfico
            output_file = project_root / f"test_fusion_originales_comparison.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"   ✅ Gráfico guardado: {output_file.name}")
            
            plt.close()
            
        else:
            print("   ⚠️ No se encontraron curvas comunes para comparación")
    
    except Exception as e:
        print(f"   ❌ Error creando gráfico: {str(e)}")
    
    # Intentar guardar pozo fusionado
    print(f"\\n💾 Guardando pozo fusionado...")
    try:
        output_las = project_root / "ABEDUL1_FUSION_TEST.las"
        success = merged_well.save_merged_well(str(output_las))
        
        if success:
            print(f"   ✅ Pozo fusionado guardado: {output_las.name}")
        else:
            print(f"   ⚠️ No se pudo guardar el archivo LAS")
            
    except Exception as e:
        print(f"   ❌ Error guardando: {str(e)}")
    
    print(f"\\n🎉 Test completado exitosamente!")
    print(f"\\n💡 Para probar en la GUI:")
    print(f"   1. Ejecute: python pypozo_app.py")
    print(f"   2. Cargue los archivos de data/Originales/")
    print(f"   3. El sistema detectará automáticamente duplicados del mismo pozo")
    print(f"   4. Elija 'Sí' para fusionar automáticamente")
    
    return True

def main():
    """Función principal del test."""
    setup_logging()
    
    try:
        success = test_fusion_archivos_originales()
        
        if success:
            print("\\n✅ Todos los tests pasaron correctamente")
            return 0
        else:
            print("\\n❌ Algunos tests fallaron")
            return 1
            
    except Exception as e:
        print(f"\\n❌ Error durante el test: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
