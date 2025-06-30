#!/usr/bin/env python3
"""
PyPozo 2.0 - Script de Ejemplo
==============================

Este script demuestra cómo usar PyPozo 2.0 para cargar y visualizar
registros geofísicos de pozos.

Ejemplo: Visualizar el registro de GR del pozo Abedul
"""

import sys
from pathlib import Path

# Agregar el path del módulo
sys.path.insert(0, str(Path(__file__).parent))

# Importar PyPozo
from pypozo import WellManager, WellPlotter, StandardWorkflow

def main():
    """Función principal del ejemplo."""
    print("🔧 PyPozo 2.0 - Ejemplo de Uso")
    print("=" * 40)
    
    # Ruta al archivo LAS del Abedul
    las_file = Path(__file__).parent.parent / "data" / "70449_abedul1_gn_1850_800_05mz79p.las"
    
    if not las_file.exists():
        print(f"❌ Archivo no encontrado: {las_file}")
        print("💡 Verifica que el archivo LAS esté en la carpeta 'data/'")
        return
    
    try:
        # 1. Cargar el pozo
        print(f"📁 Cargando pozo: {las_file.name}")
        well = WellManager.from_las(las_file)
        
        # 2. Mostrar información básica
        print(f"✅ Pozo cargado: {well.name}")
        print(f"📊 Curvas disponibles: {len(well.curves)}")
        print(f"📏 Intervalo: {well.depth_range[0]:.1f} - {well.depth_range[1]:.1f} m")
        
        # 3. Listar curvas disponibles
        print("\n📋 Curvas disponibles:")
        for i, curve in enumerate(well.curves, 1):
            print(f"  {i:2d}. {curve}")
        
        # 4. Buscar el registro de GR
        gr_curves = [curve for curve in well.curves if 'GR' in curve.upper()]
        
        if not gr_curves:
            print("\n⚠️  No se encontró curva de GR")
            print("💡 Curvas disponibles que podrían ser GR:")
            possible_gr = [curve for curve in well.curves 
                          if any(keyword in curve.upper() 
                                for keyword in ['GAMMA', 'RAY', 'GR_', 'SGRD'])]
            for curve in possible_gr:
                print(f"   - {curve}")
        else:
            gr_curve = gr_curves[0]  # Usar la primera curva de GR encontrada
            print(f"\n📈 Curva de GR encontrada: {gr_curve}")
            
            # 5. Crear visualización básica
            plotter = WellPlotter()
            
            print("\n🎨 Generando visualización...")
            try:
                # Visualizar el registro de GR
                plotter.plot_well_logs(
                    well, 
                    curves=[gr_curve],
                    title=f"Registro de Rayos Gamma - {well.name}",
                    show_grid=True,
                    save_path=Path(__file__).parent.parent / "output_workflow_simple" / f"{well.name}_GR.png"
                )
                print("✅ Visualización generada exitosamente")
                
            except Exception as e:
                print(f"⚠️  Error en visualización: {str(e)}")
                print("💡 Usando visualización simulada...")
                
        # 6. Workflow completo (opcional)
        print("\n🔄 Ejecutando workflow estándar...")
        workflow = StandardWorkflow()
        
        try:
            results = workflow.process_well(
                las_file,
                output_dir=Path(__file__).parent.parent / "output_workflow_simple"
            )
            print("✅ Workflow completado")
            
        except Exception as e:
            print(f"⚠️  Error en workflow: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

def list_available_wells():
    """Listar pozos disponibles en la carpeta data/."""
    data_dir = Path(__file__).parent.parent / "data"
    
    if not data_dir.exists():
        print("❌ Carpeta 'data/' no encontrada")
        return
    
    las_files = list(data_dir.glob("*.las"))
    
    if not las_files:
        print("❌ No se encontraron archivos LAS en 'data/'")
        return
    
    print("📁 Pozos disponibles:")
    for i, file in enumerate(las_files, 1):
        print(f"  {i}. {file.name}")

if __name__ == "__main__":
    # Ejecutar el ejemplo
    main()
    
    # Listar pozos disponibles
    print("\n" + "=" * 40)
    list_available_wells()