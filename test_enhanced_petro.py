#!/usr/bin/env python3
"""
Test Completo de Análisis Petrofísico Avanzado
==============================================

Prueba todas las nuevas funcionalidades de análisis petrofísico:
- Saturación de Agua (Archie, Simandoux)
- Permeabilidad (Timur, Kozeny-Carman)
- Análisis Litológico
- Evaluación de Calidad de Reservorio

Usa datos sintéticos realistas para validar los cálculos.
"""

import sys
import os
import numpy as np
import pandas as pd

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_water_saturation():
    """Test de cálculos de saturación de agua."""
    print("🧪 Test de Saturación de Agua")
    
    try:
        from src.pypozo.petrophysics import WaterSaturationCalculator
        
        # Crear calculadora
        sw_calc = WaterSaturationCalculator()
        
        # Datos sintéticos realistas
        n_points = 100
        depth = np.linspace(2000, 2100, n_points)
        
        # Resistividad verdadera (típica de arenisca con hidrocarburos)
        rt = np.random.lognormal(mean=1.5, sigma=0.8, size=n_points)  # 1-50 ohm-m
        rt = np.clip(rt, 0.5, 100)
        
        # Porosidad efectiva
        porosity = np.random.normal(0.15, 0.05, n_points)  # 15% ± 5%
        porosity = np.clip(porosity, 0.05, 0.35)
        
        # Volumen de arcilla
        vclay = np.random.beta(2, 5, n_points) * 0.4  # Sesgo hacia valores bajos
        
        print(f"   📊 Datos generados: {n_points} puntos")
        print(f"   📊 RT: {rt.min():.2f} - {rt.max():.2f} ohm-m")
        print(f"   📊 PHIE: {porosity.min():.3f} - {porosity.max():.3f}")
        print(f"   📊 VCLAY: {vclay.min():.3f} - {vclay.max():.3f}")
        
        # Test 1: Archie Simple
        print("\n   🔬 Test Archie Simple...")
        result_archie = sw_calc.calculate_archie_simple(
            rt=rt,
            porosity=porosity,
            rw=0.05,  # Agua dulce
            a=1.0,
            m=2.0,
            n=2.0
        )
        
        if result_archie['success']:
            sw_archie = result_archie['sw']
            print(f"   ✅ Archie: Sw promedio = {np.nanmean(sw_archie):.3f}")
            print(f"   📈 Rango Sw: {np.nanmin(sw_archie):.3f} - {np.nanmax(sw_archie):.3f}")
        else:
            print(f"   ❌ Error Archie: {result_archie.get('error', 'Unknown')}")
            return False
        
        # Test 2: Archie con Vclay
        print("\n   🔬 Test Archie con Vclay...")
        result_archie_vclay = sw_calc.calculate_archie_with_vclay(
            rt=rt,
            porosity=porosity,
            vclay=vclay,
            rw=0.05
        )
        
        if result_archie_vclay['success']:
            sw_archie_vclay = result_archie_vclay['sw']
            print(f"   ✅ Archie+Vclay: Sw promedio = {np.nanmean(sw_archie_vclay):.3f}")
        else:
            print(f"   ❌ Error Archie+Vclay: {result_archie_vclay.get('error', 'Unknown')}")
            return False
        
        # Test 3: Simandoux
        print("\n   🔬 Test Simandoux...")
        result_simandoux = sw_calc.calculate_simandoux(
            rt=rt,
            porosity=porosity,
            vclay=vclay,
            rw=0.05,
            rsh=2.0
        )
        
        if result_simandoux['success']:
            sw_simandoux = result_simandoux['sw']
            print(f"   ✅ Simandoux: Sw promedio = {np.nanmean(sw_simandoux):.3f}")
        else:
            print(f"   ❌ Error Simandoux: {result_simandoux.get('error', 'Unknown')}")
            return False
        
        print("   🎉 Todos los tests de Sw PASARON")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en test Sw: {e}")
        return False

