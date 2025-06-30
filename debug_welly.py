#!/usr/bin/env python3
"""
Script de depuración para Welly
"""

import welly
from pathlib import Path

# Ruta al archivo LAS
las_file = Path("data/70449_abedul1_gn_1850_800_05mz79p.las")

print(f"📁 Archivo: {las_file}")
print(f"📁 Existe: {las_file.exists()}")

if las_file.exists():
    try:
        # Intentar cargar con Welly
        print("\n🔧 Cargando con Welly...")
        well = welly.Well.from_las(str(las_file))
        
        print(f"✅ Pozo cargado: {type(well)}")
        print(f"📊 Atributos disponibles: {dir(well)}")
        
        # Verificar atributos principales
        print(f"\n🔍 Verificando atributos:")
        print(f"  - has data: {hasattr(well, 'data')}")
        print(f"  - has header: {hasattr(well, 'header')}")
        print(f"  - has basis: {hasattr(well, 'basis')}")
        print(f"  - has name: {hasattr(well, 'name')}")
        
        if hasattr(well, 'data'):
            print(f"  - data type: {type(well.data)}")
            print(f"  - data length: {len(well.data) if well.data is not None else 'None'}")
            
        if hasattr(well, 'header'):
            print(f"  - header type: {type(well.header)}")
            print(f"  - header keys: {list(well.header.keys()) if well.header else 'None'}")
            
        if hasattr(well, 'basis'):
            print(f"  - basis type: {type(well.basis)}")
            print(f"  - basis: {well.basis}")
            
        # Mostrar curvas disponibles
        if hasattr(well, 'data') and well.data is not None:
            print(f"\n📋 Curvas disponibles:")
            for i, curve in enumerate(well.data):
                print(f"  {i+1}. {curve.mnemonic if hasattr(curve, 'mnemonic') else str(curve)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ Tipo de error: {type(e)}")
        import traceback
        traceback.print_exc()
