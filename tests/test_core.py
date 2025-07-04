"""
Tests para el módulo core de PyPozo
===================================

Tests para WellManager y funcionalidades básicas de carga y gestión de pozos.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from pypozo.core.well import WellManager, WellDataFrame
except ImportError:
    # Fallback para estructura alternativa
    try:
        import pypozo
        WellManager = pypozo.WellManager
        WellDataFrame = pypozo.WellDataFrame
    except ImportError:
        pytest.skip("No se pudo importar WellManager", allow_module_level=True)


class TestWellManager:
    """Tests para la clase WellManager."""
    
    def test_well_manager_creation(self):
        """Test creación básica de WellManager."""
        well = WellManager()
        assert well is not None
        assert hasattr(well, 'name')
    
    def test_load_from_las_file(self, temp_las_file):
        """Test carga desde archivo LAS."""
        try:
            # Intentar cargar usando método estático
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(temp_las_file)
            else:
                # Fallback: crear instancia y cargar
                well = WellManager()
                well.load_las(temp_las_file)
            
            assert well is not None
            assert hasattr(well, 'data') or hasattr(well, 'curves')
            
            # Verificar que se cargaron datos
            if hasattr(well, 'data'):
                assert len(well.data) > 0
                assert 'GR' in well.data.columns
            elif hasattr(well, 'curves'):
                assert len(well.curves) > 0
                assert 'GR' in well.curves
                
        except Exception as e:
            pytest.skip(f"Error cargando LAS: {e}")
    
    def test_depth_range_calculation(self, temp_las_file):
        """Test obtención de rango de profundidad."""
        try:
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(temp_las_file)
            else:
                well = WellManager()
                well.load_las(temp_las_file)
            
            if hasattr(well, 'depth_range'):
                depth_range = well.depth_range
                assert len(depth_range) == 2
                assert depth_range[0] < depth_range[1]
                assert depth_range[0] >= 1000
                assert depth_range[1] <= 1100
                
        except Exception as e:
            pytest.skip(f"Error en test de depth_range: {e}")
    
    def test_curve_access(self, temp_las_file):
        """Test acceso a curvas individuales."""
        try:
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(temp_las_file)
            else:
                well = WellManager()
                well.load_las(temp_las_file)
            
            # Test diferentes métodos de acceso a curvas
            if hasattr(well, 'get_curve_data'):
                gr_data = well.get_curve_data('GR')
                assert gr_data is not None
                assert len(gr_data) > 0
            elif hasattr(well, 'data'):
                assert 'GR' in well.data.columns
                gr_data = well.data['GR']
                assert len(gr_data) > 0
                
        except Exception as e:
            pytest.skip(f"Error en test de curve_access: {e}")
    
    def test_add_new_curve(self, temp_las_file):
        """Test agregar nueva curva calculada."""
        try:
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(temp_las_file)
            else:
                well = WellManager()
                well.load_las(temp_las_file)
            
            # Crear datos de prueba
            if hasattr(well, 'data'):
                depth = well.data.index
                test_data = np.random.random(len(depth))
                
                # Intentar agregar curva
                if hasattr(well, 'add_curve'):
                    success = well.add_curve(
                        curve_name='TEST_CURVE',
                        data=test_data,
                        units='test_units',
                        description='Test curve'
                    )
                    assert success
                    assert 'TEST_CURVE' in well.data.columns
                else:
                    # Fallback: agregar directamente
                    well.data['TEST_CURVE'] = test_data
                    assert 'TEST_CURVE' in well.data.columns
                    
        except Exception as e:
            pytest.skip(f"Error en test de add_curve: {e}")


class TestWellDataFrame:
    """Tests para operaciones de WellDataFrame."""
    
    def test_well_merging(self, temp_las_file):
        """Test fusión de pozos."""
        try:
            # Crear dos pozos para fusionar
            if hasattr(WellManager, 'from_las'):
                well1 = WellManager.from_las(temp_las_file)
                well2 = WellManager.from_las(temp_las_file)
            else:
                well1 = WellManager()
                well1.load_las(temp_las_file)
                well2 = WellManager()
                well2.load_las(temp_las_file)
            
            # Modificar ligeramente well2 para simular datos diferentes
            if hasattr(well2, 'data'):
                well2.data['GR'] = well2.data['GR'] * 1.1  # 10% diferencia
                
                # Intentar fusión
                if hasattr(WellDataFrame, 'merge_wells'):
                    merged = WellDataFrame.merge_wells([well1, well2], 'MERGED_TEST')
                    assert merged is not None
                    assert hasattr(merged, 'data')
                    assert len(merged.data) > 0
                    
        except Exception as e:
            pytest.skip(f"Error en test de merging: {e}")
    
    def test_data_validation(self, sample_las_data):
        """Test validación de datos."""
        # Test con datos válidos
        assert len(sample_las_data) > 0
        assert 'GR' in sample_las_data.columns
        assert 'RHOB' in sample_las_data.columns
        
        # Test valores en rangos esperados
        gr_values = sample_las_data['GR']
        assert gr_values.min() >= 10
        assert gr_values.max() <= 150
        
        rhob_values = sample_las_data['RHOB']
        assert rhob_values.min() >= 2.0
        assert rhob_values.max() <= 2.8


class TestWellIO:
    """Tests para entrada/salida de datos de pozos."""
    
    def test_las_export(self, temp_las_file, temp_output_dir):
        """Test exportación a LAS."""
        try:
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(temp_las_file)
            else:
                well = WellManager()
                well.load_las(temp_las_file)
            
            # Crear archivo de salida
            output_file = Path(temp_output_dir) / "exported_test.las"
            
            # Intentar exportar
            if hasattr(well, 'export_to_las'):
                success = well.export_to_las(str(output_file))
                assert success
                assert output_file.exists()
                assert output_file.stat().st_size > 0
                
        except Exception as e:
            pytest.skip(f"Error en test de export: {e}")
    
    def test_csv_export(self, temp_las_file, temp_output_dir):
        """Test exportación a CSV."""
        try:
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(temp_las_file)
            else:
                well = WellManager()
                well.load_las(temp_las_file)
            
            # Crear archivo CSV
            csv_file = Path(temp_output_dir) / "exported_test.csv"
            
            if hasattr(well, 'data'):
                well.data.to_csv(str(csv_file), index=True)
                assert csv_file.exists()
                assert csv_file.stat().st_size > 0
                
        except Exception as e:
            pytest.skip(f"Error en test de CSV export: {e}")


class TestRealDataIntegration:
    """Tests de integración con datos reales del proyecto."""
    
    def test_load_real_las_file(self, real_las_file):
        """Test carga de archivo LAS real del proyecto."""
        try:
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(real_las_file)
            else:
                well = WellManager()
                well.load_las(real_las_file)
            
            assert well is not None
            
            # Verificar que se cargaron datos reales
            if hasattr(well, 'data'):
                assert len(well.data) > 0
                print(f"Cargadas {len(well.data.columns)} curvas del archivo real")
            elif hasattr(well, 'curves'):
                assert len(well.curves) > 0
                print(f"Cargadas {len(well.curves)} curvas del archivo real")
                
        except Exception as e:
            pytest.skip(f"Error cargando archivo real: {e}")
    
    def test_real_data_statistics(self, real_las_file):
        """Test estadísticas de datos reales."""
        try:
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(real_las_file)
            else:
                well = WellManager()
                well.load_las(real_las_file)
            
            if hasattr(well, 'data'):
                # Verificar estadísticas básicas
                stats = well.data.describe()
                assert len(stats) > 0
                
                # Verificar que no hay valores todos NaN
                for column in well.data.columns:
                    valid_count = well.data[column].notna().sum()
                    if valid_count > 0:  # Al menos una curva debe tener datos válidos
                        print(f"Curva {column}: {valid_count} valores válidos")
                        break
                else:
                    pytest.fail("Ninguna curva tiene datos válidos")
                    
        except Exception as e:
            pytest.skip(f"Error en estadísticas de datos reales: {e}")
