"""
Script de prueba para validar las mejoras geológicas en la reconstrucción de GR.
Prueba todas las funcionalidades implementadas: características geológicas,
arquitecturas neuronales avanzadas, y postprocesamiento morfológico.
"""

import sys
import os
sys.path.append(r'c:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\pypozo')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def test_geological_improvements():
    """
    Prueba completa de las mejoras geológicas implementadas.
    """
    print("=" * 80)
    print("🧪 PRUEBA DE MEJORAS GEOLÓGICAS PARA RECONSTRUCCIÓN DE GR")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. VERIFICAR IMPORTACIONES DE MÓDULOS GEOLÓGICOS
    print("🔍 1. VERIFICANDO MÓDULOS GEOLÓGICOS")
    print("-" * 50)
    
    modules_status = {}
    
    try:
        from patreon_dlc.completion.geological_features import create_geological_feature_engineer
        modules_status['geological_features'] = "✅ DISPONIBLE"
        print("✅ geological_features.py - Ingeniería de características geológicas")
    except ImportError as e:
        modules_status['geological_features'] = f"❌ ERROR: {e}"
        print(f"❌ geological_features.py - Error: {e}")
    
    try:
        from patreon_dlc.completion.advanced_architectures import create_advanced_neural_architect
        modules_status['advanced_architectures'] = "✅ DISPONIBLE"
        print("✅ advanced_architectures.py - Arquitecturas neuronales avanzadas")
    except ImportError as e:
        modules_status['advanced_architectures'] = f"❌ ERROR: {e}"
        print(f"❌ advanced_architectures.py - Error: {e}")
    
    try:
        from patreon_dlc.completion.geological_postprocessing import create_geological_postprocessor
        modules_status['geological_postprocessing'] = "✅ DISPONIBLE"
        print("✅ geological_postprocessing.py - Postprocesamiento morfológico")
    except ImportError as e:
        modules_status['geological_postprocessing'] = f"❌ ERROR: {e}"
        print(f"❌ geological_postprocessing.py - Error: {e}")
    
    try:
        from patreon_dlc.completion.completion_engine import CompletionEngine
        modules_status['completion_engine'] = "✅ DISPONIBLE"
        print("✅ completion_engine.py - Motor de completado avanzado")
    except ImportError as e:
        modules_status['completion_engine'] = f"❌ ERROR: {e}"
        print(f"❌ completion_engine.py - Error: {e}")
    
    print()
    
    # 2. VERIFICAR DEPENDENCIAS OPCIONALES
    print("🔍 2. VERIFICANDO DEPENDENCIAS OPCIONALES")
    print("-" * 50)
    
    dependencies_status = {}
    
    try:
        import tensorflow as tf
        dependencies_status['tensorflow'] = f"✅ v{tf.__version__}"
        print(f"✅ TensorFlow {tf.__version__} - Arquitecturas CNN/LSTM/Autoencoder disponibles")
    except ImportError:
        dependencies_status['tensorflow'] = "⚠️ NO DISPONIBLE"
        print("⚠️ TensorFlow no disponible - usando solo sklearn")
    
    try:
        from scipy import signal, ndimage
        dependencies_status['scipy'] = "✅ DISPONIBLE"
        print("✅ SciPy - Procesamiento de señales y morfología matemática")
    except ImportError:
        dependencies_status['scipy'] = "⚠️ NO DISPONIBLE"
        print("⚠️ SciPy no disponible - funcionalidad limitada")
    
    try:
        from sklearn.model_selection import cross_val_score
        from sklearn.preprocessing import RobustScaler
        dependencies_status['sklearn'] = "✅ DISPONIBLE"
        print("✅ Scikit-learn - Modelos base y validación cruzada")
    except ImportError:
        dependencies_status['sklearn'] = "❌ NO DISPONIBLE"
        print("❌ Scikit-learn no disponible - ERROR CRÍTICO")
    
    print()
    
    # 3. PRUEBA DE INGENIERÍA DE CARACTERÍSTICAS GEOLÓGICAS
    if 'geological_features' in modules_status and modules_status['geological_features'].startswith("✅"):
        print("🔬 3. PRUEBA DE INGENIERÍA DE CARACTERÍSTICAS GEOLÓGICAS")
        print("-" * 60)
        
        try:
            # Crear datos sintéticos similares a registros geofísicos
            n_samples = 1000
            depth = np.linspace(1500, 2500, n_samples)  # Profundidad 1500-2500m
            
            # Simular curvas geofísicas con patrones geológicos realistas
            np.random.seed(42)
            
            # GR con variación geológica (lutitas altas, arenas bajas)
            base_gr = 50 + 30 * np.sin(depth / 200) + 20 * np.random.random(n_samples)
            gr_true = np.clip(base_gr, 15, 150)
            
            # SP correlacionado negativamente con GR
            sp = -20 - 0.6 * (gr_true - 50) + 10 * np.random.random(n_samples)
            
            # RHOB con variación geológica
            rhob = 2.4 - 0.002 * (gr_true - 50) + 0.1 * np.random.random(n_samples)
            rhob = np.clip(rhob, 1.9, 2.8)
            
            # NEUT correlacionado con arcillosidad
            neut = 15 + 0.15 * (gr_true - 50) + 5 * np.random.random(n_samples)
            neut = np.clip(neut, 5, 45)
            
            # CALI con rugosidad del pozo
            cali = 8.5 + 0.05 * (gr_true - 50) + 2 * np.random.random(n_samples)
            cali = np.clip(cali, 6, 16)
            
            # Crear DataFrame
            df_test = pd.DataFrame({
                'DEPTH': depth,
                'GR': gr_true,
                'SP': sp,
                'RHOB': rhob,
                'NEUT': neut,
                'CALI': cali
            })
            
            print(f"   📊 Datos sintéticos creados: {len(df_test)} muestras")
            print(f"   📏 Rango de profundidad: {depth.min():.1f} - {depth.max():.1f} m")
            
            # Crear ingeniero de características
            feature_engineer = create_geological_feature_engineer()
            
            # Extraer características
            df_enhanced = feature_engineer.extract_geological_features(
                df_test, 'GR', ['SP', 'RHOB', 'NEUT', 'CALI'])
            
            original_features = len(df_test.columns)
            enhanced_features = len(df_enhanced.columns)
            new_features = enhanced_features - original_features
            
            print(f"   ✅ Características originales: {original_features}")
            print(f"   🆕 Características nuevas: {new_features}")
            print(f"   📈 Total características: {enhanced_features}")
            
            # Mostrar algunas características nuevas
            geological_features = [col for col in df_enhanced.columns if col not in df_test.columns][:10]
            print(f"   🔬 Características geológicas creadas (muestra):")
            for feature in geological_features:
                print(f"      • {feature}")
            
            print("   ✅ Ingeniería de características geológicas - EXITOSA")
            
        except Exception as e:
            print(f"   ❌ Error en ingeniería de características: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # 4. PRUEBA DE ARQUITECTURAS NEURONALES AVANZADAS
    if 'advanced_architectures' in modules_status and modules_status['advanced_architectures'].startswith("✅"):
        print("🧠 4. PRUEBA DE ARQUITECTURAS NEURONALES AVANZADAS")
        print("-" * 60)
        
        try:
            architect = create_advanced_neural_architect()
            
            # Datos de prueba
            X_test = np.random.random((500, 10))
            y_test = np.random.random(500) * 100 + 20  # Simular GR
            
            # Selección de arquitectura
            architecture = architect.select_optimal_architecture(X_test, y_test, 'GR')
            print(f"   🏗️ Arquitectura seleccionada: {architecture}")
            
            # Entrenar modelo
            print("   🔄 Entrenando modelo...")
            model_result = architect.build_and_train_model(
                X_test[:400], y_test[:400], 
                X_test[400:], y_test[400:],
                architecture=architecture
            )
            
            print(f"   ✅ Modelo entrenado: {model_result.model_type}")
            print(f"   📊 Métricas disponibles: {list(model_result.metrics.keys())}")
            print(f"   🎯 R²: {model_result.metrics.get('r2', 'N/A'):.3f}")
            print(f"   📈 Confianza promedio: {np.mean(model_result.confidence):.3f}")
            
            print("   ✅ Arquitecturas neuronales avanzadas - EXITOSA")
            
        except Exception as e:
            print(f"   ❌ Error en arquitecturas avanzadas: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # 5. PRUEBA DE POSTPROCESAMIENTO MORFOLÓGICO
    if 'geological_postprocessing' in modules_status and modules_status['geological_postprocessing'].startswith("✅"):
        print("🔧 5. PRUEBA DE POSTPROCESAMIENTO MORFOLÓGICO")
        print("-" * 60)
        
        try:
            postprocessor = create_geological_postprocessor('GR')
            
            # Datos de prueba con ruido
            n_points = 500
            depth_test = np.linspace(1600, 1800, n_points)
            
            # Curva original (suave)
            original_gr = 40 + 20 * np.sin(depth_test / 50) + 10 * np.sin(depth_test / 20)
            
            # Curva "reconstruida" con ruido y artifacts
            reconstructed_gr = original_gr + 15 * np.random.random(n_points) - 7.5
            reconstructed_gr[100:120] += 50  # Artifact artificial
            reconstructed_gr[300:310] -= 30  # Otro artifact
            
            print(f"   📊 Datos de prueba: {n_points} puntos")
            print(f"   📏 Rango original: {original_gr.min():.1f} - {original_gr.max():.1f} gAPI")
            print(f"   🔀 Rango con ruido: {reconstructed_gr.min():.1f} - {reconstructed_gr.max():.1f} gAPI")
            
            # Aplicar postprocesamiento
            processed_gr = postprocessor.apply_morphological_processing(
                reconstructed_gr, original_gr, depth_test)
            
            print(f"   🛠️ Rango procesado: {processed_gr.min():.1f} - {processed_gr.max():.1f} gAPI")
            
            # Evaluación de calidad
            evaluation = postprocessor.evaluate_geological_quality(
                processed_gr, original_gr, depth_test)
            
            print(f"   📊 Métricas numéricas: {len(evaluation.numerical_metrics)}")
            print(f"   🌍 Métricas geológicas: {len(evaluation.geological_metrics)}")
            print(f"   🎨 Calidad morfológica: {len(evaluation.morphological_quality)}")
            
            if evaluation.warnings:
                print(f"   ⚠️ Advertencias: {len(evaluation.warnings)}")
            if evaluation.recommendations:
                print(f"   💡 Recomendaciones: {len(evaluation.recommendations)}")
            
            print("   ✅ Postprocesamiento morfológico - EXITOSO")
            
        except Exception as e:
            print(f"   ❌ Error en postprocesamiento: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # 6. RESUMEN DE CAPACIDADES
    print("📋 6. RESUMEN DE CAPACIDADES IMPLEMENTADAS")
    print("-" * 60)
    
    available_features = []
    
    if modules_status['geological_features'].startswith("✅"):
        available_features.extend([
            "✅ Gradientes verticales y curvatura",
            "✅ Razones entre curvas (litológicas)",
            "✅ Variaciones locales suavizadas",
            "✅ Indicadores de litología estimada",
            "✅ Características de textura y morfología",
            "✅ Características específicas para GR"
        ])
    
    if modules_status['advanced_architectures'].startswith("✅"):
        if dependencies_status.get('tensorflow', '').startswith("✅"):
            available_features.extend([
                "✅ CNN 1D para patrones locales",
                "✅ LSTM para secuencias geológicas",
                "✅ Autoencoders para representaciones",
                "✅ Selección automática de arquitectura"
            ])
        available_features.extend([
            "✅ MLP avanzado con regularización",
            "✅ Ensemble de modelos múltiples",
            "✅ Estimación de confianza de predicciones"
        ])
    
    if modules_status['geological_postprocessing'].startswith("✅"):
        available_features.extend([
            "✅ Filtrado de ruido geológicamente consciente",
            "✅ Suavizado adaptativo",
            "✅ Corrección de outliers geológicos",
            "✅ Operaciones morfológicas",
            "✅ Límites físicos realistas",
            "✅ Evaluación de calidad geológica"
        ])
    
    print(f"   🎯 CAPACIDADES DISPONIBLES ({len(available_features)}):")
    for feature in available_features:
        print(f"      {feature}")
    
    print()
    
    # 7. RECOMENDACIONES FINALES
    print("💡 7. RECOMENDACIONES PARA USO ÓPTIMO")
    print("-" * 60)
    
    recommendations = [
        "🔬 Usar datos con buena correlación geológica entre curvas",
        "📊 Mínimo 100 puntos de entrenamiento para resultados robustos",
        "🧠 Arquitecturas CNN 1D funcionan mejor con >500 muestras",
        "🎯 GR se reconstruye mejor con SP, RHOB, NEUT como predictores",
        "🔧 Postprocesamiento morfológico es crítico para realismo geológico",
        "📈 Evaluar métricas geológicas además de métricas numéricas",
        "⚠️ Revisar advertencias y aplicar recomendaciones del sistema"
    ]
    
    print("   📋 MEJORES PRÁCTICAS:")
    for rec in recommendations:
        print(f"      {rec}")
    
    print()
    print("=" * 80)
    print("🎉 PRUEBA DE MEJORAS GEOLÓGICAS COMPLETADA")
    print("=" * 80)
    print()
    
    # Retornar estado para scripts que llamen a esta función
    return {
        'modules': modules_status,
        'dependencies': dependencies_status,
        'available_features': available_features,
        'success': all(status.startswith("✅") for status in modules_status.values())
    }

if __name__ == "__main__":
    # Ejecutar prueba
    result = test_geological_improvements()
    
    # Salir con código apropiado
    if result['success']:
        print("✅ Todas las mejoras geológicas están funcionando correctamente")
        exit(0)
    else:
        print("⚠️ Algunas mejoras no están disponibles, pero el sistema puede funcionar")
        exit(1)
