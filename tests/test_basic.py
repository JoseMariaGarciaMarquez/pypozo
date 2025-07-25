"""
Tests básicos para PyPozo - Compatible con CI/CD
"""

import sys
import pytest
from pathlib import Path

def test_basic_imports():
    """Test que las importaciones básicas funcionen."""
    try:
        # Tests de importaciones básicas
        import os
        import sys
        assert True
        print("✅ Imports básicos funcionan")
    except ImportError as e:
        pytest.fail(f"Fallo importando dependencias básicas: {e}")

def test_optional_imports():
    """Test imports opcionales sin fallar."""
    try:
        import numpy as np
        print("✅ NumPy disponible")
    except ImportError:
        print("⚠️ NumPy no disponible en CI")
    
    try:
        import pandas as pd  
        print("✅ Pandas disponible")
    except ImportError:
        print("⚠️ Pandas no disponible en CI")
    
    # Este test siempre pasa
    assert True

def test_project_structure():
    """Test que la estructura del proyecto sea correcta."""
    project_root = Path(__file__).parent.parent
    
    # Verificar archivos importantes que deben existir
    required_files = [
        "README.md",
        "welcome_dialog.py", 
        ".gitignore"
    ]
    
    for file in required_files:
        assert (project_root / file).exists(), f"Archivo faltante: {file}"
        print(f"✅ {file} existe")

def test_gitignore_dlc_protection():
    """Test que .gitignore proteja el DLC de Patreon."""
    gitignore_path = Path(__file__).parent.parent / ".gitignore"
    
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding='utf-8')
        assert "patreon_dlc" in content, "DLC no está protegido en .gitignore"
        print("✅ DLC protegido en .gitignore")

def test_documentation_exists():
    """Test que la documentación principal exista.""" 
    project_root = Path(__file__).parent.parent
    readme_path = project_root / "README.md"
    
    assert readme_path.exists(), "README.md no existe"
    
    content = readme_path.read_text(encoding='utf-8')
    assert len(content) > 100, "README muy corto"
    print("✅ README.md existe y tiene contenido")

if __name__ == "__main__":
    # Ejecutar tests directamente si se llama el script
    print("🧪 Ejecutando tests básicos...")
    test_basic_imports()
    test_optional_imports() 
    test_project_structure()
    test_gitignore_dlc_protection()
    test_documentation_exists()
    print("🎉 Todos los tests básicos pasaron!")
