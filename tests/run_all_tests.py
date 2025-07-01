#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner Principal - PyPozo 2.0
=================================

Script principal para ejecutar todos los tests de PyPozo de forma organizada.

Autor: José María García Márquez
Fecha: Julio 2025
"""

import sys
import subprocess
from pathlib import Path
import importlib.util

def run_test_file(test_file_path: Path, description: str) -> bool:
    """
    Ejecutar un archivo de test específico.
    
    Args:
        test_file_path: Ruta al archivo de test
        description: Descripción del test
        
    Returns:
        bool: True si el test pasó, False si falló
    """
    print(f"\\n{'='*60}")
    print(f"🧪 {description}")
    print(f"📁 Archivo: {test_file_path.name}")
    print(f"{'='*60}")
    
    if not test_file_path.exists():
        print(f"❌ Archivo no encontrado: {test_file_path}")
        return False
    
    try:
        # Ejecutar el test
        result = subprocess.run(
            [sys.executable, str(test_file_path)],
            capture_output=True,
            text=True,
            cwd=test_file_path.parent.parent
        )
        
        # Mostrar output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Verificar resultado
        if result.returncode == 0:
            print(f"✅ Test pasado: {description}")
            return True
        else:
            print(f"❌ Test falló: {description} (código: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando test: {str(e)}")
        return False

def main():
    """Función principal del test runner."""
    print("🚀 PyPozo 2.0 - Test Runner Principal")
    print("=" * 60)
    print("Ejecutando suite completa de tests...")
    
    # Ruta base de tests
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    # Lista de tests a ejecutar
    tests_to_run = [
        {
            "file": tests_dir / "test_fusion_pozos.py",
            "description": "Test de Fusión de Pozos (Datos Reales)"
        },
        {
            "file": tests_dir / "test_fusion_originales.py", 
            "description": "Test de Fusión con Archivos Originales"
        },
        {
            "file": tests_dir / "test_visualizacion.py",
            "description": "Test de Visualización de Registros"
        },
        {
            "file": tests_dir / "test_subplots_fix.py",
            "description": "Test de Corrección de Subplots (Eje Compartido)"
        },
        {
            "file": tests_dir / "test_visualization_fixes.py",
            "description": "Test de Correcciones de Visualización"
        }
    ]
    
    # Ejecutar tests
    passed = 0
    failed = 0
    
    for test_info in tests_to_run:
        success = run_test_file(test_info["file"], test_info["description"])
        
        if success:
            passed += 1
        else:
            failed += 1
    
    # Resumen final
    print(f"\\n{'='*60}")
    print("📊 RESUMEN DE TESTS")
    print(f"{'='*60}")
    print(f"✅ Tests pasados: {passed}")
    print(f"❌ Tests fallidos: {failed}")
    print(f"📈 Total ejecutados: {passed + failed}")
    
    if failed == 0:
        print(f"\\n🎉 ¡Todos los tests pasaron correctamente!")
        print(f"\\n💡 PyPozo 2.0 está listo para uso:")
        print(f"   • GUI principal: python pypozo_app.py")
        print(f"   • Demo de fusión: python demo_fusion_completo.py")
        print(f"   • Tests individuales: python tests/test_[nombre].py")
        return 0
    else:
        print(f"\\n⚠️ Algunos tests fallaron. Revise los errores arriba.")
        print(f"\\n🔧 Para debugging:")
        print(f"   • Ejecute tests individualmente")
        print(f"   • Verifique dependencias: pip install -r requirements.txt")
        print(f"   • Revise logs en pypozo_app.log")
        return 1

if __name__ == "__main__":
    sys.exit(main())
