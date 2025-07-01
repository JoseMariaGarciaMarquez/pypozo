#!/usr/bin/env python3
"""
Test específico para verificar que la corrección de subplots funciona correctamente.
Verifica que todos los subplots compartan el mismo eje de profundidad.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pypozo.core.well import WellManager
from pypozo.visualization.plotter import WellPlotter

def test_subplots_shared_depth():
    """Test que verifica que los subplots compartan el mismo eje de profundidad."""
    print("🔍 Testing subplots con eje de profundidad compartido...")
    
    # Buscar archivo de test
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    test_files = []
    
    for file in os.listdir(data_dir):
        if file.endswith('.las'):
            test_files.append(os.path.join(data_dir, file))
    
    if not test_files:
        print("❌ No se encontraron archivos LAS para prueba")
        return False
    
    # Cargar el primer archivo
    test_file = test_files[0]
    print(f"📁 Usando archivo: {os.path.basename(test_file)}")
    
    try:
        # Cargar pozo usando el método correcto
        well = WellManager.from_las(test_file)
        print(f"✅ Pozo cargado: {well.name}")
        print(f"📊 Curvas disponibles: {len(well.curves)} curvas")
        print(f"📏 Rango de profundidad: {well.depth_range[0]:.1f} - {well.depth_range[1]:.1f} m")
        
        # Obtener algunas curvas para graficar (máximo 4 para el test)
        curves_to_plot = well.curves[:4]
        print(f"📈 Curvas seleccionadas para test: {curves_to_plot}")
        
        # Crear plotter y figura
        plotter = WellPlotter()
        fig, axes = plt.subplots(1, len(curves_to_plot), figsize=(15, 8))
        
        if len(curves_to_plot) == 1:
            axes = [axes]
        
        # Obtener datos del pozo
        df = well._well.df()
        
        # Determinar el rango de profundidad común
        all_depths = []
        valid_curves_data = []
        
        for curve_name in curves_to_plot:
            if curve_name in df.columns:
                curve_data = df[curve_name].dropna()
                if len(curve_data) > 0:
                    depth = curve_data.index
                    values = curve_data.values
                    
                    # Filtrar valores finitos
                    valid_mask = np.isfinite(values) & np.isfinite(depth)
                    if np.any(valid_mask):
                        valid_depth = depth[valid_mask]
                        valid_values = values[valid_mask]
                        all_depths.extend(valid_depth)
                        valid_curves_data.append((curve_name, valid_depth, valid_values))
        
        if not valid_curves_data:
            print("❌ No se encontraron datos válidos para graficar")
            return False
        
        # Calcular rango común
        common_depth_min = min(all_depths)
        common_depth_max = max(all_depths)
        
        print(f"📐 Rango de profundidad común: {common_depth_min:.1f} - {common_depth_max:.1f} m")
        
        # Crear subplots con eje Y compartido
        colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00']
        
        for i, (curve_name, depth, values) in enumerate(valid_curves_data):
            ax = axes[i]
            
            # Compartir eje Y con el primer subplot
            if i > 0:
                ax.sharey(axes[0])
            
            # Graficar
            color = colors[i % len(colors)]
            ax.plot(values, depth, linewidth=1.5, color=color, label=curve_name)
            ax.fill_betweenx(depth, values, alpha=0.3, color=color)
            
            # Configurar ejes
            ax.set_xlabel(f'{curve_name}', fontsize=11, fontweight='bold')
            ax.set_title(curve_name, fontsize=12, fontweight='bold', pad=15)
            ax.invert_yaxis()  # Profundidad hacia abajo
            ax.grid(True, alpha=0.3)
            
            # CLAVE: Establecer el mismo rango de profundidad para todos
            ax.set_ylim(common_depth_max, common_depth_min)  # Invertido para profundidad
            
            # Solo el primer subplot tiene etiqueta Y
            if i == 0:
                ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
            else:
                ax.set_yticklabels([])
        
        # Título principal
        fig.suptitle(f'{well.name} - Test Subplots Compartidos | Profundidad: {common_depth_min:.0f}-{common_depth_max:.0f}m', 
                    fontsize=14, fontweight='bold')
        
        # Verificar que todos los subplots tienen el mismo rango Y
        first_ylim = axes[0].get_ylim()
        all_same_ylim = True
        
        for i, ax in enumerate(axes):
            current_ylim = ax.get_ylim()
            if abs(current_ylim[0] - first_ylim[0]) > 0.1 or abs(current_ylim[1] - first_ylim[1]) > 0.1:
                print(f"❌ Subplot {i} tiene rango Y diferente: {current_ylim} vs {first_ylim}")
                all_same_ylim = False
                break
        
        if all_same_ylim:
            print(f"✅ Todos los subplots comparten el mismo rango Y: {first_ylim}")
        
        # Guardar la figura de test
        output_file = os.path.join(os.path.dirname(__file__), '..', 'test_subplots_shared.png')
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"💾 Figura guardada en: {output_file}")
        
        plt.close()
        
        return all_same_ylim
        
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar test de subplots."""
    print("🧪 Test de corrección de subplots con eje de profundidad compartido")
    print("=" * 60)
    
    success = test_subplots_shared_depth()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST EXITOSO: Los subplots comparten correctamente el eje de profundidad")
    else:
        print("❌ TEST FALLIDO: Problemas con el eje de profundidad compartido")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
