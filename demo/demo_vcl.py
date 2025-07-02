"""
Demo del Módulo de Volumen de Arcilla (VCL)
===========================================

Script de demostración que muestra las capacidades del nuevo módulo
de cálculo de VCL usando datos sintéticos y reales.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Agregar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pypozo.petrophysics.vcl import VclCalculator

def generate_synthetic_data():
    """Genera datos sintéticos de Gamma Ray para demo"""
    depth = np.arange(1000, 1200, 0.5)  # 400 puntos cada 0.5m
    
    # Crear litología sintética variada
    gr = np.zeros_like(depth)
    
    # Arena limpia (1000-1050m)
    mask1 = (depth >= 1000) & (depth < 1050)
    gr[mask1] = 25 + 10 * np.random.random(np.sum(mask1))
    
    # Arena arcillosa (1050-1100m)  
    mask2 = (depth >= 1050) & (depth < 1100)
    gr[mask2] = 50 + 30 * np.random.random(np.sum(mask2))
    
    # Arcilla (1100-1150m)
    mask3 = (depth >= 1100) & (depth < 1150)
    gr[mask3] = 120 + 40 * np.random.random(np.sum(mask3))
    
    # Transición (1150-1200m)
    mask4 = (depth >= 1150) & (depth <= 1200)
    transition = np.linspace(150, 40, np.sum(mask4))
    gr[mask4] = transition + 15 * np.random.random(np.sum(mask4))
    
    # Agregar algunos valores nulos para realismo
    null_indices = np.random.choice(len(gr), size=20, replace=False)
    gr[null_indices] = np.nan
    
    return depth, gr

def demo_basic_calculation():
    """Demo básico de cálculo de VCL"""
    print("🧪 DEMO 1: Cálculo Básico de VCL")
    print("=" * 40)
    
    # Crear calculadora
    calc = VclCalculator()
    
    # Generar datos sintéticos
    depth, gr = generate_synthetic_data()
    
    # Cálculo básico con método por defecto
    result = calc.calculate(
        gamma_ray=gr,
        auto_percentiles=True,
        method='larionov_tertiary'
    )
    
    # Mostrar resultados
    print(f"Método utilizado: {result['parameters']['method']}")
    print(f"GR_clean calculado: {result['parameters']['gr_clean']:.1f} API")
    print(f"GR_clay calculado: {result['parameters']['gr_clay']:.1f} API")
    print(f"Rango de GR: {result['parameters']['gr_range']:.1f} API")
    
    # Estadísticas VCL
    stats = result['qc_stats']['vcl']
    print(f"\n📊 Estadísticas VCL:")
    print(f"  Puntos válidos: {stats['valid_points']}/{stats['total_points']}")
    print(f"  Rango: {stats['min']:.3f} - {stats['max']:.3f}")
    print(f"  Promedio: {stats['mean']:.3f} ± {stats['std']:.3f}")
    print(f"  P10-P50-P90: {stats['p10']:.3f}, {stats['p50']:.3f}, {stats['p90']:.3f}")
    
    # Warnings si los hay
    if result['warnings']:
        print(f"\n⚠️  Advertencias:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    # Quality flags
    quality = result['quality_flags']
    print(f"\n🎯 Calidad del cálculo: {quality['overall_quality'].upper()}")
    
    return depth, gr, result

def demo_method_comparison():
    """Demo comparación de métodos"""
    print("\n\n🔬 DEMO 2: Comparación de Métodos")
    print("=" * 40)
    
    calc = VclCalculator()
    depth, gr = generate_synthetic_data()
    
    # Calcular con todos los métodos
    results = calc.batch_calculate(
        gamma_ray=gr,
        auto_percentiles=True
    )
    
    print("Métodos calculados:")
    for method in results:
        if method != 'comparison':
            if 'error' in results[method]:
                print(f"  ❌ {method}: {results[method]['error']}")
            else:
                stats = results[method]['qc_stats']['vcl']
                print(f"  ✅ {method}: VCL promedio = {stats['mean']:.3f}")
    
    # Mostrar correlaciones
    if 'comparison' in results:
        print(f"\n📈 Correlaciones entre métodos:")
        correlations = results['comparison']['correlations']
        for pair, corr in correlations.items():
            print(f"  {pair}: {corr:.3f}")
    
    return depth, gr, results

def demo_visualization():
    """Demo con visualización"""
    print("\n\n📊 DEMO 3: Visualización de Resultados")
    print("=" * 40)
    
    calc = VclCalculator()
    depth, gr = generate_synthetic_data()
    
    # Calcular múltiples métodos
    methods = ['linear', 'larionov_tertiary', 'clavier']
    results = calc.batch_calculate(
        gamma_ray=gr,
        methods=methods,
        auto_percentiles=True
    )
    
    # Crear figura
    fig, axes = plt.subplots(1, len(methods) + 1, figsize=(15, 8))
    fig.suptitle('Comparación de Métodos de Cálculo VCL', fontsize=14, fontweight='bold')
    
    # Plot Gamma Ray
    axes[0].plot(gr, depth, 'g-', linewidth=1, label='Gamma Ray')
    axes[0].set_xlabel('Gamma Ray [API]')
    axes[0].set_ylabel('Profundidad [m]')
    axes[0].set_title('Gamma Ray\nOriginal')
    axes[0].grid(True, alpha=0.3)
    axes[0].invert_yaxis()
    
    # Plot cada método
    colors = ['blue', 'red', 'orange']
    for i, method in enumerate(methods):
        if 'error' not in results[method]:
            vcl = results[method]['vcl']
            axes[i+1].plot(vcl, depth, color=colors[i], linewidth=1.5, label=f'VCL {method}')
            axes[i+1].set_xlabel('VCL [fracción]')
            axes[i+1].set_title(f'VCL\n{method.replace("_", " ").title()}')
            axes[i+1].grid(True, alpha=0.3)
            axes[i+1].set_xlim(0, 1)
            axes[i+1].invert_yaxis()
            
            # Agregar estadísticas como texto
            stats = results[method]['qc_stats']['vcl']
            stats_text = f"Media: {stats['mean']:.2f}\nStd: {stats['std']:.2f}"
            axes[i+1].text(0.7, depth[10], stats_text, fontsize=8, 
                          bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.7))
    
    plt.tight_layout()
    
    # Guardar figura
    output_path = os.path.join('demo', 'vcl_demo_comparison.png')
    os.makedirs('demo', exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado en: {output_path}")
    
    # Mostrar información adicional
    print(f"\n📊 Información adicional:")
    print(f"  Total de puntos analizados: {len(depth)}")
    print(f"  Rango de profundidad: {depth[0]:.1f} - {depth[-1]:.1f} m")
    
    return fig

def demo_parameter_sensitivity():
    """Demo de sensibilidad a parámetros"""
    print("\n\n🎛️  DEMO 4: Sensibilidad a Parámetros")
    print("=" * 40)
    
    calc = VclCalculator()
    depth, gr = generate_synthetic_data()
    
    # Probar diferentes combinaciones de GR_clean y GR_clay
    gr_clean_values = [25, 30, 35]
    gr_clay_values = [140, 160, 180]
    
    print("Sensibilidad a parámetros GR_clean y GR_clay:")
    print("GR_clean | GR_clay | VCL_medio | VCL_std")
    print("-" * 40)
    
    for gr_clean in gr_clean_values:
        for gr_clay in gr_clay_values:
            try:
                result = calc.calculate(
                    gamma_ray=gr,
                    gr_clean=gr_clean,
                    gr_clay=gr_clay,
                    method='larionov_tertiary',
                    auto_percentiles=False
                )
                
                stats = result['qc_stats']['vcl']
                print(f"  {gr_clean:6.0f} | {gr_clay:7.0f} | {stats['mean']:9.3f} | {stats['std']:7.3f}")
                
            except Exception as e:
                print(f"  {gr_clean:6.0f} | {gr_clay:7.0f} | ERROR: {str(e)[:20]}...")

def demo_method_info():
    """Demo información de métodos"""
    print("\n\n📚 DEMO 5: Información de Métodos Disponibles")
    print("=" * 50)
    
    calc = VclCalculator()
    info = calc.get_method_info()
    
    print("Métodos disponibles para cálculo de VCL:")
    print("-" * 50)
    
    for method in info['available_methods']:
        description = info['descriptions'][method]
        recommendation = info['recommendations'][method]
        
        print(f"\n🔹 {method.upper().replace('_', ' ')}")
        print(f"   Fórmula: {description}")
        print(f"   Uso recomendado: {recommendation}")

def main():
    """Función principal del demo"""
    print("🚀 DEMO COMPLETO: Módulo de Cálculo de Volumen de Arcilla (VCL)")
    print("="*70)
    print("PyPozo 2.0 - Fase 1: Cálculos Petrofísicos Básicos")
    print("="*70)
    
    try:
        # Ejecutar todos los demos
        depth, gr, basic_result = demo_basic_calculation()
        depth, gr, comparison_results = demo_method_comparison()
        
        # Solo mostrar gráficos si matplotlib está disponible
        try:
            fig = demo_visualization()
            print("\n💡 Tip: Revisa el archivo 'demo/vcl_demo_comparison.png' para ver los gráficos")
        except ImportError:
            print("\n⚠️  Matplotlib no disponible - saltando visualización")
        
        demo_parameter_sensitivity()
        demo_method_info()
        
        print("\n\n🎉 DEMO COMPLETADO EXITOSAMENTE!")
        print("="*40)
        print("El módulo VCL está listo para usar en PyPozo 2.0")
        print("Próximos pasos:")
        print("  1. Integrar con la GUI principal")
        print("  2. Implementar módulo de Porosidad (PHIE)")
        print("  3. Agregar exportación de resultados")
        
    except Exception as e:
        print(f"\n❌ Error durante el demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
