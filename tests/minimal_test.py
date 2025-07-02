#!/usr/bin/env python3

import sys
from pathlib import Path

# Configurar path
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

print(f"Agregado al path: {src_path}")
print(f"Python path: {sys.path[:3]}")

# Test muy básico
try:
    import pypozo
    print("✅ pypozo importado")
    print(f"pypozo version: {pypozo.__version__}")
    print(f"pypozo location: {pypozo.__file__}")
except Exception as e:
    print(f"❌ Error importando pypozo: {e}")
    sys.exit(1)

# Test calculadoras
try:
    from pypozo.petrophysics import VclCalculator
    vcl = VclCalculator()
    print("✅ VclCalculator OK")
except Exception as e:
    print(f"❌ VclCalculator error: {e}")

try:
    from pypozo.petrophysics import PorosityCalculator  
    por = PorosityCalculator()
    print("✅ PorosityCalculator OK")
except Exception as e:
    print(f"❌ PorosityCalculator error: {e}")

print("Test completado")
