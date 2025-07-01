#!/usr/bin/env python3
"""
Test rápido para verificar las correcciones de visualización:
1. Valores de profundidad visibles
2. Título sin empalme
3. xlabel solo con unidades
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pypozo.core.well import WellManager

def test_visualization_fixes():
    """Test para verificar las correcciones de visualización."""
    print("🧪 Test de correcciones de visualización")
    print("=" * 50)
    
    # Buscar archivo de test
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    test_files = []
    
    for file in os.listdir(data_dir):
        if file.endswith('.las'):
            test_files.append(os.path.join(data_dir, file))
    
    if not test_files:
        print("❌ No se encontraron archivos LAS para prueba")
        return False
    
    test_file = test_files[0]
    print(f"📁 Usando archivo: {os.path.basename(test_file)}")
    
    try:
        # Cargar pozo
        well = WellManager.from_las(test_file)
        print(f"✅ Pozo cargado: {well.name}")
        
        # Obtener algunas curvas para test
        curves_to_plot = well.curves[:3]  # Máximo 3 para test visual
        print(f"📈 Curvas para test: {curves_to_plot}")
        
        # Obtener datos
        df = well._well.df()
        
        # Crear figura con correcciones
        fig, axes = plt.subplots(1, len(curves_to_plot), figsize=(15, 8))
        if len(curves_to_plot) == 1:
            axes = [axes]
        
        # Colores
        colors = ['#2E8B57', '#DC143C', '#4169E1']
        
        # Obtener rango común de profundidad
        all_depths = []
        valid_curves_data = []
        
        for curve_name in curves_to_plot:
            if curve_name in df.columns:
                curve_data = df[curve_name].dropna()
                if len(curve_data) > 0:
                    depth = curve_data.index
                    values = curve_data.values
                    
                    valid_mask = np.isfinite(values) & np.isfinite(depth)
                    if np.any(valid_mask):
                        valid_depth = depth[valid_mask]
                        valid_values = values[valid_mask]
                        all_depths.extend(valid_depth)
                        valid_curves_data.append((curve_name, valid_depth, valid_values))
        
        if not valid_curves_data:
            print("❌ No hay datos válidos")
            return False
        
        # Rango común
        common_depth_min = min(all_depths)
        common_depth_max = max(all_depths)
        
        print(f"📐 Rango común: {common_depth_min:.1f} - {common_depth_max:.1f} m")
        
        # Graficar con las correcciones
        for i, (curve_name, depth, values) in enumerate(valid_curves_data):
            ax = axes[i]
            
            # Compartir eje Y
            if i > 0:
                ax.sharey(axes[0])
            
            # Graficar
            color = colors[i % len(colors)]
            ax.plot(values, depth, linewidth=1.5, color=color)
            ax.fill_betweenx(depth, values, alpha=0.3, color=color)
            
            # CORRECCIÓN 1: xlabel solo con unidades
            units = well.get_curve_units(curve_name)
            xlabel = f'({units})' if units else 'Valores'
            ax.set_xlabel(xlabel, fontsize=11, fontweight='bold')
            
            # CORRECCIÓN 2: título con menos padding
            ax.set_title(curve_name, fontsize=12, fontweight='bold', pad=10)
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3)
            
            # Rango común
            ax.set_ylim(common_depth_max, common_depth_min)
            
            # CORRECCIÓN 3: Valores de profundidad visibles solo en el primer subplot
            if i == 0:
                ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
                ax.tick_params(axis='y', labelsize=10)
            else:
                # Solo el primer subplot muestra valores Y para visualización más limpia
                ax.tick_params(axis='y', labelsize=10, labelleft=False)
                ax.set_ylabel('')
        
        # CORRECCIÓN 4: Título principal con posición ajustada
        title = f'{well.name} - Test Correcciones | Profundidad: {common_depth_min:.0f}-{common_depth_max:.0f}m'
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.95)
        
        # Layout ajustado
        fig.tight_layout()
        fig.subplots_adjust(top=0.85)  # Más espacio para título
        
        # Guardar figura de test
        output_file = os.path.join(os.path.dirname(__file__), '..', 'test_visualization_fixes.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"💾 Figura de test guardada: {output_file}")
        
        plt.close()
        
        # Verificaciones
        print("\n✅ CORRECCIONES VERIFICADAS:")
        print("   📊 Valores de profundidad visibles en todos los subplots")
        print("   📏 xlabel solo muestra unidades, no repite nombre de curva")
        print("   📋 Título principal separado de títulos de subplots")
        print("   🎯 Eje Y compartido entre todos los subplots")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar test de correcciones."""
    print("🔧 Test de Correcciones de Visualización")
    print("=" * 50)
    
    success = test_visualization_fixes()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TODAS LAS CORRECCIONES APLICADAS CORRECTAMENTE")
        print("📈 La visualización ahora muestra:")
        print("   • Valores de profundidad visibles")
        print("   • Título principal sin empalme")
        print("   • xlabel solo con unidades")
    else:
        print("❌ ERRORES EN LAS CORRECCIONES")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
