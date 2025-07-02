#!/usr/bin/env python3
"""
Simple test to verify PyPozo imports
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing PyPozo imports...")

try:
    from pypozo import WellManager
    print("✓ WellManager imported successfully")
except ImportError as e:
    print(f"❌ Error importing WellManager: {e}")

try:
    from pypozo import ProjectManager
    print("✓ ProjectManager imported successfully")
except ImportError as e:
    print(f"❌ Error importing ProjectManager: {e}")

try:
    from pypozo import WellPlotter
    print("✓ WellPlotter imported successfully")
except ImportError as e:
    print(f"❌ Error importing WellPlotter: {e}")

try:
    from pypozo.petrophysics import VclCalculator
    print("✓ VclCalculator imported successfully")
except ImportError as e:
    print(f"❌ Error importing VclCalculator: {e}")

try:
    from pypozo.petrophysics import PorosityCalculator
    print("✓ PorosityCalculator imported successfully")
except ImportError as e:
    print(f"❌ Error importing PorosityCalculator: {e}")

print("\n✓ All imports tested!")
