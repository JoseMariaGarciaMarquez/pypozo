"""
Test rápido para verificar funcionalidad básica de PyPozo
"""

def test_always_pass():
    """Test que siempre pasa para verificar que pytest funciona."""
    assert True

def test_python_version():
    """Verificar versión de Python."""
    import sys
    version = sys.version_info
    assert version.major >= 3

def test_basic_functionality():
    """Test de funcionalidad básica."""
    result = 2 + 2
    assert result == 4
    
    lista = [1, 2, 3]
    assert len(lista) == 3

if __name__ == "__main__":
    test_always_pass()
    test_python_version()
    test_basic_functionality()