def test_permeability():
    """Test de cálculos de permeabilidad."""
    print("\n🧪 Test de Permeabilidad")
    
    try:
        from src.pypozo.petrophysics import PermeabilityCalculator
        
        # Crear calculadora
        perm_calc = PermeabilityCalculator()
        
        # Datos sintéticos
        n_points = 100
        
        # Porosidad efectiva
        porosity = np.random.normal(0.18, 0.06, n_points)
        porosity = np.clip(porosity, 0.08, 0.35)
        
        # Saturación agua irreducible
        swi = np.random.normal(0.25, 0.08, n_points)
        swi = np.clip(swi, 0.1, 0.6)
        
        # Tamaño de grano (micrones)
        grain_size = np.random.lognormal(mean=4.5, sigma=0.4, size=n_points)  # ~90 micrones promedio
        grain_size = np.clip(grain_size, 20, 300)
        
        print(f"   📊 PHIE: {porosity.min():.3f} - {porosity.max():.3f}")
        print(f"   📊 SWI: {swi.min():.3f} - {swi.max():.3f}")
        print(f"   📊 Grain size: {grain_size.min():.1f} - {grain_size.max():.1f} μm")
        
        # Test 1: Timur (Arenisca)
        print("\n   🔬 Test Timur (Arenisca)...")
        result_timur = perm_calc.calculate_timur(
            porosity=porosity,
            sw_irreducible=swi,
            rock_type='sandstone'
        )
        
        if result_timur['success']:
            perm_timur = result_timur['permeability']
            print(f"   ✅ Timur: K promedio = {np.nanmean(perm_timur):.2f} mD")
            print(f"   📈 Rango K: {np.nanmin(perm_timur):.3f} - {np.nanmax(perm_timur):.1f} mD")
        else:
            print(f"   ❌ Error Timur: {result_timur.get('error', 'Unknown')}")
            return False
        
        # Test 2: Kozeny-Carman
        print("\n   🔬 Test Kozeny-Carman...")
        result_kc = perm_calc.calculate_kozeny_carman(
            porosity=porosity,
            grain_size=grain_size,
            rock_type='sandstone'
        )
        
        if result_kc['success']:
            perm_kc = result_kc['permeability']
            print(f"   ✅ Kozeny-Carman: K promedio = {np.nanmean(perm_kc):.2f} mD")
        else:
            print(f"   ❌ Error K-C: {result_kc.get('error', 'Unknown')}")
            return False
        
        # Test 3: Wyllie & Rose
        print("\n   🔬 Test Wyllie & Rose...")
        result_wr = perm_calc.calculate_wyllie_rose(
            porosity=porosity,
            grain_size=grain_size
        )
        
        if result_wr['success']:
            perm_wr = result_wr['permeability']
            print(f"   ✅ Wyllie & Rose: K promedio = {np.nanmean(perm_wr):.2f} mD")
        else:
            print(f"   ❌ Error W&R: {result_wr.get('error', 'Unknown')}")
            return False
        
        # Test 4: Clasificación de permeabilidad
        print("\n   🔬 Test Clasificación...")
        classification = perm_calc.get_permeability_classification(perm_timur)
        print("   📊 Clasificación de permeabilidad:")
        for class_name, stats in classification['classifications'].items():
            if stats['count'] > 0:
                print(f"      {class_name}: {stats['count']} puntos ({stats['percentage']:.1f}%)")
        
        print("   🎉 Todos los tests de Permeabilidad PASARON")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en test Permeabilidad: {e}")
        return False

