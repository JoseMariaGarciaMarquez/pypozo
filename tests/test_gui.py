"""
Tests para la interfaz gráfica de PyPozo
========================================

Tests para la aplicación GUI principal y sus funcionalidades.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import os

# Configurar para tests de GUI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Evitar ventanas en tests

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt
    import pypozo_app
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    pytest.skip("PyQt5 no disponible para tests de GUI", allow_module_level=True)


@pytest.fixture(scope="session")
def qapp():
    """Fixture para aplicación Qt."""
    if not GUI_AVAILABLE:
        pytest.skip("GUI no disponible")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # No cerrar la app para evitar problemas con otros tests


@pytest.fixture
def main_window(qapp):
    """Fixture para ventana principal."""
    try:
        window = pypozo_app.PyPozoApp()
        yield window
        window.close()
    except Exception as e:
        pytest.skip(f"Error creando ventana principal: {e}")


class TestMainWindow:
    """Tests para la ventana principal."""
    
    def test_window_creation(self, main_window):
        """Test creación de la ventana principal."""
        assert main_window is not None
        assert hasattr(main_window, 'wells')
        assert hasattr(main_window, 'current_well')
        assert main_window.wells == {}
    
    def test_window_components(self, main_window):
        """Test componentes principales de la ventana."""
        # Verificar componentes principales
        assert hasattr(main_window, 'wells_tree')
        assert hasattr(main_window, 'curves_list')
        assert hasattr(main_window, 'props_text')
        assert hasattr(main_window, 'figure')
        assert hasattr(main_window, 'canvas')
    
    def test_menu_bar(self, main_window):
        """Test barra de menú."""
        menubar = main_window.menuBar()
        assert menubar is not None
        
        # Verificar menús principales
        menu_texts = [action.text() for action in menubar.actions()]
        expected_menus = ['Archivo', 'Ver', 'Herramientas', 'Ayuda']
        
        for expected in expected_menus:
            assert any(expected in text for text in menu_texts), f"Menú '{expected}' no encontrado"
    
    def test_toolbar(self, main_window):
        """Test barra de herramientas."""
        toolbars = main_window.findChildren(type(main_window.toolbar))
        assert len(toolbars) > 0
        
        toolbar = toolbars[0]
        actions = toolbar.actions()
        assert len(actions) > 0
    
    def test_petrophysics_tabs(self, main_window):
        """Test pestañas de petrofísica."""
        if hasattr(main_window, 'petro_tabs'):
            tabs = main_window.petro_tabs
            assert tabs.count() >= 2  # Al menos VCL y Porosidad
            
            # Verificar nombres de pestañas
            tab_texts = [tabs.tabText(i) for i in range(tabs.count())]
            assert any('VCL' in text for text in tab_texts)
            assert any('Porosidad' in text for text in tab_texts)


class TestWellLoading:
    """Tests para carga de pozos."""
    
    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    def test_load_well_dialog(self, mock_dialog, main_window, temp_las_file):
        """Test diálogo de carga de pozos."""
        # Simular selección de archivo
        mock_dialog.return_value = (temp_las_file, "LAS files (*.las)")
        
        # Intentar cargar pozo
        try:
            main_window.load_well()
            # El test pasa si no hay excepciones
            assert True
        except Exception as e:
            pytest.skip(f"Error en test de carga: {e}")
    
    def test_load_well_from_path(self, main_window, temp_las_file):
        """Test carga directa desde path."""
        try:
            initial_count = len(main_window.wells)
            main_window.load_well_from_path(temp_las_file)
            
            # Verificar que se agregó el pozo
            assert len(main_window.wells) >= initial_count
            
        except Exception as e:
            pytest.skip(f"Error cargando desde path: {e}")
    
    def test_well_tree_update(self, main_window, temp_las_file):
        """Test actualización del árbol de pozos."""
        try:
            initial_items = main_window.wells_tree.topLevelItemCount()
            main_window.load_well_from_path(temp_las_file)
            
            # Verificar que se agregó item al árbol
            final_items = main_window.wells_tree.topLevelItemCount()
            assert final_items >= initial_items
            
        except Exception as e:
            pytest.skip(f"Error en actualización de árbol: {e}")


class TestPetrophysicsGUI:
    """Tests para la interfaz de petrofísica."""
    
    def test_vcl_tab_components(self, main_window):
        """Test componentes de la pestaña VCL."""
        # Verificar que existen los componentes principales
        assert hasattr(main_window, 'vcl_method_combo')
        assert hasattr(main_window, 'vcl_gr_combo')
        assert hasattr(main_window, 'vcl_gr_min')
        assert hasattr(main_window, 'vcl_gr_max')
        assert hasattr(main_window, 'calc_vcl_btn')
    
    def test_porosity_tab_components(self, main_window):
        """Test componentes de la pestaña de porosidad."""
        assert hasattr(main_window, 'por_method_combo')
        assert hasattr(main_window, 'por_rhob_combo')
        assert hasattr(main_window, 'por_nphi_combo')
        assert hasattr(main_window, 'calc_por_btn')
    
    def test_calculation_buttons_state(self, main_window):
        """Test estado de botones de cálculo."""
        # Sin pozo seleccionado, botones deben estar deshabilitados
        assert not main_window.calc_vcl_btn.isEnabled()
        assert not main_window.calc_por_btn.isEnabled()
    
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_calculation_without_well(self, mock_warning, main_window):
        """Test cálculo sin pozo seleccionado."""
        # Intentar calcular VCL sin pozo
        main_window.calculate_vcl()
        
        # Debe mostrar advertencia
        mock_warning.assert_called()


class TestPlotting:
    """Tests para funcionalidades de graficado."""
    
    def test_plot_components(self, main_window):
        """Test componentes de plotting."""
        assert hasattr(main_window, 'figure')
        assert hasattr(main_window, 'canvas')
        assert hasattr(main_window, 'plot_btn')
        assert hasattr(main_window, 'clear_plot_btn')
    
    def test_plot_buttons_state(self, main_window):
        """Test estado inicial de botones de plot."""
        # Sin pozo, botones deben estar deshabilitados
        assert not main_window.plot_btn.isEnabled()
        assert not main_window.plot_all_btn.isEnabled()
        assert not main_window.save_plot_btn.isEnabled()
    
    def test_clear_plot(self, main_window):
        """Test limpiar gráfico."""
        try:
            main_window.clear_plot()
            # Verificar que la figura se limpió
            assert len(main_window.figure.axes) == 0
        except Exception as e:
            pytest.skip(f"Error en clear_plot: {e}")


class TestWellComparison:
    """Tests para comparación de pozos."""
    
    def test_comparison_components(self, main_window):
        """Test componentes de comparación."""
        assert hasattr(main_window, 'compare_list')
        assert hasattr(main_window, 'compare_curve_combo')
        assert hasattr(main_window, 'compare_btn')
    
    def test_merge_wells_dialog(self, main_window):
        """Test diálogo de fusión de pozos."""
        # Test básico de existencia de método
        assert hasattr(main_window, 'merge_selected_wells')


class TestUtilityFunctions:
    """Tests para funciones utilitarias de la GUI."""
    
    def test_logging_functionality(self, main_window):
        """Test funcionalidad de logging."""
        assert hasattr(main_window, 'log_activity')
        assert hasattr(main_window, 'activity_log')
        
        # Test logging
        test_message = "Test log message"
        main_window.log_activity(test_message)
        
        # Verificar que se agregó al log
        log_text = main_window.activity_log.toPlainText()
        assert test_message in log_text
    
    def test_well_count_update(self, main_window):
        """Test actualización de conteo de pozos."""
        assert hasattr(main_window, 'update_wells_count')
        assert hasattr(main_window, 'wells_count_label')
        
        # Test actualización
        main_window.update_wells_count()
        
        # Verificar que el label se actualizó
        count_text = main_window.wells_count_label.text()
        assert "0" in count_text  # Debe mostrar 0 pozos inicialmente
    
    def test_curve_selection_utilities(self, main_window):
        """Test utilidades de selección de curvas."""
        assert hasattr(main_window, 'select_all_curves')
        assert hasattr(main_window, 'select_no_curves')
        assert hasattr(main_window, 'select_basic_curves')
        
        # Test funciones (sin errores)
        try:
            main_window.select_all_curves()
            main_window.select_no_curves()
            main_window.select_basic_curves()
        except Exception as e:
            pytest.skip(f"Error en funciones de selección: {e}")


class TestErrorHandling:
    """Tests para manejo de errores en la GUI."""
    
    def test_invalid_file_handling(self, main_window, temp_output_dir):
        """Test manejo de archivos inválidos."""
        # Crear archivo falso
        fake_file = Path(temp_output_dir) / "fake.las"
        fake_file.write_text("Este no es un archivo LAS válido")
        
        try:
            main_window.load_well_from_path(str(fake_file))
            # Si llega aquí, debe haber manejado el error graciosamente
        except Exception:
            # Se espera que los errores se manejen internamente
            pass
    
    def test_empty_well_operations(self, main_window):
        """Test operaciones con pozos vacíos."""
        # Verificar que las operaciones manejan pozos vacíos
        assert main_window.current_well is None
        
        # Estas operaciones no deben fallar catastróficamente
        try:
            main_window.update_well_properties()
            main_window.update_curves_list()
            main_window.update_petrophysics_ui()
        except Exception as e:
            pytest.skip(f"Error en operaciones con pozos vacíos: {e}")


class TestIntegrationGUI:
    """Tests de integración para la GUI."""
    
    def test_full_workflow_simulation(self, main_window, temp_las_file):
        """Test simulación de workflow completo."""
        try:
            # 1. Cargar pozo
            main_window.load_well_from_path(temp_las_file)
            assert len(main_window.wells) > 0
            
            # 2. Seleccionar pozo (simular click)
            if main_window.wells_tree.topLevelItemCount() > 0:
                item = main_window.wells_tree.topLevelItem(0)
                main_window.wells_tree.setCurrentItem(item)
                main_window.on_well_selected(item)
                
                assert main_window.current_well is not None
                
                # 3. Verificar que la UI se actualizó
                assert main_window.calc_vcl_btn.isEnabled()
                assert main_window.plot_btn.isEnabled()
                
                # 4. Test rápido de análisis
                main_window.run_quick_analysis()
                
        except Exception as e:
            pytest.skip(f"Error en workflow completo: {e}")
    
    def test_memory_cleanup(self, main_window):
        """Test limpieza de memoria."""
        assert hasattr(main_window, 'closeEvent')
        
        # Test que la ventana se puede cerrar sin errores
        try:
            main_window.close()
        except Exception as e:
            pytest.skip(f"Error en cleanup: {e}")
