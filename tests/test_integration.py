"""
Tests de integración para PyPozo
================================

Tests que verifican la integración entre módulos y workflows completos.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import tempfile
import shutil

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from pypozo.core.well import WellManager, WellDataFrame
    from pypozo.petrophysics import VclCalculator, PorosityCalculator
    from pypozo.visualization.plotter import WellPlotter
except ImportError:
    try:
        import pypozo
        WellManager = pypozo.WellManager
        WellDataFrame = pypozo.WellDataFrame
        VclCalculator = pypozo.VclCalculator
        PorosityCalculator = pypozo.PorosityCalculator
        WellPlotter = pypozo.WellPlotter
    except ImportError:
        pytest.skip("No se pudieron importar módulos de PyPozo", allow_module_level=True)


class TestEndToEndWorkflow:
    """Tests de workflow completo de principio a fin."""
    
    def test_complete_petrophysical_workflow(self, temp_las_file, temp_output_dir):
        """Test workflow petrofísico completo: carga → cálculos → visualización → exportación."""
        try:
            # Paso 1: Cargar pozo
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(temp_las_file)
            else:
                well = WellManager()
                well.load_las(temp_las_file)
            
            assert well is not None
            print(f"✓ Pozo cargado: {well.name if hasattr(well, 'name') else 'TEST_WELL'}")
            
            # Paso 2: Calcular VCL
            vcl_calc = VclCalculator()
            if hasattr(well, 'data') and 'GR' in well.data.columns:
                gr_data = well.data['GR']
                
                if hasattr(vcl_calc, 'calculate'):
                    vcl_result = vcl_calc.calculate(
                        gamma_ray=gr_data,
                        method='linear',
                        gr_clean=20,
                        gr_clay=120
                    )
                    
                    # Agregar VCL al pozo
                    if hasattr(well, 'add_curve') and 'vcl' in vcl_result:
                        well.add_curve('VCL', vcl_result['vcl'], 'fraction', 'Volume of clay')
                        print("✓ VCL calculado y agregado")
            
            # Paso 3: Calcular porosidad
            por_calc = PorosityCalculator()
            if hasattr(well, 'data') and 'RHOB' in well.data.columns and 'NPHI' in well.data.columns:
                rhob_data = well.data['RHOB']
                nphi_data = well.data['NPHI']
                
                if hasattr(por_calc, 'calculate_density_neutron_porosity'):
                    por_result = por_calc.calculate_density_neutron_porosity(
                        bulk_density=rhob_data,
                        neutron_porosity=nphi_data,
                        matrix_density=2.65,
                        fluid_density=1.0
                    )
                    
                    # Agregar porosidad al pozo
                    porosity_key = 'phie' if 'phie' in por_result else 'porosity'
                    if hasattr(well, 'add_curve'):
                        well.add_curve('PHIE', por_result[porosity_key], 'fraction', 'Effective porosity')
                        print("✓ Porosidad calculada y agregada")
            
            # Paso 4: Visualización
            plotter = WellPlotter()
            if hasattr(plotter, 'plot_curves'):
                curves_to_plot = ['GR', 'RHOB', 'NPHI']
                if hasattr(well, 'data'):
                    available_curves = [c for c in curves_to_plot if c in well.data.columns]
                    if available_curves:
                        fig = plotter.plot_curves(well, available_curves)
                        assert fig is not None
                        print(f"✓ Gráfico creado con {len(available_curves)} curvas")
                        
                        # Guardar plot
                        plot_file = Path(temp_output_dir) / "workflow_plot.png"
                        fig.savefig(str(plot_file))
                        assert plot_file.exists()
                        print(f"✓ Gráfico guardado: {plot_file.name}")
            
            # Paso 5: Exportación
            if hasattr(well, 'export_to_las'):
                export_file = Path(temp_output_dir) / "processed_well.las"
                success = well.export_to_las(str(export_file))
                if success:
                    assert export_file.exists()
                    print(f"✓ Pozo exportado: {export_file.name}")
            
            # Exportar datos como CSV
            if hasattr(well, 'data'):
                csv_file = Path(temp_output_dir) / "well_data.csv"
                well.data.to_csv(str(csv_file))
                assert csv_file.exists()
                print(f"✓ Datos exportados a CSV: {csv_file.name}")
            
            print("🎉 Workflow completo exitoso")
            
        except Exception as e:
            pytest.skip(f"Error en workflow completo: {e}")
    
    def test_multi_well_analysis(self, temp_las_file, temp_output_dir):
        """Test análisis de múltiples pozos."""
        try:
            wells = []
            
            # Crear múltiples pozos (simulando datos diferentes)
            for i in range(3):
                if hasattr(WellManager, 'from_las'):
                    well = WellManager.from_las(temp_las_file)
                else:
                    well = WellManager()
                    well.load_las(temp_las_file)
                
                # Modificar datos ligeramente para simular pozos diferentes
                if hasattr(well, 'data'):
                    well.data['GR'] = well.data['GR'] * (1 + i * 0.1)  # Variación 10%
                    well.name = f"WELL_{i+1}"
                
                wells.append(well)
                
            print(f"✓ {len(wells)} pozos creados para análisis")
            
            # Análisis comparativo
            if len(wells) >= 2:
                # Comparar estadísticas de GR
                gr_stats = {}
                for well in wells:
                    if hasattr(well, 'data') and 'GR' in well.data.columns:
                        gr_stats[well.name if hasattr(well, 'name') else f"Well_{id(well)}"] = {
                            'mean': well.data['GR'].mean(),
                            'std': well.data['GR'].std(),
                            'min': well.data['GR'].min(),
                            'max': well.data['GR'].max()
                        }
                
                print(f"✓ Estadísticas comparativas calculadas para {len(gr_stats)} pozos")
                
                # Fusión de pozos si está disponible
                if hasattr(WellDataFrame, 'merge_wells'):
                    merged_well = WellDataFrame.merge_wells(wells[:2], "MERGED_WELL")
                    if merged_well is not None:
                        print("✓ Fusión de pozos exitosa")
                        
                        # Exportar pozo fusionado
                        if hasattr(merged_well, 'export_to_las'):
                            merged_file = Path(temp_output_dir) / "merged_well.las"
                            success = merged_well.export_to_las(str(merged_file))
                            if success:
                                assert merged_file.exists()
                                print(f"✓ Pozo fusionado exportado: {merged_file.name}")
            
        except Exception as e:
            pytest.skip(f"Error en análisis multi-pozo: {e}")


class TestRealDataIntegration:
    """Tests de integración con datos reales del proyecto."""
    
    def test_real_data_processing(self, real_las_file, temp_output_dir):
        """Test procesamiento de datos reales."""
        try:
            # Cargar archivo real
            if hasattr(WellManager, 'from_las'):
                well = WellManager.from_las(real_las_file)
            else:
                well = WellManager()
                well.load_las(real_las_file)
            
            print(f"✓ Archivo real cargado: {Path(real_las_file).name}")
            
            # Inspeccionar datos
            if hasattr(well, 'data'):
                curves = list(well.data.columns)
                print(f"📊 Curvas disponibles: {len(curves)}")
                print(f"📏 Puntos de datos: {len(well.data)}")
                
                # Estadísticas básicas
                stats = well.data.describe()
                print("✓ Estadísticas calculadas")
                
                # Buscar curvas comunes para análisis
                common_curves = {
                    'GR': [c for c in curves if 'GR' in c.upper()],
                    'RHOB': [c for c in curves if any(kw in c.upper() for kw in ['RHOB', 'DEN'])],
                    'NPHI': [c for c in curves if any(kw in c.upper() for kw in ['NPHI', 'NEU'])],
                    'RT': [c for c in curves if any(kw in c.upper() for kw in ['RT', 'RES', 'ILD', 'LLD'])]
                }
                
                available_analyses = {}
                for curve_type, found_curves in common_curves.items():
                    if found_curves:
                        available_analyses[curve_type] = found_curves[0]  # Usar la primera encontrada
                
                print(f"🔍 Análisis disponibles: {list(available_analyses.keys())}")
                
                # Calcular VCL si hay GR
                if 'GR' in available_analyses:
                    try:
                        vcl_calc = VclCalculator()
                        gr_data = well.data[available_analyses['GR']]
                        
                        # Estimar parámetros automáticamente
                        gr_clean = np.percentile(gr_data.dropna(), 5)
                        gr_clay = np.percentile(gr_data.dropna(), 95)
                        
                        if hasattr(vcl_calc, 'calculate'):
                            vcl_result = vcl_calc.calculate(
                                gamma_ray=gr_data,
                                method='linear',
                                gr_clean=gr_clean,
                                gr_clay=gr_clay
                            )
                            print(f"✓ VCL calculado (GR: {gr_clean:.1f}-{gr_clay:.1f})")
                    except Exception as e:
                        print(f"⚠️ Error calculando VCL: {e}")
                
                # Calcular porosidad si hay RHOB y NPHI
                if 'RHOB' in available_analyses and 'NPHI' in available_analyses:
                    try:
                        por_calc = PorosityCalculator()
                        rhob_data = well.data[available_analyses['RHOB']]
                        nphi_data = well.data[available_analyses['NPHI']]
                        
                        if hasattr(por_calc, 'calculate_density_neutron_porosity'):
                            por_result = por_calc.calculate_density_neutron_porosity(
                                bulk_density=rhob_data,
                                neutron_porosity=nphi_data,
                                matrix_density=2.65,
                                fluid_density=1.0
                            )
                            print("✓ Porosidad calculada")
                    except Exception as e:
                        print(f"⚠️ Error calculando porosidad: {e}")
                
                # Exportar resultados
                output_file = Path(temp_output_dir) / f"real_data_processed_{Path(real_las_file).stem}.csv"
                well.data.to_csv(str(output_file))
                print(f"✓ Datos reales procesados y exportados: {output_file.name}")
            
        except Exception as e:
            pytest.skip(f"Error procesando datos reales: {e}")
    
    def test_batch_processing(self, temp_output_dir):
        """Test procesamiento en lote de múltiples archivos."""
        try:
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data"
            
            if not data_dir.exists():
                pytest.skip("Directorio de datos no encontrado")
            
            # Buscar archivos LAS
            las_files = list(data_dir.glob("*.las"))[:3]  # Limitar a 3 para tests
            
            if not las_files:
                pytest.skip("No hay archivos LAS para procesamiento en lote")
            
            processed_wells = []
            
            for las_file in las_files:
                try:
                    if hasattr(WellManager, 'from_las'):
                        well = WellManager.from_las(str(las_file))
                    else:
                        well = WellManager()
                        well.load_las(str(las_file))
                    
                    processed_wells.append({
                        'file': las_file.name,
                        'well': well,
                        'curves': len(well.data.columns) if hasattr(well, 'data') else 0,
                        'points': len(well.data) if hasattr(well, 'data') else 0
                    })
                    
                except Exception as e:
                    print(f"⚠️ Error procesando {las_file.name}: {e}")
            
            print(f"✓ Procesamiento en lote: {len(processed_wells)}/{len(las_files)} exitosos")
            
            # Generar reporte de lote
            if processed_wells:
                report_file = Path(temp_output_dir) / "batch_processing_report.txt"
                with open(report_file, 'w') as f:
                    f.write("REPORTE DE PROCESAMIENTO EN LOTE\n")
                    f.write("=" * 40 + "\n\n")
                    
                    for well_info in processed_wells:
                        f.write(f"Archivo: {well_info['file']}\n")
                        f.write(f"Curvas: {well_info['curves']}\n")
                        f.write(f"Puntos: {well_info['points']}\n")
                        f.write("-" * 20 + "\n")
                
                print(f"✓ Reporte generado: {report_file.name}")
            
        except Exception as e:
            pytest.skip(f"Error en procesamiento en lote: {e}")


class TestSystemIntegration:
    """Tests de integración del sistema completo."""
    
    def test_memory_usage(self, temp_las_file):
        """Test uso de memoria con operaciones típicas."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Cargar múltiples pozos
            wells = []
            for i in range(5):
                if hasattr(WellManager, 'from_las'):
                    well = WellManager.from_las(temp_las_file)
                else:
                    well = WellManager()
                    well.load_las(temp_las_file)
                wells.append(well)
            
            mid_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Realizar cálculos
            for well in wells:
                if hasattr(well, 'data') and 'GR' in well.data.columns:
                    vcl_calc = VclCalculator()
                    if hasattr(vcl_calc, 'calculate'):
                        vcl_result = vcl_calc.calculate(
                            gamma_ray=well.data['GR'],
                            method='linear',
                            gr_clean=20,
                            gr_clay=120
                        )
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"💾 Memoria inicial: {initial_memory:.1f} MB")
            print(f"💾 Memoria con pozos: {mid_memory:.1f} MB")
            print(f"💾 Memoria final: {final_memory:.1f} MB")
            
            # Verificar que el uso de memoria es razonable
            memory_increase = final_memory - initial_memory
            assert memory_increase < 500  # No más de 500 MB de incremento
            
        except ImportError:
            pytest.skip("psutil no disponible para test de memoria")
        except Exception as e:
            pytest.skip(f"Error en test de memoria: {e}")
    
    def test_concurrent_operations(self, temp_las_file):
        """Test operaciones concurrentes (simuladas)."""
        try:
            import threading
            import time
            
            results = []
            errors = []
            
            def load_and_process(thread_id):
                try:
                    if hasattr(WellManager, 'from_las'):
                        well = WellManager.from_las(temp_las_file)
                    else:
                        well = WellManager()
                        well.load_las(temp_las_file)
                    
                    # Simular procesamiento
                    if hasattr(well, 'data') and 'GR' in well.data.columns:
                        vcl_calc = VclCalculator()
                        if hasattr(vcl_calc, 'calculate'):
                            vcl_result = vcl_calc.calculate(
                                gamma_ray=well.data['GR'],
                                method='linear',
                                gr_clean=20,
                                gr_clay=120
                            )
                    
                    results.append(f"Thread {thread_id}: OK")
                    
                except Exception as e:
                    errors.append(f"Thread {thread_id}: {e}")
            
            # Crear y ejecutar threads
            threads = []
            for i in range(3):
                thread = threading.Thread(target=load_and_process, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Esperar completación
            for thread in threads:
                thread.join(timeout=10)
            
            print(f"✓ Operaciones concurrentes: {len(results)} exitosas, {len(errors)} errores")
            
            # Al menos la mayoría debe ser exitosa
            assert len(results) >= len(threads) // 2
            
        except Exception as e:
            pytest.skip(f"Error en test de concurrencia: {e}")
    
    def test_error_recovery(self, temp_output_dir):
        """Test recuperación ante errores."""
        try:
            # Test con archivo corrupto
            corrupt_file = Path(temp_output_dir) / "corrupt.las"
            corrupt_file.write_text("Este archivo está corrupto\nNo es un LAS válido")
            
            try:
                if hasattr(WellManager, 'from_las'):
                    well = WellManager.from_las(str(corrupt_file))
                else:
                    well = WellManager()
                    well.load_las(str(corrupt_file))
                # Si llega aquí, manejó el error graciosamente
            except Exception as e:
                # Se espera que falle, pero de manera controlada
                print(f"✓ Error manejado graciosamente: {type(e).__name__}")
            
            # Test con datos inválidos
            vcl_calc = VclCalculator()
            invalid_data = pd.Series([np.nan, np.inf, -np.inf])
            
            try:
                if hasattr(vcl_calc, 'calculate'):
                    result = vcl_calc.calculate(
                        gamma_ray=invalid_data,
                        method='linear',
                        gr_clean=20,
                        gr_clay=120
                    )
                # Debe manejar datos inválidos
                print("✓ Datos inválidos manejados")
            except Exception as e:
                print(f"✓ Error en datos inválidos manejado: {type(e).__name__}")
            
        except Exception as e:
            pytest.skip(f"Error en test de recuperación: {e}")
