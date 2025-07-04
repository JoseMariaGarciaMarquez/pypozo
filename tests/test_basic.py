"""
Test básico de funcionamiento
=============================

Test simple para verificar que el entorno está configurado correctamente.
"""

def test_basic_math():
    """Test matemática básica."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    print("✓ Matemática básica funciona")

def test_imports():
    """Test imports básicos."""
    import sys
    import os
    from pathlib import Path
    
    assert sys.version_info >= (3, 7)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Test estructura del proyecto
    project_root = Path(__file__).parent.parent
    assert project_root.exists()
    assert (project_root / "src").exists()
    print("✓ Estructura del proyecto correcta")

def test_numpy_pandas():
    """Test NumPy y Pandas."""
    try:
        import numpy as np
        import pandas as pd
        
        # Test básico de NumPy
        arr = np.array([1, 2, 3, 4, 5])
        assert len(arr) == 5
        assert arr.mean() == 3.0
        
        # Test básico de Pandas
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        assert len(df) == 3
        assert list(df.columns) == ['a', 'b']
        
        print("✓ NumPy y Pandas funcionan correctamente")
        
    except ImportError as e:
        print(f"⚠️ Error importando NumPy/Pandas: {e}")
        assert False, "NumPy/Pandas requeridos"

if __name__ == "__main__":
    print("🧪 TESTS BÁSICOS")
    print("=" * 30)
    
    try:
        test_basic_math()
        test_imports()
        test_numpy_pandas()
        print("\n✅ TODOS LOS TESTS BÁSICOS PASARON")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
