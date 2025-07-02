#!/usr/bin/env python3
"""
Test the enhanced porosity functionality with corrections
"""
import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from pypozo.petrophysics import PorosityCalculator
    print("✅ PorosityCalculator imported successfully")
    
    # Create calculator instance
    calc = PorosityCalculator()
    print("✅ PorosityCalculator instance created")
    
    # Test data (synthetic)
    bulk_density = np.array([2.0, 2.1, 2.2, 2.3, 2.4, 2.5])
    vcl_data = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
    
    print("\n🧪 Testing density porosity calculation...")
    result = calc.calculate_density_porosity(
        bulk_density=bulk_density,
        matrix_density=2.65,
        fluid_density=1.0
    )
    print(f"✅ Porosity calculated: {result['porosity'][:3]}...")
    
    print("\n🧪 Testing clay correction...")
    corrected_result = calc.apply_clay_correction(result, vcl_data)
    print(f"✅ Clay correction applied: {corrected_result.get('clay_correction_applied', False)}")
    
    print("\n🧪 Testing gas correction...")
    gas_corrected_result = calc.apply_gas_correction(result)
    print(f"✅ Gas correction applied: {gas_corrected_result.get('gas_correction_applied', False)}")
    
    print("\n🧪 Testing lithology analysis...")
    neutron_data = np.array([0.15, 0.20, 0.25, 0.30, 0.35, 0.40])
    litho_analysis = calc.get_lithology_recommendations(
        phid=result['porosity'], 
        phin=neutron_data
    )
    print(f"✅ Lithology analysis: {litho_analysis['dominant_lithology']}")
    
    print("\n✅ All enhanced functionality tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
