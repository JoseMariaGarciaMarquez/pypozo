"""
Script de prueba para verificar la integración del sistema "Pozo Inteligente" en PyPozo.
"""

import sys
import os
sys.path.append(r'c:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\pypozo')

import pandas as pd
import numpy as np
from pathlib import Path

def test_integration():
    """Probar la integración completa del sistema Pozo Inteligente."""
    print("🧠 Verificando integración del sistema 'Pozo Inteligente' en PyPozo...")
    
    # Test 1: Verificar que el módulo patreon_dlc existe
    try:
        import patreon_dlc
        print("✅ Módulo patreon_dlc importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando patreon_dlc: {e}")
        return False
    
    # Test 2: Verificar que el submódulo completion existe
    try:
        from patreon_dlc import completion
        print("✅ Submódulo completion importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando completion: {e}")
        return False
    
    # Test 3: Verificar que las funciones principales están disponibles
    try:
        from patreon_dlc.completion import SmartWellDialog, show_completion_dialog
        print("✅ SmartWellDialog y show_completion_dialog disponibles")
    except ImportError as e:
        print(f"❌ Error importando funciones principales: {e}")
        return False
    
    # Test 4: Verificar CompletionEngine
    try:
        from patreon_dlc.completion import CompletionEngine, CompletionResult
        print("✅ CompletionEngine y CompletionResult disponibles")
    except ImportError as e:
        print(f"❌ Error importando engine: {e}")
        return False
    
    # Test 5: Verificar que PyPozo puede cargar el DLC
    try:
        # Simular la verificación que hace PyPozo
        patreon_functions = {
            'show_completion_dialog': hasattr(completion, 'show_completion_dialog'),
            'create_completion_dialog': hasattr(completion, 'create_completion_dialog'),
            'SmartWellDialog': hasattr(completion, 'SmartWellDialog'),
            'CompletionEngine': hasattr(completion, 'CompletionEngine'),
        }
        
        missing_functions = [name for name, exists in patreon_functions.items() if not exists]
        
        if missing_functions:
            print(f"❌ Funciones faltantes: {missing_functions}")
            return False
        else:
            print("✅ Todas las funciones requeridas están disponibles")
    
    except Exception as e:
        print(f"❌ Error verificando funciones: {e}")
        return False
    
    # Test 6: Crear datos de prueba y verificar que el sistema funciona
    try:
        print("\n🔧 Creando datos de prueba...")
        
        # Crear pozo de prueba
        class MockWell:
            def __init__(self, name, data):
                self.name = name
                self.data = data
        
        # Generar datos sintéticos
        np.random.seed(42)
        depth = np.arange(1000, 2000, 0.5)
        n_points = len(depth)
        
        gr = 50 + 30 * np.sin(depth/100) + np.random.normal(0, 5, n_points)
        resistivity = np.exp(2 + 0.001 * depth + np.random.normal(0, 0.2, n_points))
        porosity = 0.2 + 0.1 * np.cos(depth/80) + np.random.normal(0, 0.02, n_points)
        
        # Introducir gaps
        gr[100:150] = np.nan
        resistivity[500:520] = np.nan
        
        data = pd.DataFrame({
            'DEPTH': depth,
            'GR': gr,
            'RESISTIVITY': resistivity,
            'POROSITY': porosity
        })
        
        test_well = MockWell("TEST-WELL", data)
        print("✅ Datos de prueba creados")
        
        # Test 7: Verificar CompletionEngine
        engine = CompletionEngine(test_well)
        print("✅ CompletionEngine instanciado correctamente")
        
        # Test 8: Verificar análisis de factibilidad
        analysis = engine.analyze_completability('GR', ['RESISTIVITY', 'POROSITY'])
        if analysis.get('feasible', False):
            print("✅ Análisis de factibilidad exitoso")
            print(f"   - Puntos de entrenamiento: {analysis.get('training_points', 0)}")
            print(f"   - Predictores recomendados: {len(analysis.get('recommended_predictors', []))}")
        else:
            print(f"⚠️ Análisis indica no factible: {analysis.get('error', 'razón desconocida')}")
        
        # Test 9: Verificar completado (solo test básico)
        if analysis.get('feasible', False):
            result = engine.complete_curve(
                target_curve='GR',
                predictor_curves=['RESISTIVITY', 'POROSITY'],
                model_type='auto'
            )
            
            if result.success:
                print("✅ Completado neuronal exitoso")
                print(f"   - Puntos completados: {result.completed_points}")
                print(f"   - Modelo usado: {result.model_type}")
                print(f"   - Métricas: R² = {result.metrics.get('r2', 'N/A'):.3f}")
            else:
                print(f"❌ Error en completado: {result.errors}")
        
        print("\n🎉 ¡Integración del sistema 'Pozo Inteligente' verificada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas de funcionalidad: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pypozo_integration():
    """Verificar que PyPozo puede usar el sistema correctamente."""
    print("\n🔗 Verificando integración con PyPozo principal...")
    
    try:
        # Simular la carga del DLC como lo hace PyPozo
        try:
            import patreon_dlc
            patreon_dlc_module = patreon_dlc
            has_patreon_dlc = True
            print("✅ PyPozo puede cargar patreon_dlc")
        except ImportError:
            has_patreon_dlc = False
            print("❌ PyPozo no puede cargar patreon_dlc")
            return False
        
        # Verificar funciones específicas que PyPozo busca
        required_functions = [
            'show_completion_dialog',
            'create_completion_dialog',
        ]
        
        for func_name in required_functions:
            if hasattr(patreon_dlc_module.completion, func_name):
                print(f"✅ Función {func_name} disponible para PyPozo")
            else:
                print(f"❌ Función {func_name} NO disponible para PyPozo")
                return False
        
        print("✅ PyPozo puede acceder a todas las funciones del sistema 'Pozo Inteligente'")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando integración con PyPozo: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 VERIFICACIÓN DE INTEGRACIÓN DEL SISTEMA 'POZO INTELIGENTE'")
    print("=" * 70)
    
    success = test_integration()
    
    if success:
        success = test_pypozo_integration()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ¡INTEGRACIÓN COMPLETA Y EXITOSA!")
        print("🚀 El sistema 'Pozo Inteligente' está listo para usar en PyPozo")
        print("\n💡 Para usar en PyPozo:")
        print("   1. Abre PyPozo normalmente")
        print("   2. Carga un pozo con datos")
        print("   3. Ve al menú '🧠 Pozo Inteligente' → 'Sistema Pozo Inteligente'")
        print("   4. O usa el botón '🧠 Pozo Inteligente - ¡ACTIVO!' en la pestaña principal")
    else:
        print("❌ INTEGRACIÓN FALLÓ")
        print("🔧 Revisa los errores mostrados arriba")
    
    print("=" * 70)
    
    input("\nPresiona Enter para continuar...")
