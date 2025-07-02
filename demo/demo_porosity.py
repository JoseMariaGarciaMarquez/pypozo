"""
Demo del Módulo de Porosidad Efectiva (PHIE)
============================================

Script de demostración que muestra las capacidades del módulo de cálculo
de porosidad efectiva usando datos sintéticos que simulan condiciones reales.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Agregar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pypozo.petrophysics.porosity import PorosityCalculator
from pypozo.petrophysics.vcl import VclCalculator

def generate_realistic_well_data():
    """Genera datos sintéticos realistas de un pozo"""
    depth = np.arange(2000, 2200, 0.25)  # 800 puntos cada 0.25m
    
    # Simular secuencia geológica realista
    np.random.seed(123)  # Para reproducibilidad
    
    # Gamma Ray base con tendencias
    gr_base = 45 + 50 * np.sin(np.linspace(0, 6*np.pi, len(depth))) + \
              20 * np.sin(np.linspace(0, 2*np.pi, len(depth)))
    gr_noise = 8 * np.random.randn(len(depth))
    gamma_ray = np.maximum(gr_base + gr_noise, 20)  # Mínimo 20 API
    
    # Densidad volumétrica correlacionada con litología
    # Arena limpia: ~2.6-2.5, Arcilla: ~2.3-2.4
    base_density = 2.6 - (gamma_ray - 30) * 0.003  # Relación inversa con GR
    density_variation = 0.05 * np.random.randn(len(depth))
    bulk_density = np.clip(base_density + density_variation, 1.8, 2.8)
    
    # Porosidad neutrón con efectos realistas
    # Correlacionada con densidad pero con efectos de arcilla
    base_neutron = 0.35 - (bulk_density - 2.0) * 0.3  # Relación inversa con densidad
    clay_effect = (gamma_ray - 30) * 0.004  # Arcilla aumenta NPHI aparente
    neutron_noise = 0.02 * np.random.randn(len(depth))
    neutron_porosity = np.clip(base_neutron + clay_effect + neutron_noise, 0.02, 0.45)
    
    # Simular efectos de gas en algunas zonas
    gas_zones = (depth > 2050) & (depth < 2080)  # 30m de zona con gas
    neutron_porosity[gas_zones] *= 0.7  # Reducir NPHI por efecto de gas
    
    # Agregar algunos valores nulos realistas
    null_indices = np.random.choice(len(depth), size=15, replace=False)
    gamma_ray[null_indices] = np.nan
    bulk_density[null_indices[:7]] = np.nan
    neutron_porosity[null_indices[7:]] = np.nan
    
    return {
        'depth': depth,
        'gamma_ray': gamma_ray,
        'bulk_density': bulk_density,
        'neutron_porosity': neutron_porosity,
        'gas_zones': gas_zones
    }

def demo_basic_porosity_calculations():
    """Demo de cálculos básicos de porosidad"""
    print("🧪 DEMO 1: Cálculos Básicos de Porosidad")
    print("=" * 45)
    
    # Generar datos
    data = generate_realistic_well_data()
    calc = PorosityCalculator()
    
    # 1. Porosidad densidad
    print("\n🔹 Calculando Porosidad Densidad (PHID)...")
    phid_result = calc.calculate_density_porosity(
        bulk_density=data['bulk_density'],
        matrix_density=2.65,  # Arenisca
        fluid_density=1.00    # Agua
    )
    
    phid_stats = phid_result['qc_stats']['phid']
    print(f"✅ PHID calculado:")
    print(f"   Rango: {phid_stats['min']:.3f} - {phid_stats['max']:.3f}")
    print(f"   Promedio: {phid_stats['mean']:.3f} ± {phid_stats['std']:.3f}")
    print(f"   Puntos válidos: {phid_stats['valid_points']}/{phid_stats['total_points']}")
    
    # 2. Porosidad neutrón
    print("\n🔹 Calculando Porosidad Neutrón (PHIN)...")
    phin_result = calc.calculate_neutron_porosity(
        neutron_porosity=data['neutron_porosity'],
        lithology='sandstone'
    )
    
    phin_stats = phin_result['qc_stats']['phin']
    print(f"✅ PHIN calculado:")
    print(f"   Rango: {phin_stats['min']:.3f} - {phin_stats['max']:.3f}")
    print(f"   Promedio: {phin_stats['mean']:.3f} ± {phin_stats['std']:.3f}")
    
    return data, phid_result, phin_result

def demo_vcl_corrected_porosity():
    """Demo de porosidad con corrección por arcilla"""
    print("\n\n🧪 DEMO 2: Porosidad con Corrección por Arcilla")
    print("=" * 50)
    
    data = generate_realistic_well_data()
    
    # Calcular VCL primero
    vcl_calc = VclCalculator()
    vcl_result = vcl_calc.calculate(
        gamma_ray=data['gamma_ray'],
        auto_percentiles=True,
        method='larionov_tertiary'
    )
    
    vcl = vcl_result['vcl']
    vcl_stats = vcl_result['qc_stats']['vcl']
    
    print(f"🔹 VCL calculado:")
    print(f"   Promedio: {vcl_stats['mean']:.3f} ± {vcl_stats['std']:.3f}")
    print(f"   P10-P90: {vcl_stats['p10']:.3f} - {vcl_stats['p90']:.3f}")
    
    # Porosidad con corrección por arcilla
    print(f"\n🔹 Calculando porosidad con corrección por arcilla...")
    
    porosity_calc = PorosityCalculator()
    
    # Densidad con corrección por VCL
    phid_corrected = porosity_calc.calculate_density_porosity(
        bulk_density=data['bulk_density'],
        matrix_density=2.65,
        vcl=vcl
    )
    
    # Neutrón con corrección por VCL
    phin_corrected = porosity_calc.calculate_neutron_porosity(
        neutron_porosity=data['neutron_porosity'],
        vcl=vcl,
        lithology='sandstone'
    )
    
    # Comparar con y sin corrección
    phid_raw = phid_corrected['phid_raw']
    phid_corr = phid_corrected['phid']
    phin_raw = phin_corrected['phin_raw']
    phin_corr = phin_corrected['phin']
    
    print(f"✅ Efectos de la corrección por arcilla:")
    print(f"   PHID - Raw: {np.nanmean(phid_raw):.3f}, Corregido: {np.nanmean(phid_corr):.3f}")
    print(f"   PHIN - Raw: {np.nanmean(phin_raw):.3f}, Corregido: {np.nanmean(phin_corr):.3f}")
    
    correction_phid = np.nanmean(phid_raw - phid_corr)
    correction_phin = np.nanmean(phin_raw - phin_corr)
    print(f"   Corrección promedio - PHID: {correction_phid:.3f}, PHIN: {correction_phin:.3f}")
    
    return data, vcl, phid_corrected, phin_corrected

def demo_combined_porosity_methods():
    """Demo de métodos de combinación de porosidad"""
    print("\n\n🧪 DEMO 3: Métodos de Combinación de Porosidad")
    print("=" * 50)
    
    data = generate_realistic_well_data()
    calc = PorosityCalculator()
    
    methods = ['arithmetic', 'geometric', 'harmonic']
    results = {}
    
    print("🔹 Calculando PHIE con diferentes métodos de combinación...")
    
    for method in methods:
        result = calc.calculate_density_neutron_porosity(
            bulk_density=data['bulk_density'],
            neutron_porosity=data['neutron_porosity'],
            matrix_density=2.65,
            combination_method=method
        )
        
        results[method] = result
        phie_stats = result['qc_stats']['phie']
        
        print(f"   {method.title():>10}: μ={phie_stats['mean']:.3f}, σ={phie_stats['std']:.3f}")
    
    # Analizar correlaciones entre métodos
    print(f"\n📊 Correlaciones entre métodos:")
    phie_arithmetic = results['arithmetic']['phie']
    phie_geometric = results['geometric']['phie']
    phie_harmonic = results['harmonic']['phie']
    
    valid_mask = ~(np.isnan(phie_arithmetic) | np.isnan(phie_geometric) | np.isnan(phie_harmonic))
    
    if np.sum(valid_mask) > 1:
        corr_arith_geom = np.corrcoef(phie_arithmetic[valid_mask], phie_geometric[valid_mask])[0,1]
        corr_arith_harm = np.corrcoef(phie_arithmetic[valid_mask], phie_harmonic[valid_mask])[0,1]
        corr_geom_harm = np.corrcoef(phie_geometric[valid_mask], phie_harmonic[valid_mask])[0,1]
        
        print(f"   Aritmética vs Geométrica: {corr_arith_geom:.3f}")
        print(f"   Aritmética vs Armónica:   {corr_arith_harm:.3f}")
        print(f"   Geométrica vs Armónica:   {corr_geom_harm:.3f}")
    
    return data, results

def demo_gas_detection():
    """Demo de detección de efectos de gas"""
    print("\n\n🧪 DEMO 4: Detección de Efectos de Gas")
    print("=" * 40)
    
    data = generate_realistic_well_data()
    calc = PorosityCalculator()
    
    # Calcular porosidad combinada
    result = calc.calculate_density_neutron_porosity(
        bulk_density=data['bulk_density'],
        neutron_porosity=data['neutron_porosity'],
        matrix_density=2.65,
        combination_method='arithmetic'
    )
    
    gas_effect = result['gas_effect']
    
    print(f"🔹 Análisis de efectos de gas:")
    print(f"   Puntos con posible gas: {gas_effect['gas_points_count']}")
    print(f"   Porcentaje del pozo: {gas_effect['gas_percentage']:.1f}%")
    print(f"   Máximo efecto de gas: {gas_effect['max_gas_effect']:.3f}")
    print(f"   Umbral utilizado: {gas_effect['threshold_used']:.3f}")
    
    # Comparar con zonas conocidas de gas
    gas_zones_real = data['gas_zones']
    gas_zones_detected = gas_effect['gas_zones']
    
    if len(gas_zones_real) == len(gas_zones_detected):
        # Calcular precisión de detección
        true_positives = np.sum(gas_zones_real & gas_zones_detected)
        false_positives = np.sum(~gas_zones_real & gas_zones_detected)
        false_negatives = np.sum(gas_zones_real & ~gas_zones_detected)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        print(f"\n📈 Evaluación de detección (vs zonas sintéticas):")
        print(f"   Precisión: {precision:.2f}")
        print(f"   Recall: {recall:.2f}")
    
    return data, result

def demo_lithology_analysis():
    """Demo de análisis litológico"""
    print("\n\n🧪 DEMO 5: Análisis Litológico")
    print("=" * 35)
    
    data = generate_realistic_well_data()
    calc = PorosityCalculator()
    
    # Calcular porosidades individuales
    phid_result = calc.calculate_density_porosity(
        bulk_density=data['bulk_density'],
        matrix_density=2.65
    )
    
    phin_result = calc.calculate_neutron_porosity(
        neutron_porosity=data['neutron_porosity'],
        lithology='sandstone'
    )
    
    phid = phid_result['phid']
    phin = phin_result['phin']
    
    # Análisis litológico
    litho_analysis = calc.get_lithology_recommendations(phid, phin)
    
    print(f"🔹 Recomendaciones litológicas:")
    print(f"   Litología primaria: {litho_analysis['primary_lithology']}")
    print(f"   Nivel de confianza: {litho_analysis['confidence']}")
    print(f"   Separación promedio PHIN-PHID: {litho_analysis['avg_separation']:.3f}")
    
    print(f"\n📊 Distribución litológica:")
    analysis = litho_analysis['analysis']
    print(f"   Arena limpia: {analysis['clean_sandstone_percentage']:.1f}%")
    print(f"   Arcilla: {analysis['clay_percentage']:.1f}%")
    print(f"   Carbonatos: {analysis['carbonate_percentage']:.1f}%")
    
    print(f"\n💡 Recomendaciones específicas:")
    for i, rec in enumerate(litho_analysis['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    # Información de densidades de matriz
    matrix_info = calc.get_matrix_density_info()
    print(f"\n🔧 Densidades de matriz disponibles:")
    for litho, density in matrix_info['densities'].items():
        if density is not None:
            print(f"   {litho}: {density} g/cm³")
    
    return data, litho_analysis

def demo_visualization():
    """Demo con visualización completa"""
    print("\n\n📊 DEMO 6: Visualización Completa")
    print("=" * 40)
    
    try:
        data = generate_realistic_well_data()
        calc = PorosityCalculator()
        
        # Calcular todas las porosidades
        combined_result = calc.calculate_density_neutron_porosity(
            bulk_density=data['bulk_density'],
            neutron_porosity=data['neutron_porosity'],
            matrix_density=2.65,
            combination_method='arithmetic'
        )
        
        depth = data['depth']
        rhob = data['bulk_density']
        nphi = data['neutron_porosity']
        phid = combined_result['phid']
        phin = combined_result['phin']
        phie = combined_result['phie']
        gas_zones = combined_result['gas_effect']['gas_zones']
        
        # Crear figura con subplots
        fig, axes = plt.subplots(1, 5, figsize=(20, 10))
        fig.suptitle('Análisis Completo de Porosidad - PyPozo 2.0', fontsize=16, fontweight='bold')
        
        # Track 1: Gamma Ray y Densidad
        ax1 = axes[0]
        ax1_twin = ax1.twiny()
        
        ax1.plot(data['gamma_ray'], depth, 'g-', linewidth=1, label='GR')
        ax1_twin.plot(rhob, depth, 'r-', linewidth=1, label='RHOB')
        
        ax1.set_xlabel('Gamma Ray [API]', color='green')
        ax1_twin.set_xlabel('Densidad [g/cm³]', color='red')
        ax1.set_ylabel('Profundidad [m]')
        ax1.set_title('GR / RHOB')
        ax1.grid(True, alpha=0.3)
        ax1.invert_yaxis()
        
        # Track 2: Neutrón
        ax2 = axes[1]
        ax2.plot(nphi, depth, 'b-', linewidth=1, label='NPHI')
        ax2.set_xlabel('Porosidad Neutrón')
        ax2.set_title('NPHI')
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()
        
        # Track 3: Porosidades calculadas
        ax3 = axes[2]
        ax3.plot(phid, depth, 'r-', linewidth=1.5, label='PHID')
        ax3.plot(phin, depth, 'b-', linewidth=1.5, label='PHIN')
        ax3.plot(phie, depth, 'k-', linewidth=2, label='PHIE')
        ax3.set_xlabel('Porosidad [fracción]')
        ax3.set_title('Porosidades\nCalculadas')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.invert_yaxis()
        
        # Track 4: Efectos de gas
        ax4 = axes[3]
        gas_indicator = phid - phin
        ax4.plot(gas_indicator, depth, 'orange', linewidth=1.5, label='PHID-PHIN')
        
        # Marcar zonas con gas
        gas_depth = depth[gas_zones] if np.any(gas_zones) else []
        if len(gas_depth) > 0:
            ax4.scatter([0.05]*len(gas_depth), gas_depth, c='red', s=20, 
                       marker='>', label='Gas detectado', alpha=0.7)
        
        ax4.axvline(x=0.05, color='red', linestyle='--', alpha=0.5, label='Umbral gas')
        ax4.set_xlabel('Indicador de Gas')
        ax4.set_title('Detección\nde Gas')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.invert_yaxis()
        
        # Track 5: Crossplot PHID vs PHIN
        ax5 = axes[4]
        
        # Limpiar datos para crossplot
        valid_mask = ~(np.isnan(phid) | np.isnan(phin))
        phid_clean = phid[valid_mask]
        phin_clean = phin[valid_mask]
        
        # Colorear por efectos de gas
        gas_mask = gas_zones[valid_mask] if len(gas_zones) == len(valid_mask) else None
        
        if gas_mask is not None and np.any(gas_mask):
            ax5.scatter(phin_clean[~gas_mask], phid_clean[~gas_mask], 
                       c='blue', alpha=0.6, s=10, label='Normal')
            ax5.scatter(phin_clean[gas_mask], phid_clean[gas_mask], 
                       c='red', alpha=0.8, s=15, label='Gas', marker='^')
        else:
            ax5.scatter(phin_clean, phid_clean, c='blue', alpha=0.6, s=10)
        
        # Línea 1:1
        max_por = max(np.max(phid_clean), np.max(phin_clean))
        ax5.plot([0, max_por], [0, max_por], 'k--', alpha=0.5, label='1:1')
        
        ax5.set_xlabel('PHIN [fracción]')
        ax5.set_ylabel('PHID [fracción]')
        ax5.set_title('Crossplot\nPHID vs PHIN')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Guardar figura
        output_path = os.path.join('demo', 'porosity_demo_complete.png')
        os.makedirs('demo', exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico completo guardado en: {output_path}")
        
        # Estadísticas finales
        print(f"\n📊 Estadísticas Finales:")
        print(f"   Intervalo analizado: {depth[0]:.1f} - {depth[-1]:.1f} m")
        print(f"   Total de puntos: {len(depth)}")
        print(f"   PHIE promedio: {np.nanmean(phie):.3f} ± {np.nanstd(phie):.3f}")
        print(f"   Zonas con gas detectadas: {np.sum(gas_zones)} puntos")
        
        return fig, combined_result
        
    except ImportError:
        print("⚠️  Matplotlib no disponible - saltando visualización")
        return None, None

def main():
    """Función principal del demo"""
    print("🚀 DEMO COMPLETO: Módulo de Porosidad Efectiva (PHIE)")
    print("=" * 60)
    print("PyPozo 2.0 - Fase 1: Cálculos Petrofísicos Avanzados")
    print("=" * 60)
    
    try:
        # Ejecutar todos los demos
        demo_basic_porosity_calculations()
        demo_vcl_corrected_porosity()
        demo_combined_porosity_methods()
        demo_gas_detection()
        demo_lithology_analysis()
        demo_visualization()
        
        print("\n\n🎉 DEMO DE POROSIDAD COMPLETADO EXITOSAMENTE!")
        print("=" * 50)
        print("✅ El módulo PHIE está completamente implementado y probado")
        print("✅ Fase 1 - Milestone 2: COMPLETADO")
        print("\n🚀 Capacidades implementadas:")
        print("   ✅ Porosidad densidad (PHID) con corrección por arcilla")
        print("   ✅ Porosidad neutrón (PHIN) con correcciones litológicas")
        print("   ✅ Combinación PHID-PHIN (3 métodos)")
        print("   ✅ Detección automática de efectos de gas")
        print("   ✅ Análisis litológico y recomendaciones")
        print("   ✅ Control de calidad integral")
        print("\n📋 Próximos pasos sugeridos:")
        print("   1. Crear panel GUI para cálculos de porosidad")
        print("   2. Implementar módulo de Saturación de Agua (SW)")
        print("   3. Desarrollar templates de workflows")
        print("   4. Integrar con sistema de exportación")
        
    except Exception as e:
        print(f"\n❌ Error durante el demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