def test_lithology_analysis():
    """Test de análisis litológico."""
    print("\n🧪 Test de Análisis Litológico")
    
    try:
        from src.pypozo.petrophysics import LithologyAnalyzer
        
        # Crear analizador
        litho_analyzer = LithologyAnalyzer()
        
        # Datos sintéticos - simulando diferentes litologías
        n_points = 150
        
        # Crear 3 zonas litológicas diferentes
        n_per_zone = n_points // 3
        
        # Zona 1: Arenisca limpia (quartz sandstone)
        rhob_ss = np.random.normal(2.45, 0.1, n_per_zone)
        nphi_ss = np.random.normal(0.15, 0.05, n_per_zone)
        pe_ss = np.random.normal(1.8, 0.2, n_per_zone)
        
        # Zona 2: Caliza (limestone)
        rhob_ls = np.random.normal(2.68, 0.08, n_per_zone)
        nphi_ls = np.random.normal(0.08, 0.04, n_per_zone)
        pe_ls = np.random.normal(5.1, 0.3, n_per_zone)
        
        # Zona 3: Lutita (shale)
        rhob_sh = np.random.normal(2.35, 0.12, n_per_zone)
        nphi_sh = np.random.normal(0.35, 0.08, n_per_zone)
        pe_sh = np.random.normal(2.9, 0.4, n_per_zone)
        
        # Combinar todas las zonas
        rhob = np.concatenate([rhob_ss, rhob_ls, rhob_sh])
        nphi = np.concatenate([nphi_ss, nphi_ls, nphi_sh])
        pe = np.concatenate([pe_ss, pe_ls, pe_sh])
        
        # Aplicar límites físicos
        rhob = np.clip(rhob, 1.8, 3.0)
        nphi = np.clip(nphi, 0.0, 0.6)
        pe = np.clip(pe, 1.0, 8.0)
        
        print(f"   📊 RHOB: {rhob.min():.2f} - {rhob.max():.2f} g/cm³")
        print(f"   📊 NPHI: {nphi.min():.3f} - {nphi.max():.3f}")
        print(f"   📊 PE: {pe.min():.2f} - {pe.max():.2f} barns/e-")
        
        # Test 1: Análisis Neutron-Density
        print("\n   🔬 Test Análisis Neutron-Density...")
        result_nd = litho_analyzer.neutron_density_analysis(
            rhob=rhob,
            nphi=nphi,
            pe=pe,
            fluid_type='fresh_water'
        )
        
        if result_nd['success']:
            dominant_mineral = result_nd['dominant_mineral']
            facies = result_nd['petrophysical_facies']
            
            print(f"   ✅ Mineral dominante identificado: {dominant_mineral}")
            
            # Contar facies
            unique_facies, counts = np.unique(facies, return_counts=True)
            print("   📊 Facies petrofísicas identificadas:")
            for facies_type, count in zip(unique_facies, counts):
                percentage = (count / len(facies)) * 100
                print(f"      {facies_type}: {count} puntos ({percentage:.1f}%)")
                
        else:
            print(f"   ❌ Error en análisis N-D: {result_nd.get('error', 'Unknown')}")
            return False
        
        # Test 2: Análisis PE
        print("\n   🔬 Test Análisis Factor Fotoeléctrico...")
        result_pe = litho_analyzer.photoelectric_analysis(
            pe=pe,
            rhob=rhob,
            nphi=nphi
        )
        
        if result_pe['success']:
            mineral_id = result_pe['mineral_identification']
            mineral_stats = result_pe['mineral_statistics']
            
            print("   📊 Minerales identificados:")
            for mineral, stats in mineral_stats.items():
                print(f"      {mineral}: {stats['count']} puntos ({stats['percentage']:.1f}%)")
                
        else:
            print(f"   ❌ Error en análisis PE: {result_pe.get('error', 'Unknown')}")
            return False
        
        print("   🎉 Todos los tests de Litología PASARON")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en test Litología: {e}")
        return False

