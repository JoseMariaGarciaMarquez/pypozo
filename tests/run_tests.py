"""
Script para ejecutar la suite de tests de PyPozo
================================================

Este script ejecuta todos los tests de forma organizada y genera reportes.
"""

import subprocess
import sys
from pathlib import Path
import time

def run_command(command, description):
    """Ejecutar comando y reportar resultado."""
    print(f"\n🔄 {description}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - EXITOSO ({duration:.1f}s)")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} - FALLÓ ({duration:.1f}s)")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando: {e}")
        return False

def main():
    """Ejecutar suite completa de tests."""
    print("🧪 SUITE DE TESTS DE PYPOZO")
    print("=" * 50)
    print(f"Directorio: {Path(__file__).parent.parent}")
    
    # Verificar que pytest está disponible
    try:
        import pytest
        print(f"✓ pytest {pytest.__version__} disponible")
    except ImportError:
        print("❌ pytest no está instalado")
        print("Instalar con: pip install pytest")
        return False
    
    # Lista de tests a ejecutar en orden
    test_commands = [
        ("python -m pytest tests/test_quick_check.py -v", 
         "Verificación rápida del entorno"),
        
        ("python -m pytest tests/test_core.py -v", 
         "Tests del módulo core"),
        
        ("python -m pytest tests/test_petrophysics.py -v", 
         "Tests de petrofísica"),
        
        ("python -m pytest tests/test_integration.py -v", 
         "Tests de integración"),
        
        ("python -m pytest tests/test_gui.py -v", 
         "Tests de interfaz gráfica"),
        
        ("python -m pytest tests/ -v --tb=short", 
         "Suite completa de tests"),
    ]
    
    results = []
    
    for command, description in test_commands:
        success = run_command(command, description)
        results.append((description, success))
        
        if not success and "Verificación rápida" in description:
            print("\n⚠️ La verificación rápida falló. Revisar configuración antes de continuar.")
            break
    
    # Reporte final
    print("\n" + "=" * 50)
    print("📊 REPORTE FINAL DE TESTS")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {description}")
    
    print(f"\n📈 Resultado: {passed_tests}/{total_tests} exitosos")
    
    if passed_tests == total_tests:
        print("🎉 TODOS LOS TESTS PASARON!")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisar los logs arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
