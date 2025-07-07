#!/usr/bin/env python3
"""
Script de prueba para el análisis de completado neural
=======================================================

Este script prueba la lógica mejorada de análisis de pozos.
"""

import sys
import pandas as pd
from pathlib import Path

# Agregar el path del módulo
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Importar PyPozo
    from src.pypozo import WellManager
    from patreon_dlc.neural_completion import NeuralCompletionEngine
    
    def test_neural_analysis():
        """Probar el análisis de completado neural."""
        print("🧪 Probando análisis de completado neural...")
        print("=" * 50)
        
        # Archivos de prueba
        test_files = [
            "data/ARIEL-1_export.las",
            "data/ABEDUL1_REPROCESADO.las",
            "data/70449_abedul1_gn_1850_800_05mz79p.las"
        ]
        
        engine = NeuralCompletionEngine()
        
        for file_path in test_files:
            las_file = Path(__file__).parent / file_path
            
            if not las_file.exists():
                print(f"⚠️  Archivo no encontrado: {file_path}")
                continue
                
            print(f"\n📁 Analizando: {las_file.name}")
            print("-" * 40)
            
            try:
                # Cargar el pozo
                well = WellManager.from_las(las_file)
                print(f"✅ Pozo cargado: {well.name}")
                print(f"📊 Curvas disponibles: {len(well.curves)}")
                print(f"📏 Intervalo: {well.depth_range[0]:.1f} - {well.depth_range[1]:.1f} m")
                
                # Mostrar información básica de datos
                print(f"\n🔍 Estructura de datos:")
                print(f"   Tipo: {type(well.data)}")
                print(f"   Columnas: {list(well.data.columns)}")  # Mostrar todas las columnas
                
                # Verificar específicamente la columna DEPTH
                if 'DEPTH' in well.data.columns:
                    print(f"   ✅ Columna DEPTH encontrada")
                    depth_col = well.data['DEPTH']
                    print(f"   📏 DEPTH rango: {depth_col.min():.1f} - {depth_col.max():.1f}")
                else:
                    print(f"   ❌ Columna DEPTH no encontrada")
                    print(f"   🔍 Buscando columnas similares...")
                    for col in well.data.columns:
                        if any(depth_name in col.upper() for depth_name in ['DEPTH', 'DEPT', 'MD']):
                            print(f"      📍 Posible: {col}")
                
                # Verificar si tiene métodos pandas
                if hasattr(well.data, 'iloc'):
                    print(f"   Primeras filas:")
                    try:
                        first_rows = well.data.iloc[:3]
                        for i, row in first_rows.iterrows():
                            values = [f"{v:.2f}" if isinstance(v, (int, float)) and abs(v) < 10000 else str(v)[:8] for v in row.values[:3]]
                            print(f"     {i}: {values}")
                    except:
                        print("     (No se pueden mostrar filas)")
                
                # Identificar valores NULL comunes
                print(f"\n🔢 Análisis de valores NULL:")
                first_curve = well.data.columns[1] if len(well.data.columns) > 1 else well.data.columns[0]
                if hasattr(well.data, 'unique'):
                    unique_vals = well.data[first_curve].unique()[:10]
                elif hasattr(well.data[first_curve], 'unique'):
                    unique_vals = well.data[first_curve].unique()[:10] 
                else:
                    unique_vals = "No disponible"
                print(f"   {first_curve}: {unique_vals}")
                
                # Analizar con el motor neural
                analysis = engine.analyze_well_for_completion(well)
                
                print(f"\n📈 Análisis de Completado Neural:")
                print(f"   💡 Viable: {'SÍ' if analysis['feasible'] else 'NO'}")
                print(f"   ✅ Curvas completas: {len(analysis['complete_curves'])}")
                print(f"   ⚠️  Curvas incompletas: {len(analysis['incomplete_curves'])}")
                
                # Análisis de profundidad
                depth_info = analysis['depth_analysis']
                if depth_info:
                    print(f"   📏 Rango de profundidad: {depth_info.get('total_range', 'N/A')}")
                    print(f"   📊 Columna de profundidad: {depth_info.get('depth_column', 'N/A')}")
                    print(f"   🔢 Puntos válidos: {depth_info.get('total_points', 'N/A')}")
                
                # Mostrar curvas completas
                if analysis['complete_curves']:
                    print(f"\n✅ Curvas Completas:")
                    for curve in analysis['complete_curves'][:5]:
                        curve_info = analysis['curve_analysis'].get(curve, {})
                        coverage = curve_info.get('coverage_ratio', 0) * 100
                        print(f"   • {curve}: {coverage:.1f}% cobertura")
                
                # Mostrar curvas incompletas
                if analysis['incomplete_curves']:
                    print(f"\n⚠️  Curvas Incompletas:")
                    for curve in analysis['incomplete_curves'][:5]:
                        curve_info = analysis['curve_analysis'].get(curve, {})
                        coverage = curve_info.get('coverage_ratio', 0) * 100
                        missing_info = analysis['missing_intervals'].get(curve, {})
                        gaps = missing_info.get('gaps_meters', 0)
                        print(f"   • {curve}: {coverage:.1f}% cobertura, +{gaps:.0f}m extensión")
                
                # Mostrar recomendaciones
                print(f"\n💡 Recomendaciones:")
                for rec in analysis['recommendations'][:5]:
                    print(f"   {rec}")
                
                # Mostrar oportunidades de correlación
                if analysis['correlation_opportunities']:
                    print(f"\n🧠 Oportunidades de Correlación:")
                    for opp in analysis['correlation_opportunities'][:3]:
                        print(f"   • {opp['model']} (Confianza: {opp['confidence']})")
                
            except Exception as e:
                print(f"❌ Error procesando {file_path}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n✅ Prueba completada")
    
    if __name__ == "__main__":
        test_neural_analysis()
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Asegúrate de que PyPozo y las dependencias estén instaladas")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
