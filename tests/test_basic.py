"""
Tests básicos para PyPozo - Compatible con CI/CD
"""

import sys
import pytest
from pathlib import Path

# Agregar src al path de forma relativa
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test que las importaciones básicas funcionen."""
    try:
        # Tests de importaciones sin GUI
        import numpy as np
        import pandas as pd
        assert True
    except ImportError as e:
        pytest.fail(f"Fallo importando dependencias básicas: {e}")

def test_pypozo_core_imports():
    """Test que PyPozo core se pueda importar."""
    try:
        from pypozo import WellManager
        assert WellManager is not None
    except ImportError as e:
        # Si no se puede importar, verificar que el archivo existe
        pypozo_path = Path(__file__).parent / "src" / "pypozo.py"
        if pypozo_path.exists():
            pytest.skip("PyPozo existe pero tiene dependencias faltantes")
        else:
            pytest.fail(f"PyPozo no se encuentra: {e}")

def test_welcome_dialog_import():
    """Test que el diálogo de bienvenida se pueda importar."""
    try:
        import welcome_dialog
        assert hasattr(welcome_dialog, 'WelcomeDialog')
    except ImportError:
        pytest.skip("PyQt5 no disponible en entorno CI")

def test_project_structure():
    """Test que la estructura del proyecto sea correcta."""
    project_root = Path(__file__).parent
    
    # Verificar archivos importantes
    required_files = [
        "README.md",
        "pyproject.toml", 
        "CHANGELOG.md",
        "welcome_dialog.py",
        ".gitignore"
    ]
    
    for file in required_files:
        assert (project_root / file).exists(), f"Archivo faltante: {file}"

def test_gitignore_dlc_protection():
    """Test que .gitignore proteja el DLC de Patreon."""
    gitignore_path = Path(__file__).parent / ".gitignore"
    
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding='utf-8')
        assert "patreon_dlc" in content, "DLC no está protegido en .gitignore"

def test_documentation_updated():
    """Test que la documentación mencione las nuevas funcionalidades."""
    readme_path = Path(__file__).parent / "README.md"
    
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        assert "Buy Me a Coffee" in content, "README no menciona Buy Me a Coffee"
        assert "diálogo" in content.lower() or "dialog" in content.lower(), "README no menciona diálogo de bienvenida"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
