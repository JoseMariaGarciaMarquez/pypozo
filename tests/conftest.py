"""
Configuración compartida para tests de PyPozo
============================================

Este archivo define fixtures y configuraciones compartidas para todos los tests.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import os
import sys

# Agregar src al path para imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configuración de logging para tests
import logging
logging.basicConfig(level=logging.WARNING)  # Reducir verbosidad en tests


@pytest.fixture
def sample_las_data():
    """Crear datos LAS de muestra para tests."""
    depth = np.arange(1000, 1100, 0.5)  # 200 puntos
    
    # Simular curvas típicas
    gr = 50 + 30 * np.sin(depth / 20) + np.random.normal(0, 5, len(depth))
    gr = np.clip(gr, 10, 150)  # Valores típicos de GR
    
    rhob = 2.3 + 0.2 * np.sin(depth / 30) + np.random.normal(0, 0.05, len(depth))
    rhob = np.clip(rhob, 2.0, 2.8)  # Valores típicos de densidad
    
    nphi = 0.15 + 0.1 * np.cos(depth / 25) + np.random.normal(0, 0.02, len(depth))
    nphi = np.clip(nphi, 0.05, 0.35)  # Valores típicos de porosidad neutrón
    
    rt = 10 + 50 * np.exp(-depth / 500) + np.random.normal(0, 2, len(depth))
    rt = np.clip(rt, 1, 200)  # Valores típicos de resistividad
    
    return pd.DataFrame({
        'DEPTH': depth,
        'GR': gr,
        'RHOB': rhob,
        'NPHI': nphi,
        'RT': rt
    })


@pytest.fixture
def sample_well_metadata():
    """Metadatos de muestra para un pozo."""
    return {
        'well_name': 'TEST_WELL_001',
        'field': 'TEST_FIELD',
        'operator': 'TEST_OPERATOR',
        'api': '123456789',
        'location': {'x': 100000, 'y': 200000},
        'kb_elevation': 1250.0,
        'td': 1100.0
    }


@pytest.fixture
def temp_las_file(sample_las_data, sample_well_metadata):
    """Crear archivo LAS temporal para tests."""
    temp_dir = tempfile.mkdtemp()
    las_file = Path(temp_dir) / "test_well.las"
    
    # Crear archivo LAS básico
    with open(las_file, 'w') as f:
        f.write("~Version Information\n")
        f.write("VERS.   2.0    : CWLS log ASCII Standard -VERSION 2.0\n")
        f.write("WRAP.   NO     : One line per depth step\n")
        f.write("~Well Information\n")
        f.write(f"WELL.   {sample_well_metadata['well_name']}   : WELL\n")
        f.write(f"FLD .   {sample_well_metadata['field']}   : FIELD\n")
        f.write(f"COMP.   {sample_well_metadata['operator']}   : COMPANY\n")
        f.write("~Curve Information\n")
        f.write("DEPTH.M    : DEPTH\n")
        f.write("GR   .GAPI : GAMMA RAY\n")
        f.write("RHOB .G/C3 : BULK DENSITY\n")
        f.write("NPHI .V/V  : NEUTRON POROSITY\n")
        f.write("RT   .OHMM : RESISTIVITY\n")
        f.write("~ASCII\n")
        
        # Escribir datos
        for _, row in sample_las_data.iterrows():
            f.write(f"{row['DEPTH']:.1f} {row['GR']:.2f} {row['RHOB']:.3f} {row['NPHI']:.3f} {row['RT']:.2f}\n")
    
    yield str(las_file)
    
    # Limpiar después del test
    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_vcl_data():
    """Datos para tests de VCL."""
    depth = np.arange(1000, 1050, 0.5)
    gr = np.linspace(20, 120, len(depth)) + np.random.normal(0, 5, len(depth))
    return pd.Series(gr, index=depth, name='GR')


@pytest.fixture
def sample_porosity_data():
    """Datos para tests de porosidad."""
    depth = np.arange(1000, 1050, 0.5)
    rhob = 2.5 - 0.3 * np.random.random(len(depth))  # 2.2-2.5 g/cc
    nphi = 0.05 + 0.25 * np.random.random(len(depth))  # 5-30% porosidad
    
    return {
        'rhob': pd.Series(rhob, index=depth, name='RHOB'),
        'nphi': pd.Series(nphi, index=depth, name='NPHI')
    }


@pytest.fixture
def real_las_file():
    """Path a un archivo LAS real del proyecto para tests de integración."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    # Buscar archivos LAS reales
    las_files = list(data_dir.glob("*.las"))
    if las_files:
        return str(las_files[0])  # Retornar el primero disponible
    else:
        pytest.skip("No hay archivos LAS reales disponibles para test")


@pytest.fixture
def temp_output_dir():
    """Directorio temporal para outputs de test."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Limpiar después del test
    import shutil
    shutil.rmtree(temp_dir)