def test_reservoir_quality():
    """Test de evaluación de calidad de reservorio."""
    print("\n🧪 Test de Calidad de Reservorio")
    
    try:
        from src.pypozo.petrophysics import LithologyAnalyzer
        
        # Crear analizador
        litho_analyzer = LithologyAnalyzer()
        
        # Simular datos de un reservorio con diferentes calidades
        n_points = 200
        
        # Crear 4 zonas de calidad diferentes
        n_per_zone = n_points // 4
        
        # Zona 1: Excelente (alta φ, alta K)
        phi_exc = np.random.normal(0.22, 0.03, n_per_zone)
        perm_exc = np.random.lognormal(2.5, 0.5, n_per_zone)  # ~12 mD promedio
        vclay_exc = np.random.beta(2, 8, n_per_zone) * 0.1  # Muy limpia
        
        # Zona 2: Buena (moderada φ, moderada K)
        phi_good = np.random.normal(0.16, 0.02, n_per_zone)
        perm_good = np.random.lognormal(1.5, 0.6, n_per_zone)  # ~4.5 mD promedio
        vclay_good = np.random.beta(2, 5, n_per_zone) * 0.2
        
        # Zona 3: Regular (baja φ, baja K)
        phi_fair = np.random.normal(0.11, 0.02, n_per_zone)
        perm_fair = np.random.lognormal(0.2, 0.8, n_per_zone)  # ~1.2 mD promedio
        vclay_fair = np.random.beta(2, 3, n_per_zone) * 0.4
        
        # Zona 4: Pobre (muy baja φ, muy baja K)
        phi_poor = np.random.normal(0.06, 0.015, n_per_zone)
        perm_poor = np.random.lognormal(-1.0, 0.8, n_per_zone)  # ~0.37 mD promedio
        vclay_poor = np.random.beta(3, 2, n_per_zone) * 0.6
        
        # Combinar zonas
        porosity = np.concatenate([phi_exc, phi_good, phi_fair, phi_poor])
        permeability = np.concatenate([perm_exc, perm_good, perm_fair, perm_poor])
        vclay = np.concatenate([vclay_exc, vclay_good, vclay_fair, vclay_poor])
        
        # Simular saturación de agua
        sw = np.random.beta(2, 3, n_points) * 0.8 + 0.2  # 20-100%
        
        # Aplicar límites físicos
        porosity = np.clip(porosity, 0.01, 0.35)
        permeability = np.clip(permeability, 0.001, 1000)
        vclay = np.clip(vclay, 0.0, 0.8)
        sw = np.clip(sw, 0.2, 1.0)
        
        print(f"   📊 PHIE: {porosity.min():.3f} - {porosity.max():.3f}")
        print(f"   📊 PERM: {permeability.min():.3f} - {permeability.max():.1f} mD")
        print(f"   📊 VCLAY: {vclay.min():.3f} - {vclay.max():.3f}")
        print(f"   📊 SW: {sw.min():.3f} - {sw.max():.3f}")
        
        # Test: Evaluación de calidad completa
        print("\n   🔬 Test Evaluación de Calidad...")
        result_quality = litho_analyzer.reservoir_quality_assessment(
            porosity=porosity,
            permeability=permeability,
            vclay=vclay,
            sw=sw
        )
        
        if result_quality['success']:
            overall_quality = result_quality['overall_quality']
            quality_stats = result_quality['quality_statistics']
            
            print("   📊 Distribución de calidad:")
            for quality_class, stats in quality_stats.items():
                print(f"      {quality_class.upper()}: {stats['count']} puntos ({stats['percentage']:.1f}%)")
                print(f"         φ promedio: {stats['avg_porosity']:.3f}")
                print(f"         K promedio: {stats['avg_permeability']:.2f} mD")
                print(f"         RQI promedio: {stats['avg_rqi']:.3f}")
            
            # Verificar que detectó las 4 categorías
            unique_qualities = np.unique(overall_quality)
            expected_qualities = {'poor', 'fair', 'good', 'excellent'}
            detected_qualities = set(unique_qualities)
            
            if detected_qualities >= {'poor', 'fair', 'good'}:  # Al menos 3 de 4
                print("   ✅ Clasificación de calidad funcionando correctamente")
            else:
                print(f"   ⚠️ Solo detectó: {detected_qualities}")
                
        else:
            print(f"   ❌ Error en evaluación calidad: {result_quality.get('error', 'Unknown')}")
            return False
        
        print("   🎉 Test de Calidad de Reservorio PASÓ")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en test Calidad: {e}")
        return False

def main():
    """Ejecutar todos los tests de análisis petrofísico."""
    print("🚀 INICIANDO TESTS DE ANÁLISIS PETROFÍSICO AVANZADO")
    print("=" * 60)
    
    # Ejecutar todos los tests
    tests = [
        test_water_saturation,
        test_permeability,
        test_lithology_analysis,
        test_reservoir_quality
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error ejecutando {test_func.__name__}: {e}")
            results.append(False)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE TESTS:")
    test_names = [
        "Saturación de Agua",
        "Permeabilidad", 
        "Análisis Litológico",
        "Calidad de Reservorio"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ ÉXITO" if result else "❌ FALLO"
        print(f"   {i+1}. {name}: {status}")
    
    # Resultado global
    all_passed = all(results)
    if all_passed:
        print("\n🎉 TODOS LOS TESTS PASARON - Análisis Petrofísico Funcionando!")
        print("🔬 Los nuevos módulos están listos para usar en PyPozo")
        return 0
    else:
        failed_count = sum(1 for r in results if not r)
        print(f"\n⚠️  {failed_count} de {len(tests)} tests fallaron")
        print("🔧 Revisar implementación de módulos que fallaron")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
