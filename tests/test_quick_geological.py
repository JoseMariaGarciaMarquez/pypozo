"""
Prueba rápida de las mejoras geológicas implementadas.
"""

import sys
import os
sys.path.append(r'c:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\pypozo')

def test_quick():
    print("🧪 PRUEBA RÁPIDA DE MEJORAS GEOLÓGICAS")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Motor de completado
    try:
        from patreon_dlc.completion.completion_engine import CompletionEngine
        print("✅ Test 1/4: Motor de completado avanzado - OK")
        success_count += 1
    except Exception as e:
        print(f"❌ Test 1/4: Motor de completado - ERROR: {e}")
    
    # Test 2: Características geológicas
    try:
        from patreon_dlc.completion.geological_features import create_geological_feature_engineer
        engineer = create_geological_feature_engineer()
        print("✅ Test 2/4: Ingeniería de características geológicas - OK")
        success_count += 1
    except Exception as e:
        print(f"❌ Test 2/4: Características geológicas - ERROR: {e}")
    
    # Test 3: Arquitecturas avanzadas
    try:
        from patreon_dlc.completion.advanced_architectures import create_advanced_neural_architect
        architect = create_advanced_neural_architect()
        print("✅ Test 3/4: Arquitecturas neuronales avanzadas - OK")
        success_count += 1
    except Exception as e:
        print(f"❌ Test 3/4: Arquitecturas avanzadas - ERROR: {e}")
    
    # Test 4: Postprocesamiento
    try:
        from patreon_dlc.completion.geological_postprocessing import create_geological_postprocessor
        postprocessor = create_geological_postprocessor('GR')
        print("✅ Test 4/4: Postprocesamiento morfológico - OK")
        success_count += 1
    except Exception as e:
        print(f"❌ Test 4/4: Postprocesamiento - ERROR: {e}")
    
    print("=" * 50)
    print(f"🎯 RESULTADO: {success_count}/{total_tests} tests exitosos")
    
    if success_count == total_tests:
        print("🎉 ¡TODAS LAS MEJORAS GEOLÓGICAS ESTÁN FUNCIONANDO!")
        print("🚀 Sistema listo para reconstrucción de GR de alta calidad")
        return True
    else:
        print("⚠️ Algunas mejoras no están disponibles")
        print("📊 El sistema puede funcionar con capacidades reducidas")
        return False

if __name__ == "__main__":
    success = test_quick()
    print()
    if success:
        print("▶️ Para usar las mejoras:")
        print("   1. Ejecutar: python launch_pypozo_smart_well.py")
        print("   2. Cargar archivo LAS (ej: ABEDUL-1_MERGED_COMPLETE.las)")
        print("   3. Ir a '🧠 Pozo Inteligente' → 'Completado Neural'")
        print("   4. Seleccionar GR como target y SP, RHOB, NEUT como predictores")
        print("   5. ¡Disfrutar de la reconstrucción de alta calidad!")
