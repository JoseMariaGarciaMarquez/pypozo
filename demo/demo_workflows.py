#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Workflows System
====================

Demostración del sistema de workflows petrofísicos automatizados.
"""

import sys
import numpy as np
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def create_synthetic_well():
    """Crear un pozo sintético para pruebas."""
    
    # Crear datos sintéticos realistas
    depth = np.arange(1000, 1500, 0.5)  # 1000 metros de profundidad
    n_points = len(depth)
    
    # GR: base + ruido + tendencias
    gr_base = 50
    gr_noise = np.random.normal(0, 15, n_points)
    gr_trend = 30 * np.sin(np.linspace(0, 4*np.pi, n_points))  # Capas
    gr = gr_base + gr_noise + gr_trend
    gr = np.clip(gr, 10, 200)  # Rango físico
    
    # RHOB: densidad realista
    rhob_base = 2.3
    rhob_noise = np.random.normal(0, 0.1, n_points)
    rhob_vcl_effect = -0.3 * (gr - 50) / 100  # Efecto arcilla
    rhob = rhob_base + rhob_noise + rhob_vcl_effect
    rhob = np.clip(rhob, 1.8, 2.8)
    
    # NPHI: neutrón
    nphi_base = 0.15
    nphi_noise = np.random.normal(0, 0.03, n_points)
    nphi_vcl_effect = 0.2 * (gr - 50) / 100  # Efecto arcilla
    nphi = nphi_base + nphi_noise + nphi_vcl_effect
    nphi = np.clip(nphi, 0, 0.5)
    
    # Crear objeto similar a WellManager para pruebas
    class MockWellManager:
        def __init__(self):
            self.name = "POZO_SINTETICO_DEMO"
            self.curves = ["DEPTH", "GR", "RHOB", "NPHI"]
            self.data = {
                "DEPTH": depth,
                "GR": gr,
                "RHOB": rhob,
                "NPHI": nphi
            }
            self.added_curves = {}
        
        def get_curve_data(self, curve_name):
            if curve_name in self.data:
                return self.data[curve_name]
            elif curve_name in self.added_curves:
                return self.added_curves[curve_name]
            else:
                raise KeyError(f"Curva {curve_name} no encontrada")
        
        def add_curve(self, curve_name, data):
            self.added_curves[curve_name] = data
            if curve_name not in self.curves:
                self.curves.append(curve_name)
            print(f"  ✅ Curva agregada: {curve_name} (μ={np.nanmean(data):.3f})")
    
    return MockWellManager()

def demo_workflow_manager():
    """Demostrar el sistema de gestión de workflows."""
    
    print("🚀 Demo del Sistema de Workflows")
    print("=" * 50)
    
    try:
        # Importar sistema de workflows
        from pypozo.workflows import WorkflowManager
        
        # Crear gestor
        manager = WorkflowManager()
        print("✅ WorkflowManager creado")
        
        # Mostrar workflows disponibles
        available = manager.get_available_workflows()
        print(f"\n📋 Workflows Disponibles ({len(available)}):")
        for key, info in available.items():
            print(f"  🔸 {key}: {info['name']}")
            print(f"     📝 {info['description']}")
            print(f"     📊 Requiere: {info['required_curves']}")
            print(f"     📈 Genera: {info['output_curves']}")
            print(f"     🔢 Pasos: {info['total_steps']}")
            print()
        
        # Crear pozo sintético
        print("🏗️ Creando pozo sintético...")
        well = create_synthetic_well()
        print(f"✅ Pozo creado: {well.name}")
        print(f"   Curvas: {well.curves}")
        print(f"   Puntos: {len(well.get_curve_data('DEPTH'))}")
        
        # Validar workflows para el pozo
        print("\n🔍 Validando workflows para el pozo:")
        for workflow_type in available.keys():
            validation = manager.validate_well_for_workflow(well, workflow_type)
            status = "✅" if validation['is_valid'] else "❌"
            print(f"  {status} {workflow_type}: {validation['workflow_name']}")
            if validation['missing_curves']:
                print(f"      Faltan: {validation['missing_curves']}")
        
        # Obtener recomendaciones
        print("\n💡 Recomendaciones de workflows:")
        recommendations = manager.get_workflow_recommendations(well)
        for rec in recommendations:
            status = "🎯" if rec['can_execute'] else "⚠️"
            print(f"  {status} {rec['workflow_name']} (Compatibilidad: {rec['compatibility']:.1%})")
            if rec['missing_curves']:
                print(f"      Faltan: {rec['missing_curves']}")
        
        # Ejecutar workflow básico
        print("\n🚀 Ejecutando Workflow Básico de Petrofísica...")
        
        def progress_callback(percent, step_name):
            print(f"  📊 Progreso: {percent:3d}% - {step_name}")
        
        # Ejecutar
        results = manager.execute_workflow(
            "basic_petrophysics",
            well,
            progress_callback=progress_callback,
            save_results=True
        )
        
        print(f"\n✅ Workflow completado!")
        print(f"   Pasos ejecutados: {len(results)}")
        print(f"   Curvas generadas: {len(well.added_curves)}")
        
        # Mostrar resumen de resultados
        print("\n📊 Resumen de Resultados:")
        for step_name, step_results in results.items():
            print(f"  🔸 {step_name}:")
            if isinstance(step_results, dict):
                for key, value in step_results.items():
                    if isinstance(value, dict) and 'statistics' in value:
                        stats = value['statistics']
                        print(f"    📈 {key}: μ={stats['mean']:.3f}, σ={stats['std']:.3f}")
        
        # Mostrar curvas finales
        print(f"\n📋 Curvas finales del pozo:")
        print(f"   Originales: {list(well.data.keys())}")
        print(f"   Generadas: {list(well.added_curves.keys())}")
        
        # Historial de ejecuciones
        history = manager.get_execution_history()
        print(f"\n📚 Historial: {len(history)} ejecuciones guardadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar demo completo."""
    print("🔬 PyPozo 2.0 - Sistema de Workflows Automatizados")
    print("=" * 60)
    
    success = demo_workflow_manager()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡Demo completado exitosamente!")
        print("\n🚀 Sistema de workflows implementado:")
        print("  ✅ 4 Templates predefinidos")
        print("  ✅ Gestión automática de workflows")
        print("  ✅ Validación de pozos")
        print("  ✅ Sistema de recomendaciones")
        print("  ✅ Seguimiento de progreso")
        print("  ✅ Exportación de resultados")
        print("  ✅ Historial de ejecuciones")
        print("\n📋 Templates disponibles:")
        print("  🔸 Petrofísica Básica (VCL + PHIE)")
        print("  🔸 Análisis de Areniscas")
        print("  🔸 Análisis de Carbonatos")
        print("  🔸 Optimización de Completación")
        
    else:
        print("❌ Demo falló. Revisar errores arriba.")

if __name__ == "__main__":
    main()
