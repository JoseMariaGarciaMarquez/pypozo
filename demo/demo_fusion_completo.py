#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Completo: Fusión Automática de Pozos - PyPozo 2.0
=====================================================

Demostración completa de la funcionalidad de fusión automática
que incluye:
1. Simulación de registros separados
2. Fusión automática con traslapes
3. Visualización comparativa
4. Guardado del pozo fusionado

Autor: José María García Márquez
Fecha: Julio 2025
"""

import sys
import os
import logging
import numpy as np
import pandas as pd
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from pypozo import WellManager, WellPlotter
    import lasio
    import matplotlib.pyplot as plt
    DEPENDENCIES_OK = True
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    DEPENDENCIES_OK = False

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_synthetic_well_files():
    """
    Crear archivos LAS sintéticos que simulan un pozo registrado en etapas.
    
    Simula un caso real donde:
    - Etapa 1: Registros básicos (GR, SP, CAL) 
    - Etapa 2: Registros eléctricos (RT, RES) con traslape en GR
    - Etapa 3: Registros de porosidad (NPHI, DENS) 
    """
    print("🏗️ Creando archivos LAS sintéticos...")
    
    output_dir = Path("demo_fusion_output")
    output_dir.mkdir(exist_ok=True)
    
    well_name = "DEMO_POZO_FUSION"
    files_created = []
    
    # Etapa 1: Registros básicos (1000-1200m)
    print("   📝 Etapa 1: Registros básicos (1000-1200m)")
    depth1 = np.arange(1000, 1200.5, 0.5)
    
    # Simular registros realistas
    gr1 = 60 + 40 * np.sin(depth1 / 50) + np.random.normal(0, 5, len(depth1))
    sp1 = -30 + 20 * np.cos(depth1 / 60) + np.random.normal(0, 3, len(depth1))
    cal1 = 8.5 + 1.0 * np.sin(depth1 / 80) + np.random.normal(0, 0.3, len(depth1))
    
    # Crear archivo LAS
    las1 = lasio.LASFile()
    las1.well.WELL = well_name
    las1.well.COMP = "PyPozo Demo"
    las1.well.LOC = "Demo Location"
    las1.well.DATE = "2025-07-01"
    
    las1.append_curve('DEPT', depth1, unit='M', descr='Depth')
    las1.append_curve('GR', gr1, unit='GAPI', descr='Gamma Ray')
    las1.append_curve('SP', sp1, unit='MV', descr='Spontaneous Potential')
    las1.append_curve('CAL', cal1, unit='IN', descr='Caliper')
    
    file1 = output_dir / f"{well_name}_BASICOS.las"
    las1.write(str(file1), version=2.0)
    files_created.append(file1)
    print(f"      ✅ Creado: {file1.name}")
    
    # Etapa 2: Registros eléctricos (1150-1350m) - Traslape en GR
    print("   📝 Etapa 2: Registros eléctricos (1150-1350m)")
    depth2 = np.arange(1150, 1350.5, 0.5)
    
    # GR con continuidad pero algo de variación (para ver el promediado)
    gr2 = 60 + 40 * np.sin(depth2 / 50) + np.random.normal(0, 8, len(depth2))  # Más ruido
    rt2 = np.exp(1.5 + 0.8 * np.sin(depth2 / 70)) + np.random.normal(0, 0.2, len(depth2))
    res2 = np.exp(1.2 + 0.6 * np.cos(depth2 / 90)) + np.random.normal(0, 0.15, len(depth2))
    
    las2 = lasio.LASFile()
    las2.well.WELL = well_name
    las2.well.COMP = "PyPozo Demo"
    las2.well.LOC = "Demo Location"
    las2.well.DATE = "2025-07-01"
    
    las2.append_curve('DEPT', depth2, unit='M', descr='Depth')
    las2.append_curve('GR', gr2, unit='GAPI', descr='Gamma Ray')
    las2.append_curve('RT', rt2, unit='OHMM', descr='Resistivity True')
    las2.append_curve('RES', res2, unit='OHMM', descr='Resistivity')
    
    file2 = output_dir / f"{well_name}_ELECTRICOS.las"
    las2.write(str(file2), version=2.0)
    files_created.append(file2)
    print(f"      ✅ Creado: {file2.name}")
    
    # Etapa 3: Registros de porosidad (1300-1500m)
    print("   📝 Etapa 3: Registros de porosidad (1300-1500m)")
    depth3 = np.arange(1300, 1500.5, 0.5)
    
    nphi3 = 0.20 + 0.15 * np.sin(depth3 / 100) + np.random.normal(0, 0.03, len(depth3))
    dens3 = 2.4 + 0.3 * np.cos(depth3 / 120) + np.random.normal(0, 0.05, len(depth3))
    
    las3 = lasio.LASFile()
    las3.well.WELL = well_name
    las3.well.COMP = "PyPozo Demo"
    las3.well.LOC = "Demo Location"
    las3.well.DATE = "2025-07-01"
    
    las3.append_curve('DEPT', depth3, unit='M', descr='Depth')
    las3.append_curve('NPHI', nphi3, unit='V/V', descr='Neutron Porosity')
    las3.append_curve('DENS', dens3, unit='G/C3', descr='Bulk Density')
    
    file3 = output_dir / f"{well_name}_POROSIDAD.las"
    las3.write(str(file3), version=2.0)
    files_created.append(file3)
    print(f"      ✅ Creado: {file3.name}")
    
    print(f"📁 Archivos creados en: {output_dir}")
    return files_created, well_name

def demonstrate_fusion():
    """Demostrar la funcionalidad de fusión paso a paso."""
    
    print("\n" + "="*60)
    print("🚀 DEMO: FUSIÓN AUTOMÁTICA DE POZOS - PyPozo 2.0")
    print("="*60)
    
    # Crear archivos de prueba
    las_files, well_name = create_synthetic_well_files()
    
    print(f"\n📂 Cargando {len(las_files)} archivos LAS del pozo '{well_name}'...")
    
    # Cargar cada archivo individualmente
    wells = []
    for i, file_path in enumerate(las_files, 1):
        print(f"\n   📄 Cargando archivo {i}: {file_path.name}")
        try:
            well = WellManager.from_las(file_path)
            wells.append(well)
            
            depth_range = well.depth_range
            print(f"      ✅ Nombre: {well.name}")
            print(f"      📏 Rango: {depth_range[0]:.1f}-{depth_range[1]:.1f}m")
            print(f"      📈 Curvas: {', '.join(well.curves)} ({len(well.curves)})")
            
        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            return False
    
    if len(wells) != len(las_files):
        print("❌ No se pudieron cargar todos los archivos")
        return False
    
    print(f"\n🔄 Iniciando fusión de {len(wells)} pozos...")
    
    # Ejecutar fusión
    try:
        merged_well = WellManager.merge_wells(wells, well_name)
        
        if merged_well is None:
            print("❌ La fusión falló")
            return False
        
        print("✅ Fusión completada exitosamente!")
        
        # Mostrar resultados
        merged_range = merged_well.depth_range
        print(f"\n📊 RESULTADOS DE LA FUSIÓN:")
        print(f"   🎯 Rango fusionado: {merged_range[0]:.1f}-{merged_range[1]:.1f}m")
        print(f"   📈 Total de curvas: {len(merged_well.curves)}")
        print(f"   📋 Curvas fusionadas: {', '.join(sorted(merged_well.curves))}")
        
        # Información de traslapes
        if 'overlaps_processed' in merged_well.metadata:
            overlaps = merged_well.metadata['overlaps_processed']
            print(f"   🔄 Traslapes procesados: {overlaps}")
        
        # Información de archivos originales
        if 'original_files' in merged_well.metadata:
            orig_files = merged_well.metadata['original_files']
            print(f"   📁 Archivos fusionados: {len(orig_files)}")
            for i, file in enumerate(orig_files, 1):
                print(f"      {i}. {Path(file).name}")
        
        return merged_well, wells
        
    except Exception as e:
        print(f"❌ Error durante la fusión: {str(e)}")
        return False

def create_comparison_plot(merged_well, original_wells):
    """Crear gráfico comparativo mostrando el antes y después de la fusión."""
    
    print(f"\n📊 Creando gráfico comparativo...")
    
    try:
        # Configurar matplotlib
        plt.style.use('default')
        fig, axes = plt.subplots(1, 3, figsize=(18, 12))
        fig.suptitle('Demo: Fusión Automática de Pozos - PyPozo 2.0', 
                    fontsize=16, fontweight='bold', y=0.95)
        
        # Colores para cada pozo original
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        # Subplot 1: Pozos originales por separado
        ax1 = axes[0]
        ax1.set_title('Pozos Originales Separados', fontweight='bold', pad=20)
        
        for i, well in enumerate(original_wells):
            well_data = well._well.df()
            depth = well_data.index
            
            # Graficar GR si está disponible
            if 'GR' in well_data.columns:
                gr_data = well_data['GR'].dropna()
                ax1.plot(gr_data.values, gr_data.index, 
                        color=colors[i], linewidth=2, alpha=0.8,
                        label=f'Pozo {i+1} ({len(well.curves)} curvas)')
        
        ax1.set_xlabel('GR (GAPI)', fontweight='bold')
        ax1.set_ylabel('Profundidad (m)', fontweight='bold')
        ax1.invert_yaxis()
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right')
        
        # Subplot 2: Pozo fusionado
        ax2 = axes[1]
        ax2.set_title('Pozo Fusionado (GR)', fontweight='bold', pad=20)
        
        merged_data = merged_well._well.df()
        if 'GR' in merged_data.columns:
            gr_merged = merged_data['GR'].dropna()
            ax2.plot(gr_merged.values, gr_merged.index, 
                    color='red', linewidth=2, alpha=0.9, label='GR Fusionado')
            ax2.fill_betweenx(gr_merged.index, gr_merged.values, alpha=0.3, color='red')
        
        ax2.set_xlabel('GR (GAPI)', fontweight='bold')
        ax2.set_ylabel('Profundidad (m)', fontweight='bold')
        ax2.invert_yaxis()
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper right')
        
        # Subplot 3: Todas las curvas fusionadas
        ax3 = axes[2]
        ax3.set_title('Todas las Curvas Fusionadas', fontweight='bold', pad=20)
        
        # Normalizar curvas para mostrar en el mismo eje
        curve_colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        
        for i, curve_name in enumerate(sorted(merged_well.curves)):
            if curve_name in merged_data.columns:
                curve_data = merged_data[curve_name].dropna()
                if len(curve_data) > 0:
                    # Normalizar 0-1
                    normalized = (curve_data - curve_data.min()) / (curve_data.max() - curve_data.min())
                    
                    color = curve_colors[i % len(curve_colors)]
                    ax3.plot(normalized, curve_data.index, 
                            color=color, linewidth=1.5, alpha=0.8, label=curve_name)
        
        ax3.set_xlabel('Valores Normalizados (0-1)', fontweight='bold')
        ax3.set_ylabel('Profundidad (m)', fontweight='bold')
        ax3.invert_yaxis()
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar gráfico
        output_file = Path("demo_fusion_output") / "fusion_demo_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✅ Gráfico guardado: {output_file}")
        
        # Mostrar estadísticas
        print(f"\n📈 ESTADÍSTICAS DEL GRÁFICO:")
        print(f"   📊 Pozos originales: {len(original_wells)}")
        print(f"   🎯 Rango total: {merged_well.depth_range[0]:.1f}-{merged_well.depth_range[1]:.1f}m")
        print(f"   📈 Curvas en pozo fusionado: {len(merged_well.curves)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando gráfico: {str(e)}")
        return False

def save_merged_well(merged_well):
    """Guardar el pozo fusionado como archivo LAS."""
    
    print(f"\n💾 Guardando pozo fusionado...")
    
    try:
        output_file = Path("demo_fusion_output") / f"{merged_well.name}_FUSIONADO.las"
        success = merged_well.save_merged_well(output_file)
        
        if success:
            print(f"   ✅ Pozo fusionado guardado: {output_file}")
            
            # Verificar que se puede recargar
            reloaded = WellManager.from_las(output_file)
            if reloaded.is_valid:
                print(f"   ✅ Verificación: Archivo se puede recargar correctamente")
                print(f"   📈 Curvas verificadas: {len(reloaded.curves)}")
            else:
                print(f"   ⚠️ Advertencia: Archivo creado pero con problemas de validación")
        else:
            print(f"   ❌ Error guardando archivo")
            
        return success
        
    except Exception as e:
        print(f"❌ Error guardando pozo fusionado: {str(e)}")
        return False

def main():
    """Función principal del demo."""
    
    if not DEPENDENCIES_OK:
        print("❌ No se pueden ejecutar el demo sin las dependencias requeridas")
        return False
    
    print("🎯 PyPozo 2.0 - Demo Completo: Fusión Automática de Pozos")
    print("="*65)
    print()
    print("Este demo muestra:")
    print("✅ Creación de archivos LAS sintéticos con traslapes")  
    print("✅ Fusión automática de múltiples pozos")
    print("✅ Manejo inteligente de traslapes (promediado)")
    print("✅ Visualización comparativa antes/después")
    print("✅ Guardado del pozo fusionado")
    print()
    
    try:
        # Ejecutar demostración
        result = demonstrate_fusion()
        
        if not result:
            print("❌ Demo falló en la fase de fusión")
            return False
        
        merged_well, original_wells = result
        
        # Crear gráfico comparativo
        plot_success = create_comparison_plot(merged_well, original_wells)
        
        # Guardar pozo fusionado
        save_success = save_merged_well(merged_well)
        
        # Resumen final
        print(f"\n" + "="*60)
        print(f"🎉 DEMO COMPLETADO EXITOSAMENTE")
        print(f"="*60)
        print(f"✅ Fusión automática: Exitosa")
        print(f"✅ Gráfico comparativo: {'Exitoso' if plot_success else 'Falló'}")
        print(f"✅ Guardado de archivo: {'Exitoso' if save_success else 'Falló'}")
        print(f"\n📁 Archivos generados en: demo_fusion_output/")
        print(f"   📄 Archivos LAS originales (3)")
        print(f"   📄 Archivo LAS fusionado (1)")
        print(f"   📊 Gráfico comparativo (PNG)")
        print(f"\n💡 Para usar en la GUI:")
        print(f"   1. Ejecute: python pypozo_app.py")
        print(f"   2. Cargue los archivos creados en demo_fusion_output/")
        print(f"   3. El sistema detectará automáticamente los duplicados")
        print(f"   4. Elija 'Sí' para fusionar automáticamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error crítico en el demo: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
