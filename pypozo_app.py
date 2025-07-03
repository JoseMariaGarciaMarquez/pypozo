#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPozo App - Aplicación GUI Completa
===================================

Aplicación de escritorio profesional para análisis de pozos.
Alternativa Open Source a WellCAD con funcionalidades completas.

Autor: José María García Márquez
Fecha: Junio 2025
"""

import sys
import os
import logging
import traceback
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Any

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QTextEdit,
        QMenuBar, QToolBar, QStatusBar, QFileDialog, QMessageBox,
        QPushButton, QLabel, QComboBox, QCheckBox, QSpinBox, QGroupBox,
        QListWidget, QListWidgetItem, QProgressBar, QFrame, QScrollArea,
        QInputDialog, QDialog, QDoubleSpinBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextCursor
    
    # Para integrar matplotlib con PyQt5
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("❌ PyQt5 no está disponible. Instale PyQt5 para usar la GUI:")
    print("   pip install PyQt5")

if PYQT5_AVAILABLE:
    from pypozo import WellManager, WellPlotter, ProjectManager
    from pypozo.petrophysics import (VclCalculator, PorosityCalculator, PetrophysicsCalculator,
                                     WaterSaturationCalculator, PermeabilityCalculator, LithologyAnalyzer)

logger = logging.getLogger(__name__)

class WellLoadThread(QThread):
    """Thread para cargar pozos sin bloquear la GUI."""
    
    well_loaded = pyqtSignal(object, str)  # WellManager, filename
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress_updated.emit(25)
            well = WellManager.from_las(self.file_path)
            self.progress_updated.emit(75)
            self.well_loaded.emit(well, Path(self.file_path).name)
            self.progress_updated.emit(100)
        except Exception as e:
            self.error_occurred.emit(str(e))

class PyPozoApp(QMainWindow):
    """
    Aplicación principal de PyPozo 2.0.
    
    GUI profesional para análisis de pozos con todas las funcionalidades
    necesarias para competir con WellCAD.
    """
    
    def __init__(self):
        super().__init__()
        
        self.wells: Dict[str, WellManager] = {}
        self.current_well: Optional[WellManager] = None
        self.current_well_name: str = ""
        self.plotter = WellPlotter()
        self.project_manager = ProjectManager()
        
        # Lista para rastrear threads activos
        self.active_threads: List[QThread] = []
        
        self.init_ui()
        self.setup_logging()
        
        logger.info("🚀 PyPozo App iniciada")
        self.status_bar.showMessage("✅ PyPozo App lista para usar")
    
    def init_ui(self):
        """Inicializar la interfaz de usuario."""
        self.setWindowTitle("PyPozo App - Análisis Profesional de Pozos")
        
        # Configurar ícono de la aplicación
        try:
            icon_path = Path(__file__).parent / "images" / "icono.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                logger.info(f"✅ Ícono cargado: {icon_path}")
            else:
                logger.warning(f"⚠️ Ícono no encontrado: {icon_path}")
        except Exception as e:
            logger.warning(f"⚠️ Error cargando ícono: {e}")
        
        self.setGeometry(100, 100, 1600, 1000)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Paneles
        left_panel = self.create_left_panel()
        center_panel = self.create_center_panel()
        right_panel = self.create_right_panel()
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        
        # Configurar proporciones
        main_splitter.setSizes([350, 900, 350])
        
        # Crear menús y barras
        self.create_menus()
        self.create_toolbars()
        self.create_status_bar()
        
        # Aplicar estilo
        self.apply_professional_style()
        
        # Inicializar UI de petrofísica
        self.update_petrophysics_ui()
    
    def create_left_panel(self) -> QWidget:
        """Panel izquierdo - Explorador de pozos."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Título
        title = QLabel("📁 Explorador de Pozos")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #2E8B57; margin: 10px;")
        layout.addWidget(title)
        
        # Árbol de pozos
        self.wells_tree = QTreeWidget()
        self.wells_tree.setHeaderLabel("Pozos Cargados")
        self.wells_tree.itemClicked.connect(self.on_well_selected)
        layout.addWidget(self.wells_tree)
        
        # Botones de acción
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)
        
        self.load_well_btn = QPushButton("📂 Cargar Pozo")
        self.load_well_btn.clicked.connect(self.load_well)
        buttons_layout.addWidget(self.load_well_btn)
        
        self.load_multiple_btn = QPushButton("📁 Cargar Múltiples")
        self.load_multiple_btn.clicked.connect(self.load_multiple_wells)
        buttons_layout.addWidget(self.load_multiple_btn)
        
        self.remove_well_btn = QPushButton("🗑️ Remover Pozo")
        self.remove_well_btn.clicked.connect(self.remove_well)
        self.remove_well_btn.setEnabled(False)
        buttons_layout.addWidget(self.remove_well_btn)
        
        self.clear_all_btn = QPushButton("🗃️ Limpiar Todo")
        self.clear_all_btn.clicked.connect(self.clear_all_wells)
        buttons_layout.addWidget(self.clear_all_btn)
        
        layout.addWidget(buttons_frame)
        
        # Propiedades del pozo
        props_group = QGroupBox("📊 Propiedades del Pozo")
        props_layout = QVBoxLayout(props_group)
        
        self.props_text = QTextEdit()
        self.props_text.setMaximumHeight(250)
        self.props_text.setReadOnly(True)
        self.props_text.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ddd;")
        props_layout.addWidget(self.props_text)
        
        layout.addWidget(props_group)
        
        return panel
    
    def create_center_panel(self) -> QWidget:
        """Panel central - Visualización."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header con controles
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        title = QLabel("📈 Visualización de Registros")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #2E8B57;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.plot_btn = QPushButton("🎨 Graficar Seleccionadas")
        self.plot_btn.clicked.connect(self.plot_selected_curves)
        self.plot_btn.setEnabled(False)
        header_layout.addWidget(self.plot_btn)
        
        self.plot_together_btn = QPushButton("🔗 Graficar Juntas")
        self.plot_together_btn.clicked.connect(self.plot_curves_together)
        self.plot_together_btn.setEnabled(False)
        header_layout.addWidget(self.plot_together_btn)
        
        self.plot_all_btn = QPushButton("📊 Graficar Todo")
        self.plot_all_btn.clicked.connect(self.plot_all_curves)
        self.plot_all_btn.setEnabled(False)
        header_layout.addWidget(self.plot_all_btn)
        
        self.save_plot_btn = QPushButton("💾 Guardar Gráfico")
        self.save_plot_btn.clicked.connect(self.save_current_plot)
        self.save_plot_btn.setEnabled(False)
        header_layout.addWidget(self.save_plot_btn)
        
        layout.addWidget(header_frame)
        
        # Canvas de matplotlib
        self.figure = Figure(figsize=(14, 10))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Panel derecho - Herramientas."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Título
        title = QLabel("🔧 Herramientas de Análisis")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #2E8B57; margin: 10px;")
        layout.addWidget(title)
        
        # Tabs
        self.tools_tabs = QTabWidget()
        
        # Tab 1: Selección de curvas
        curves_tab = self.create_curves_tab()
        self.tools_tabs.addTab(curves_tab, "📊 Curvas")
        
        # Tab 2: Comparación
        comparison_tab = self.create_comparison_tab()
        self.tools_tabs.addTab(comparison_tab, "⚖️ Comparar")
        
        # Tab 3: Análisis
        analysis_tab = self.create_analysis_tab()
        self.tools_tabs.addTab(analysis_tab, "🔬 Análisis")
        
        # Tab 4: Petrofísica
        petrophysics_tab = self.create_petrophysics_tab()
        self.tools_tabs.addTab(petrophysics_tab, "🧪 Petrofísica")
        
        layout.addWidget(self.tools_tabs)
        
        return panel
    
    def create_curves_tab(self) -> QWidget:
        """Tab para selección de curvas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Información del pozo actual
        self.current_well_label = QLabel("Seleccione un pozo")
        self.current_well_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.current_well_label)
        
        # Lista de curvas
        curves_label = QLabel("Curvas Disponibles:")
        layout.addWidget(curves_label)
        
        self.curves_list = QListWidget()
        self.curves_list.setSelectionMode(QListWidget.MultiSelection)
        self.curves_list.itemSelectionChanged.connect(self.on_curve_selection_changed)
        layout.addWidget(self.curves_list)
        
        # Botones de selección rápida
        quick_frame = QFrame()
        quick_layout = QVBoxLayout(quick_frame)
        
        # Primera fila
        row1 = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Todo")
        self.select_all_btn.clicked.connect(self.select_all_curves)
        row1.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("❌ Nada")
        self.select_none_btn.clicked.connect(self.select_no_curves)
        row1.addWidget(self.select_none_btn)
        
        quick_layout.addLayout(row1)
        
        # Segunda fila - Presets
        row2 = QHBoxLayout()
        
        self.select_basic_btn = QPushButton("📊 Básicas")
        self.select_basic_btn.clicked.connect(self.select_basic_curves)
        row2.addWidget(self.select_basic_btn)
        
        self.select_petro_btn = QPushButton("🔬 Petrofísicas")
        self.select_petro_btn.clicked.connect(self.select_petro_curves)
        row2.addWidget(self.select_petro_btn)
        
        quick_layout.addLayout(row2)
        
        # Tercera fila
        row3 = QHBoxLayout()
        
        self.select_acoustic_btn = QPushButton("🔊 Acústicas")
        self.select_acoustic_btn.clicked.connect(self.select_acoustic_curves)
        row3.addWidget(self.select_acoustic_btn)
        
        self.select_electrical_btn = QPushButton("⚡ Eléctricas")
        self.select_electrical_btn.clicked.connect(self.select_electrical_curves)
        row3.addWidget(self.select_electrical_btn)
        
        quick_layout.addLayout(row3)
        
        layout.addWidget(quick_frame)
        
        # Info de selección
        self.selection_info = QLabel("Curvas seleccionadas: 0")
        self.selection_info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.selection_info)
        
        return tab
    
    def create_comparison_tab(self) -> QWidget:
        """Tab para comparación de pozos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        compare_label = QLabel("Pozos para Comparar:")
        layout.addWidget(compare_label)
        
        self.compare_list = QListWidget()
        self.compare_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.compare_list)
        
        # Curva para comparar
        curve_frame = QFrame()
        curve_layout = QHBoxLayout(curve_frame)
        curve_layout.addWidget(QLabel("Curva:"))
        
        self.compare_curve_combo = QComboBox()
        curve_layout.addWidget(self.compare_curve_combo)
        
        layout.addWidget(curve_frame)
        
        self.compare_btn = QPushButton("⚖️ Comparar Seleccionados")
        self.compare_btn.clicked.connect(self.compare_wells)
        layout.addWidget(self.compare_btn)
        
        # Botón para fusión manual
        self.merge_btn = QPushButton("🔗 Fusionar Seleccionados")
        self.merge_btn.clicked.connect(self.merge_selected_wells)
        self.merge_btn.setStyleSheet("background-color: #17a2b8; color: white;")  # Color diferente
        layout.addWidget(self.merge_btn)
        
        return tab
    
    def create_analysis_tab(self) -> QWidget:
        """Tab para análisis automático."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Análisis rápido
        quick_group = QGroupBox("🚀 Análisis Rápido")
        quick_layout = QVBoxLayout(quick_group)
        
        self.quick_analysis_btn = QPushButton("📈 Análisis Completo")
        self.quick_analysis_btn.clicked.connect(self.run_quick_analysis)
        quick_layout.addWidget(self.quick_analysis_btn)
        
        self.export_data_btn = QPushButton("📤 Exportar Datos")
        self.export_data_btn.clicked.connect(self.export_current_well)
        quick_layout.addWidget(self.export_data_btn)
        
        layout.addWidget(quick_group)
        
        # Log de actividades
        log_group = QGroupBox("📋 Log de Actividades")
        log_layout = QVBoxLayout(log_group)
        
        self.activity_log = QTextEdit()
        self.activity_log.setMaximumHeight(200)
        self.activity_log.setReadOnly(True)
        self.activity_log.setStyleSheet("background-color: #f0f0f0; font-family: 'Courier New';")
        log_layout.addWidget(self.activity_log)
        
        clear_log_btn = QPushButton("🗑️ Limpiar Log")
        clear_log_btn.clicked.connect(self.clear_activity_log)
        log_layout.addWidget(clear_log_btn)
        
        layout.addWidget(log_group)
        
        return tab
    
    def create_petrophysics_tab(self) -> QWidget:
        """Tab para cálculos petrofísicos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Inicializar calculadoras
        self.vcl_calculator = VclCalculator()
        self.porosity_calculator = PorosityCalculator()
        self.water_saturation_calculator = WaterSaturationCalculator()
        self.permeability_calculator = PermeabilityCalculator()
        self.lithology_analyzer = LithologyAnalyzer()
        
        # Crear tabs para organizar mejor la interfaz
        self.petro_tabs = QTabWidget()
        
        # Tab 1: VCL y Porosidad (básicos)
        basics_tab = self.create_basics_petro_tab()
        self.petro_tabs.addTab(basics_tab, "🏔️ VCL & Porosidad")
        
        # Tab 2: Saturación de Agua
        sw_tab = self.create_water_saturation_tab()
        self.petro_tabs.addTab(sw_tab, "💧 Saturación Agua")
        
        # Tab 3: Permeabilidad
        perm_tab = self.create_permeability_tab()
        self.petro_tabs.addTab(perm_tab, "🌊 Permeabilidad")
        
        # Tab 4: Análisis Litológico
        lithology_tab = self.create_lithology_tab()
        self.petro_tabs.addTab(lithology_tab, "🪨 Litología")
        
        layout.addWidget(self.petro_tabs)
        
        # Resultados globales
        results_group = QGroupBox("📊 Resultados Petrofísicos")
        results_layout = QVBoxLayout(results_group)
        
        self.petro_results = QTextEdit()
        self.petro_results.setMaximumHeight(120)
        self.petro_results.setReadOnly(True)
        self.petro_results.setStyleSheet("background-color: #f8f9fa; font-family: 'Courier New'; font-size: 11px;")
        results_layout.addWidget(self.petro_results)
        
        # Botones de resultados globales
        results_buttons = QHBoxLayout()
        self.plot_petro_btn = QPushButton("📈 Graficar Resultados")
        self.plot_petro_btn.clicked.connect(self.plot_petrophysics_results)
        results_buttons.addWidget(self.plot_petro_btn)
        
        self.export_petro_btn = QPushButton("💾 Exportar Cálculos")
        self.export_petro_btn.clicked.connect(self.export_petrophysics_results)
        results_buttons.addWidget(self.export_petro_btn)
        
        self.comprehensive_analysis_btn = QPushButton("🔬 Análisis Completo")
        self.comprehensive_analysis_btn.clicked.connect(self.run_comprehensive_analysis)
        results_buttons.addWidget(self.comprehensive_analysis_btn)
        
        results_layout.addLayout(results_buttons)
        
        layout.addWidget(results_group)
        
        # Inicialmente deshabilitar botones
        self.update_petrophysics_ui()
        
        return tab

    def create_basics_petro_tab(self) -> QWidget:
        """Crear tab para VCL y Porosidad básica."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # VCL Section
        vcl_group = QGroupBox("🏔️ Volumen de Arcilla (VCL)")
        vcl_layout = QVBoxLayout(vcl_group)
        
        # Método VCL
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Método:"))
        self.vcl_method_combo = QComboBox()
        self.vcl_method_combo.addItems(["linear", "larionov_older", "larionov_tertiary", "clavier", "steiber"])
        method_layout.addWidget(self.vcl_method_combo)
        vcl_layout.addLayout(method_layout)
        
        # Curvas VCL
        curves_layout = QHBoxLayout()
        curves_layout.addWidget(QLabel("Curva GR:"))
        self.vcl_gr_combo = QComboBox()
        curves_layout.addWidget(self.vcl_gr_combo)
        
        curves_layout.addWidget(QLabel("GR min:"))
        self.vcl_gr_min = QSpinBox()
        self.vcl_gr_min.setRange(0, 300)
        self.vcl_gr_min.setValue(15)
        curves_layout.addWidget(self.vcl_gr_min)
        
        curves_layout.addWidget(QLabel("GR max:"))
        self.vcl_gr_max = QSpinBox()
        self.vcl_gr_max.setRange(0, 300)
        self.vcl_gr_max.setValue(150)
        curves_layout.addWidget(self.vcl_gr_max)
        
        vcl_layout.addLayout(curves_layout)
        
        # Botones VCL
        vcl_buttons = QHBoxLayout()
        self.calc_vcl_btn = QPushButton("🧮 Calcular VCL")
        self.calc_vcl_btn.clicked.connect(self.calculate_vcl)
        vcl_buttons.addWidget(self.calc_vcl_btn)
        
        self.show_vcl_info_btn = QPushButton("ℹ️ Info Métodos")
        self.show_vcl_info_btn.clicked.connect(self.show_vcl_method_info)
        vcl_buttons.addWidget(self.show_vcl_info_btn)
        
        vcl_layout.addLayout(vcl_buttons)
        
        layout.addWidget(vcl_group)
        
        # POROSIDAD Section
        por_group = QGroupBox("🕳️ Porosidad Efectiva (PHIE)")
        por_layout = QVBoxLayout(por_group)
        
        # Método Porosidad
        por_method_layout = QHBoxLayout()
        por_method_layout.addWidget(QLabel("Método:"))
        self.por_method_combo = QComboBox()
        self.por_method_combo.addItems(["density", "neutron", "combined"])
        por_method_layout.addWidget(self.por_method_combo)
        por_layout.addLayout(por_method_layout)
        
        # Curvas Porosidad
        por_curves_layout = QHBoxLayout()
        por_curves_layout.addWidget(QLabel("RHOB:"))
        self.por_rhob_combo = QComboBox()
        por_curves_layout.addWidget(self.por_rhob_combo)
        
        por_curves_layout.addWidget(QLabel("NPHI:"))
        self.por_nphi_combo = QComboBox()
        por_curves_layout.addWidget(self.por_nphi_combo)
        
        por_layout.addLayout(por_curves_layout)
        
        # Parámetros
        por_params_layout = QHBoxLayout()
        por_params_layout.addWidget(QLabel("ρma:"))
        self.por_rhoma = QSpinBox()
        self.por_rhoma.setRange(200, 300)
        self.por_rhoma.setValue(265)  # Cuarzo
        por_params_layout.addWidget(self.por_rhoma)
        
        por_params_layout.addWidget(QLabel("ρfl:"))
        self.por_rhofl = QSpinBox()
        self.por_rhofl.setRange(80, 120)
        self.por_rhofl.setValue(100)  # Agua dulce
        por_params_layout.addWidget(self.por_rhofl)
        
        por_layout.addLayout(por_params_layout)
        
        # Correcciones
        corrections_layout = QHBoxLayout()
        self.clay_correction_cb = QCheckBox("Corrección de Arcilla")
        corrections_layout.addWidget(self.clay_correction_cb)
        
        self.gas_correction_cb = QCheckBox("Corrección de Gas")
        corrections_layout.addWidget(self.gas_correction_cb)
        
        por_layout.addLayout(corrections_layout)
        
        # Botones Porosidad
        por_buttons = QHBoxLayout()
        self.calc_por_btn = QPushButton("🧮 Calcular PHIE")
        self.calc_por_btn.clicked.connect(self.calculate_porosity)
        por_buttons.addWidget(self.calc_por_btn)
        
        por_layout.addLayout(por_buttons)
        
        layout.addWidget(por_group)
        
        return tab
    
    def create_water_saturation_tab(self) -> QWidget:
        """Crear tab para cálculos de saturación de agua."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Método de Sw
        method_group = QGroupBox("💧 Método de Saturación de Agua")
        method_layout = QVBoxLayout(method_group)
        
        # Selector de método
        method_select_layout = QHBoxLayout()
        method_select_layout.addWidget(QLabel("Método:"))
        self.sw_method_combo = QComboBox()
        self.sw_method_combo.addItems([
            "archie_simple", "archie_modified", "simandoux", 
            "waxman_smits", "dual_water", "indonesian"
        ])
        self.sw_method_combo.currentTextChanged.connect(self.update_sw_method_info)
        method_select_layout.addWidget(self.sw_method_combo)
        
        self.sw_info_btn = QPushButton("ℹ️ Info")
        self.sw_info_btn.clicked.connect(self.show_sw_method_details)
        method_select_layout.addWidget(self.sw_info_btn)
        
        method_layout.addLayout(method_select_layout)
        
        # Descripción del método
        self.sw_method_description = QLabel("Archie Simple: Sw = ((a*Rw)/(φ^m * Rt))^(1/n)")
        self.sw_method_description.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        method_layout.addWidget(self.sw_method_description)
        
        layout.addWidget(method_group)
        
        # Curvas de entrada
        curves_group = QGroupBox("📊 Curvas de Entrada")
        curves_layout = QVBoxLayout(curves_group)
        
        # Primera fila: RT y Porosidad (siempre necesarios)
        curves_row1 = QHBoxLayout()
        curves_row1.addWidget(QLabel("RT (Resistividad):"))
        self.sw_rt_combo = QComboBox()
        curves_row1.addWidget(self.sw_rt_combo)
        
        curves_row1.addWidget(QLabel("Porosidad:"))
        self.sw_porosity_combo = QComboBox()
        curves_row1.addWidget(self.sw_porosity_combo)
        
        curves_layout.addLayout(curves_row1)
        
        # Segunda fila: VCL (para métodos que lo requieren)
        curves_row2 = QHBoxLayout()
        curves_row2.addWidget(QLabel("VCL (opcional):"))
        self.sw_vcl_combo = QComboBox()
        curves_row2.addWidget(self.sw_vcl_combo)
        
        # Checkbox para usar VCL calculado
        self.sw_use_calculated_vcl = QCheckBox("Usar VCL calculado")
        curves_row2.addWidget(self.sw_use_calculated_vcl)
        
        curves_layout.addLayout(curves_row2)
        
        layout.addWidget(curves_group)
        
        # Parámetros del modelo
        params_group = QGroupBox("⚙️ Parámetros del Modelo")
        params_layout = QVBoxLayout(params_group)
        
        # Parámetros de Archie
        archie_row1 = QHBoxLayout()
        archie_row1.addWidget(QLabel("a (tortuosidad):"))
        self.sw_a_spinbox = QDoubleSpinBox()
        self.sw_a_spinbox.setRange(0.1, 5.0)
        self.sw_a_spinbox.setSingleStep(0.1)
        self.sw_a_spinbox.setValue(1.0)
        archie_row1.addWidget(self.sw_a_spinbox)
        
        archie_row1.addWidget(QLabel("m (cementación):"))
        self.sw_m_spinbox = QDoubleSpinBox()
        self.sw_m_spinbox.setRange(1.0, 3.0)
        self.sw_m_spinbox.setSingleStep(0.1)
        self.sw_m_spinbox.setValue(2.0)
        archie_row1.addWidget(self.sw_m_spinbox)
        
        params_layout.addLayout(archie_row1)
        
        archie_row2 = QHBoxLayout()
        archie_row2.addWidget(QLabel("n (saturación):"))
        self.sw_n_spinbox = QDoubleSpinBox()
        self.sw_n_spinbox.setRange(1.0, 3.0)
        self.sw_n_spinbox.setSingleStep(0.1)
        self.sw_n_spinbox.setValue(2.0)
        archie_row2.addWidget(self.sw_n_spinbox)
        
        archie_row2.addWidget(QLabel("Rw (ohm-m):"))
        self.sw_rw_spinbox = QDoubleSpinBox()
        self.sw_rw_spinbox.setRange(0.01, 1.0)
        self.sw_rw_spinbox.setSingleStep(0.01)
        self.sw_rw_spinbox.setValue(0.05)
        archie_row2.addWidget(self.sw_rw_spinbox)
        
        params_layout.addLayout(archie_row2)
        
        # Parámetros adicionales (para métodos específicos)
        extra_params_row = QHBoxLayout()
        extra_params_row.addWidget(QLabel("Rsh (ohm-m):"))
        self.sw_rsh_spinbox = QDoubleSpinBox()
        self.sw_rsh_spinbox.setRange(0.1, 10.0)
        self.sw_rsh_spinbox.setSingleStep(0.1)
        self.sw_rsh_spinbox.setValue(2.0)
        extra_params_row.addWidget(self.sw_rsh_spinbox)
        
        params_layout.addLayout(extra_params_row)
        
        layout.addWidget(params_group)
        
        # Botones de cálculo
        buttons_layout = QHBoxLayout()
        self.calc_sw_btn = QPushButton("🧮 Calcular Sw")
        self.calc_sw_btn.clicked.connect(self.calculate_water_saturation)
        buttons_layout.addWidget(self.calc_sw_btn)
        
        self.preview_sw_btn = QPushButton("👁️ Vista Previa")
        self.preview_sw_btn.clicked.connect(self.preview_sw_calculation)
        buttons_layout.addWidget(self.preview_sw_btn)
        
        self.reset_sw_params_btn = QPushButton("🔄 Resetear")
        self.reset_sw_params_btn.clicked.connect(self.reset_sw_parameters)
        buttons_layout.addWidget(self.reset_sw_params_btn)
        
        layout.addLayout(buttons_layout)
        
        # Resultados
        results_group = QGroupBox("📋 Resultados Sw")
        results_layout = QVBoxLayout(results_group)
        
        self.sw_results_text = QTextEdit()
        self.sw_results_text.setMaximumHeight(100)
        self.sw_results_text.setReadOnly(True)
        self.sw_results_text.setStyleSheet("background-color: #f8f9fa; font-family: 'Courier New'; font-size: 10px;")
        results_layout.addWidget(self.sw_results_text)
        
        layout.addWidget(results_group)
        
        return tab
    
    def create_permeability_tab(self) -> QWidget:
        """Crear tab para cálculos de permeabilidad."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Método de permeabilidad
        method_group = QGroupBox("🌊 Método de Permeabilidad")
        method_layout = QVBoxLayout(method_group)
        
        method_select_layout = QHBoxLayout()
        method_select_layout.addWidget(QLabel("Método:"))
        self.perm_method_combo = QComboBox()
        self.perm_method_combo.addItems([
            "timur", "kozeny_carman", "wyllie_rose", "coates_denoo", "empirical"
        ])
        self.perm_method_combo.currentTextChanged.connect(self.update_perm_method_info)
        method_select_layout.addWidget(self.perm_method_combo)
        
        self.perm_info_btn = QPushButton("ℹ️ Info")
        self.perm_info_btn.clicked.connect(self.show_perm_method_details)
        method_select_layout.addWidget(self.perm_info_btn)
        
        method_layout.addLayout(method_select_layout)
        
        # Descripción del método
        self.perm_method_description = QLabel("Timur: K = 0.136 * (φ/Swi)^4.4")
        self.perm_method_description.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        method_layout.addWidget(self.perm_method_description)
        
        layout.addWidget(method_group)
        
        # Curvas de entrada
        curves_group = QGroupBox("📊 Curvas de Entrada")
        curves_layout = QVBoxLayout(curves_group)
        
        curves_row1 = QHBoxLayout()
        curves_row1.addWidget(QLabel("Porosidad:"))
        self.perm_porosity_combo = QComboBox()
        curves_row1.addWidget(self.perm_porosity_combo)
        
        curves_row1.addWidget(QLabel("Sw:"))
        self.perm_sw_combo = QComboBox()
        curves_row1.addWidget(self.perm_sw_combo)
        
        curves_layout.addLayout(curves_row1)
        
        # Opciones para usar datos calculados
        calc_options_row = QHBoxLayout()
        self.perm_use_calc_porosity = QCheckBox("Usar porosidad calculada")
        calc_options_row.addWidget(self.perm_use_calc_porosity)
        
        self.perm_use_calc_sw = QCheckBox("Usar Sw calculada")
        calc_options_row.addWidget(self.perm_use_calc_sw)
        
        curves_layout.addLayout(calc_options_row)
        
        layout.addWidget(curves_group)
        
        # Parámetros del modelo
        params_group = QGroupBox("⚙️ Parámetros del Modelo")
        params_layout = QVBoxLayout(params_group)
        
        params_row1 = QHBoxLayout()
        params_row1.addWidget(QLabel("Swi (irreducible):"))
        self.perm_swi_spinbox = QDoubleSpinBox()
        self.perm_swi_spinbox.setRange(0.1, 0.8)
        self.perm_swi_spinbox.setSingleStep(0.05)
        self.perm_swi_spinbox.setValue(0.25)
        params_row1.addWidget(self.perm_swi_spinbox)
        
        params_row1.addWidget(QLabel("Factor C:"))
        self.perm_c_factor_spinbox = QDoubleSpinBox()
        self.perm_c_factor_spinbox.setRange(0.01, 10.0)
        self.perm_c_factor_spinbox.setSingleStep(0.01)
        self.perm_c_factor_spinbox.setValue(0.136)  # Timur por defecto
        params_row1.addWidget(self.perm_c_factor_spinbox)
        
        params_layout.addLayout(params_row1)
        
        params_row2 = QHBoxLayout()
        params_row2.addWidget(QLabel("Exponente φ:"))
        self.perm_phi_exp_spinbox = QDoubleSpinBox()
        self.perm_phi_exp_spinbox.setRange(1.0, 8.0)
        self.perm_phi_exp_spinbox.setSingleStep(0.1)
        self.perm_phi_exp_spinbox.setValue(4.4)
        params_row2.addWidget(self.perm_phi_exp_spinbox)
        
        params_row2.addWidget(QLabel("Exponente Sw:"))
        self.perm_sw_exp_spinbox = QDoubleSpinBox()
        self.perm_sw_exp_spinbox.setRange(-8.0, -1.0)
        self.perm_sw_exp_spinbox.setSingleStep(0.1)
        self.perm_sw_exp_spinbox.setValue(-4.4)
        params_row2.addWidget(self.perm_sw_exp_spinbox)
        
        params_layout.addLayout(params_row2)
        
        layout.addWidget(params_group)
        
        # Botones de cálculo
        buttons_layout = QHBoxLayout()
        self.calc_perm_btn = QPushButton("🧮 Calcular Permeabilidad")
        self.calc_perm_btn.clicked.connect(self.calculate_permeability)
        buttons_layout.addWidget(self.calc_perm_btn)
        
        self.classify_perm_btn = QPushButton("📊 Clasificar")
        self.classify_perm_btn.clicked.connect(self.classify_permeability)
        buttons_layout.addWidget(self.classify_perm_btn)
        
        self.reset_perm_params_btn = QPushButton("🔄 Resetear")
        self.reset_perm_params_btn.clicked.connect(self.reset_perm_parameters)
        buttons_layout.addWidget(self.reset_perm_params_btn)
        
        layout.addLayout(buttons_layout)
        
        # Resultados
        results_group = QGroupBox("📋 Resultados Permeabilidad")
        results_layout = QVBoxLayout(results_group)
        
        self.perm_results_text = QTextEdit()
        self.perm_results_text.setMaximumHeight(100)
        self.perm_results_text.setReadOnly(True)
        self.perm_results_text.setStyleSheet("background-color: #f8f9fa; font-family: 'Courier New'; font-size: 10px;")
        results_layout.addWidget(self.perm_results_text)
        
        layout.addWidget(results_group)
        
        return tab
    
    def create_lithology_tab(self) -> QWidget:
        """Crear tab para análisis litológico."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tipo de análisis
        analysis_group = QGroupBox("🪨 Tipo de Análisis Litológico")
        analysis_layout = QVBoxLayout(analysis_group)
        
        analysis_select_layout = QHBoxLayout()
        analysis_select_layout.addWidget(QLabel("Análisis:"))
        self.lithology_analysis_combo = QComboBox()
        self.lithology_analysis_combo.addItems([
            "crossplots", "facies_classification", "mineral_identification", 
            "reservoir_quality", "depositional_environment"
        ])
        self.lithology_analysis_combo.currentTextChanged.connect(self.update_lithology_analysis_info)
        analysis_select_layout.addWidget(self.lithology_analysis_combo)
        
        self.lithology_info_btn = QPushButton("ℹ️ Info")
        self.lithology_info_btn.clicked.connect(self.show_lithology_analysis_details)
        analysis_select_layout.addWidget(self.lithology_info_btn)
        
        analysis_layout.addLayout(analysis_select_layout)
        
        # Descripción del análisis
        self.lithology_analysis_description = QLabel("Crossplots: Análisis de correlaciones entre propiedades petrofísicas")
        self.lithology_analysis_description.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        analysis_layout.addWidget(self.lithology_analysis_description)
        
        layout.addWidget(analysis_group)
        
        # Curvas requeridas
        curves_group = QGroupBox("📊 Curvas para Análisis")
        curves_layout = QVBoxLayout(curves_group)
        
        # Curvas básicas
        basic_curves_row = QHBoxLayout()
        basic_curves_row.addWidget(QLabel("GR:"))
        self.lith_gr_combo = QComboBox()
        basic_curves_row.addWidget(self.lith_gr_combo)
        
        basic_curves_row.addWidget(QLabel("RHOB:"))
        self.lith_rhob_combo = QComboBox()
        basic_curves_row.addWidget(self.lith_rhob_combo)
        
        basic_curves_row.addWidget(QLabel("NPHI:"))
        self.lith_nphi_combo = QComboBox()
        basic_curves_row.addWidget(self.lith_nphi_combo)
        
        curves_layout.addLayout(basic_curves_row)
        
        # Curvas adicionales
        extra_curves_row = QHBoxLayout()
        extra_curves_row.addWidget(QLabel("PEF:"))
        self.lith_pef_combo = QComboBox()
        extra_curves_row.addWidget(self.lith_pef_combo)
        
        extra_curves_row.addWidget(QLabel("RT:"))
        self.lith_rt_combo = QComboBox()
        extra_curves_row.addWidget(self.lith_rt_combo)
        
        curves_layout.addLayout(extra_curves_row)
        
        # Opciones para usar datos calculados
        calc_options_row = QHBoxLayout()
        self.lith_use_calc_porosity = QCheckBox("Usar porosidad calculada")
        calc_options_row.addWidget(self.lith_use_calc_porosity)
        
        self.lith_use_calc_vcl = QCheckBox("Usar VCL calculado")
        calc_options_row.addWidget(self.lith_use_calc_vcl)
        
        curves_layout.addLayout(calc_options_row)
        
        layout.addWidget(curves_group)
        
        # Parámetros del análisis
        params_group = QGroupBox("⚙️ Parámetros del Análisis")
        params_layout = QVBoxLayout(params_group)
        
        # Cutoffs y rangos
        cutoffs_row1 = QHBoxLayout()
        cutoffs_row1.addWidget(QLabel("VCL cutoff:"))
        self.lith_vcl_cutoff_spinbox = QDoubleSpinBox()
        self.lith_vcl_cutoff_spinbox.setRange(0.1, 0.9)
        self.lith_vcl_cutoff_spinbox.setSingleStep(0.05)
        self.lith_vcl_cutoff_spinbox.setValue(0.5)
        cutoffs_row1.addWidget(self.lith_vcl_cutoff_spinbox)
        
        cutoffs_row1.addWidget(QLabel("φ cutoff:"))
        self.lith_porosity_cutoff_spinbox = QDoubleSpinBox()
        self.lith_porosity_cutoff_spinbox.setRange(0.05, 0.3)
        self.lith_porosity_cutoff_spinbox.setSingleStep(0.01)
        self.lith_porosity_cutoff_spinbox.setValue(0.1)
        cutoffs_row1.addWidget(self.lith_porosity_cutoff_spinbox)
        
        params_layout.addLayout(cutoffs_row1)
        
        # Configuración de clustering
        cluster_row = QHBoxLayout()
        cluster_row.addWidget(QLabel("N° Facies:"))
        self.lith_n_facies_spinbox = QSpinBox()
        self.lith_n_facies_spinbox.setRange(2, 8)
        self.lith_n_facies_spinbox.setValue(4)
        cluster_row.addWidget(self.lith_n_facies_spinbox)
        
        self.lith_auto_facies = QCheckBox("Detectar automáticamente")
        cluster_row.addWidget(self.lith_auto_facies)
        
        params_layout.addLayout(cluster_row)
        
        layout.addWidget(params_group)
        
        # Botones de análisis
        buttons_layout = QHBoxLayout()
        self.analyze_lithology_btn = QPushButton("🔬 Analizar Litología")
        self.analyze_lithology_btn.clicked.connect(self.analyze_lithology)
        buttons_layout.addWidget(self.analyze_lithology_btn)
        
        self.generate_crossplots_btn = QPushButton("📊 Crossplots")
        self.generate_crossplots_btn.clicked.connect(self.generate_lithology_crossplots)
        buttons_layout.addWidget(self.generate_crossplots_btn)
        
        self.classify_facies_btn = QPushButton("🏷️ Clasificar Facies")
        self.classify_facies_btn.clicked.connect(self.classify_facies)
        buttons_layout.addWidget(self.classify_facies_btn)
        
        layout.addLayout(buttons_layout)
        
        # Resultados
        results_group = QGroupBox("📋 Resultados Litológicos")
        results_layout = QVBoxLayout(results_group)
        
        self.lithology_results_text = QTextEdit()
        self.lithology_results_text.setMaximumHeight(100)
        self.lithology_results_text.setReadOnly(True)
        self.lithology_results_text.setStyleSheet("background-color: #f8f9fa; font-family: 'Courier New'; font-size: 10px;")
        results_layout.addWidget(self.lithology_results_text)
        
        layout.addWidget(results_group)
        
        return tab
    
    def create_menus(self):
        """Crear menús."""
        menubar = self.menuBar()
        
        # Archivo
        file_menu = menubar.addMenu('📁 Archivo')
        file_menu.addAction('📂 Abrir Pozo...', self.load_well, 'Ctrl+O')
        file_menu.addAction('📁 Abrir Múltiples...', self.load_multiple_wells, 'Ctrl+Shift+O')
        file_menu.addSeparator()
        file_menu.addAction('💾 Guardar Gráfico...', self.save_current_plot, 'Ctrl+S')
        file_menu.addAction('📤 Exportar Datos...', self.export_current_well, 'Ctrl+E')
        file_menu.addSeparator()
        file_menu.addAction('❌ Salir', self.close, 'Ctrl+Q')
        
        # Ver
        view_menu = menubar.addMenu('👁️ Ver')
        view_menu.addAction('🔄 Actualizar', self.refresh_view, 'F5')
        view_menu.addAction('🔍 Limpiar Gráfico', self.clear_plot)
        
        # Herramientas
        tools_menu = menubar.addMenu('🔧 Herramientas')
        tools_menu.addAction('📈 Análisis Completo', self.run_quick_analysis)
        tools_menu.addAction('⚖️ Comparar Pozos', self.compare_wells)
        tools_menu.addAction('🔗 Fusionar Pozos', self.merge_selected_wells)
        
        # Ayuda
        help_menu = menubar.addMenu('❓ Ayuda')
        help_menu.addAction('📖 Acerca de', self.show_about)
    
    def create_toolbars(self):
        """Crear barras de herramientas."""
        toolbar = self.addToolBar('Principal')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        toolbar.addAction('📂 Abrir', self.load_well)
        toolbar.addAction('📁 Múltiples', self.load_multiple_wells)
        toolbar.addSeparator()
        toolbar.addAction('🎨 Graficar', self.plot_selected_curves)
        toolbar.addAction('💾 Guardar', self.save_current_plot)
        toolbar.addSeparator()
        toolbar.addAction('⚖️ Comparar', self.compare_wells)
        toolbar.addAction('🔄 Actualizar', self.refresh_view)
    
    def create_status_bar(self):
        """Crear barra de estado."""
        self.status_bar = self.statusBar()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Info labels
        self.wells_count_label = QLabel("Pozos: 0")
        self.status_bar.addPermanentWidget(self.wells_count_label)
        
        # Versión y branding
        version_label = QLabel("PyPozo v2.0.0")
        version_label.setStyleSheet("color: #666; font-weight: bold; margin: 0 10px;")
        self.status_bar.addPermanentWidget(version_label)
    
    def apply_professional_style(self):
        """Aplicar estilo profesional."""
        style = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            background-color: white;
        }
        QPushButton {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #218838;
        }
        QPushButton:pressed {
            background-color: #1e7e34;
        }
        QPushButton:disabled {
            background-color: #6c757d;
        }
        QTreeWidget, QListWidget, QTextEdit {
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background-color: white;
            selection-background-color: #007bff;
        }
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e9ecef;
            padding: 10px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-weight: bold;
        }
        QTabBar::tab:selected {
            background-color: #007bff;
            color: white;
        }
        QLabel {
            color: #495057;
        }
        """
        self.setStyleSheet(style)
    
    def setup_logging(self):
        """Configurar logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pypozo_app.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def closeEvent(self, event):
        """Manejar el cierre de la aplicación correctamente."""
        try:
            # Terminar todos los threads activos
            for thread in self.active_threads:
                if thread.isRunning():
                    logger.info(f"🔄 Terminando thread activo...")
                    thread.quit()
                    thread.wait(3000)  # Esperar máximo 3 segundos
                    
                    if thread.isRunning():
                        logger.warning(f"⚠️ Forzando terminación de thread...")
                        thread.terminate()
                        thread.wait(1000)
            
            # Limpiar la lista de threads
            self.active_threads.clear()
            
            logger.info("👋 PyPozo App cerrando correctamente")
            event.accept()
            
        except Exception as e:
            logger.error(f"❌ Error cerrando aplicación: {e}")
            event.accept()  # Cerrar de todas formas
    
    def log_activity(self, message: str):
        """Agregar mensaje al log de actividades."""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.activity_log.append(f"[{timestamp}] {message}")
        # Auto-scroll al final
        cursor = self.activity_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.activity_log.setTextCursor(cursor)
    
    # ========== FUNCIONALIDADES PRINCIPALES ==========
    
    def load_well(self):
        """Cargar un pozo desde archivo LAS."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Abrir Archivo LAS", 
            "",
            "Archivos LAS (*.las *.LAS);;Todos los archivos (*)"
        )
        
        if file_path:
            self.load_well_from_path(file_path)
    
    def load_multiple_wells(self):
        """Cargar múltiples pozos."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Abrir Múltiples Archivos LAS",
            "",
            "Archivos LAS (*.las *.LAS);;Todos los archivos (*)"
        )
        
        if file_paths:
            for file_path in file_paths:
                self.load_well_from_path(file_path)
    
    def load_well_from_path(self, file_path: str):
        """Cargar pozo desde ruta específica."""
        self.log_activity(f"Cargando pozo: {Path(file_path).name}")
        self.progress_bar.setVisible(True)
        
        # Usar thread para no bloquear la GUI
        load_thread = WellLoadThread(file_path)
        load_thread.well_loaded.connect(self.on_well_loaded)
        load_thread.error_occurred.connect(self.on_load_error)
        load_thread.progress_updated.connect(self.progress_bar.setValue)
        
        # Agregar thread a la lista de seguimiento
        self.active_threads.append(load_thread)
        
        # Conectar señal de terminación para limpieza automática
        load_thread.finished.connect(lambda: self._cleanup_thread(load_thread))
        
        load_thread.start()
    
    def on_well_loaded(self, well: WellManager, filename: str):
        """Manejar pozo cargado exitosamente."""
        well_name = well.name or filename
        
        # Verificar si ya existe un pozo con el mismo nombre
        if well_name in self.wells:
            self.log_activity(f"🔄 Detectado pozo duplicado: {well_name}")
            
            # Preguntar al usuario si desea fusionar
            reply = QMessageBox.question(
                self, "Pozo Duplicado Detectado",
                f"Ya existe un pozo con el nombre '{well_name}'.\n\n"
                f"¿Desea fusionar los registros automáticamente?\n\n"
                f"✅ Sí: Combinar registros y promediar traslapes\n"
                f"❌ No: Mantener pozos separados",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._merge_duplicate_wells(well_name, well)
                self.progress_bar.setVisible(False)
                return
            else:
                # Renombrar el nuevo pozo
                counter = 2
                new_name = f"{well_name}_{counter}"
                while new_name in self.wells:
                    counter += 1
                    new_name = f"{well_name}_{counter}"
                
                well_name = new_name
                self.log_activity(f"📝 Pozo renombrado a: {well_name}")
        
        # Agregar pozo (nuevo o renombrado)
        self.wells[well_name] = well
        
        # Agregar al árbol
        item = QTreeWidgetItem(self.wells_tree)
        item.setText(0, well_name)
        item.setData(0, Qt.UserRole, well_name)
        
        # Actualizar UI
        self.update_wells_count()
        self.update_comparison_list()
        self.progress_bar.setVisible(False)
        
        self.log_activity(f"✅ Pozo cargado: {well_name} ({len(well.curves)} curvas)")
        self.status_bar.showMessage(f"Pozo cargado: {well_name}", 3000)
        
        # Seleccionar automáticamente el pozo cargado
        self.wells_tree.setCurrentItem(item)
        self.on_well_selected(item, 0)
    
    def on_load_error(self, error_message: str):
        """Manejar error de carga."""
        self.progress_bar.setVisible(False)
        self.log_activity(f"❌ Error: {error_message}")
        QMessageBox.critical(self, "Error", f"Error cargando pozo:\n{error_message}")
    
    def on_well_selected(self, item: QTreeWidgetItem, column: int = 0):
        """Manejar selección de pozo."""
        well_name = item.data(0, Qt.UserRole)
        if well_name and well_name in self.wells:
            self.current_well = self.wells[well_name]
            self.current_well_name = well_name
            
            # Actualizar panel de propiedades
            self.update_well_properties()
            
            # Actualizar lista de curvas
            self.update_curves_list()
            
            # Actualizar UI de petrofísica
            self.update_petrophysics_ui()
            
            # Habilitar botones
            self.remove_well_btn.setEnabled(True)
            self.plot_btn.setEnabled(True)
            self.plot_together_btn.setEnabled(True)
            self.plot_all_btn.setEnabled(True)
            self.save_plot_btn.setEnabled(True)
            
            self.log_activity(f"📊 Pozo seleccionado: {well_name}")
    
    def update_well_properties(self):
        """Actualizar panel de propiedades del pozo."""
        if not self.current_well:
            self.props_text.clear()
            return
        
        well = self.current_well
        depth_range = well.depth_range
        
        props_text = f"""
<b>Pozo:</b> {well.name}<br>
<b>Archivo:</b> {well.metadata.get('source_file', 'N/A')}<br>
<b>Profundidad:</b> {depth_range[0]:.1f} - {depth_range[1]:.1f} m<br>
<b>Intervalo:</b> {depth_range[1] - depth_range[0]:.1f} m<br>
<b>Curvas disponibles:</b> {len(well.curves)}<br>
<br>
<b>Curvas:</b><br>
"""
        
        for i, curve in enumerate(well.curves, 1):
            curve_data = well.get_curve_data(curve)
            if curve_data is not None:
                props_text += f"{i:2d}. {curve}: {len(curve_data)} puntos<br>"
        
        self.props_text.setHtml(props_text)
        self.current_well_label.setText(f"Pozo: {well.name}")
    
    def update_curves_list(self):
        """Actualizar lista de curvas disponibles."""
        self.curves_list.clear()
        self.compare_curve_combo.clear()
        
        if not self.current_well:
            return
        
        for curve in self.current_well.curves:
            item = QListWidgetItem(curve)
            self.curves_list.addItem(item)
            self.compare_curve_combo.addItem(curve)
        
        self.update_selection_info()
    
    def update_comparison_list(self):
        """Actualizar lista de pozos para comparación."""
        self.compare_list.clear()
        
        for well_name in self.wells.keys():
            item = QListWidgetItem(well_name)
            self.compare_list.addItem(item)
    
    def update_wells_count(self):
        """Actualizar contador de pozos."""
        count = len(self.wells)
        self.wells_count_label.setText(f"Pozos: {count}")
    
    def update_selection_info(self):
        """Actualizar información de selección de curvas."""
        selected_count = len(self.curves_list.selectedItems())
        total_count = self.curves_list.count()
        self.selection_info.setText(f"Curvas seleccionadas: {selected_count}/{total_count}")
    
    def get_selected_curves(self) -> List[str]:
        """Obtener curvas seleccionadas."""
        return [item.text() for item in self.curves_list.selectedItems()]
    
    # ========== FUNCIONES DE SELECCIÓN ==========
    
    def on_curve_selection_changed(self):
        """Manejar cambio en selección de curvas."""
        self.update_selection_info()
    
    def select_all_curves(self):
        """Seleccionar todas las curvas."""
        self.curves_list.selectAll()
        self.update_selection_info()
    
    def select_no_curves(self):
        """Deseleccionar todas las curvas."""
        self.curves_list.clearSelection()
        self.update_selection_info()
    
    def select_basic_curves(self):
        """Seleccionar curvas básicas."""
        basic_curves = ["GR", "SP", "CAL", "RT", "RHOB", "NPHI"]
        self.select_curves_by_names(basic_curves)
    
    def select_petro_curves(self):
        """Seleccionar curvas petrofísicas."""
        petro_curves = ["VCL", "PHIE", "SW", "ZDEN", "VSH", "PHI", "PERM"]
        self.select_curves_by_names(petro_curves)
    
    def select_acoustic_curves(self):
        """Seleccionar curvas acústicas."""
        acoustic_curves = ["DTC", "DTS", "VPVS", "POISDIN", "SPHI"]
        self.select_curves_by_names(acoustic_curves)
    
    def select_electrical_curves(self):
        """Seleccionar curvas eléctricas automáticamente."""
        if not self.current_well:
            return
        
        electrical_curves = []
        for curve in self.current_well.curves:
            if self.plotter._is_electrical_curve(curve, self.current_well):
                electrical_curves.append(curve)
        
        if electrical_curves:
            self.select_curves_by_names(electrical_curves)
            self.log_activity(f"⚡ Curvas eléctricas seleccionadas: {', '.join(electrical_curves)}")
        else:
            self.log_activity("⚠️ No se encontraron curvas eléctricas")
            QMessageBox.information(self, "Información", "No se encontraron curvas eléctricas en el pozo actual.")

    def select_curves_by_names(self, curve_names: List[str]):
        """Seleccionar curvas por nombres."""
        self.curves_list.clearSelection()
        
        for i in range(self.curves_list.count()):
            item = self.curves_list.item(i)
            if item.text() in curve_names:
                item.setSelected(True)
        
        self.update_selection_info()
    
    # ========== FUNCIONES DE GRAFICADO ==========
    
    def plot_selected_curves(self):
        """Graficar curvas seleccionadas."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero.")
            return
        
        selected_curves = self.get_selected_curves()
        if not selected_curves:
            QMessageBox.warning(self, "Advertencia", "Seleccione al menos una curva.")
            return
        
        self.log_activity(f"🎨 Graficando {len(selected_curves)} curvas: {', '.join(selected_curves)}")
        
        try:
            # Limpiar figura anterior
            self.figure.clear()
            
            # Crear gráfico
            self._plot_curves_to_figure(selected_curves)
            
            self.log_activity(f"✅ Gráfico creado exitosamente")
            
        except Exception as e:
            self.log_activity(f"❌ Error graficando: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error creando gráfico:\n{str(e)}")
    
    def plot_all_curves(self):
        """Graficar todas las curvas del pozo."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero.")
            return
        
        all_curves = self.current_well.curves
        self.log_activity(f"📊 Graficando todas las curvas ({len(all_curves)})")
        
        try:
            # Limpiar figura anterior
            self.figure.clear()
            
            # Limitar a máximo 8 curvas para mantener legibilidad
            curves_to_plot = all_curves[:8]
            if len(all_curves) > 8:
                self.log_activity(f"⚠️ Mostrando solo las primeras 8 de {len(all_curves)} curvas")
            
            self._plot_curves_to_figure(curves_to_plot)
            
            self.log_activity(f"✅ Gráfico completo creado")
            
        except Exception as e:
            self.log_activity(f"❌ Error graficando: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error creando gráfico:\n{str(e)}")
    
    def plot_curves_together(self):
        """Graficar múltiples curvas en el mismo subplot."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero.")
            return
        
        selected_curves = self.get_selected_curves()
        if not selected_curves:
            QMessageBox.warning(self, "Advertencia", "Seleccione al menos una curva.")
            return
        
        # Preguntar si se quiere normalizar los valores
        normalize_reply = QMessageBox.question(
            self, 
            "Normalización de Curvas",
            "¿Desea normalizar las curvas de 0 a 1 para mejor visualización?\n\n"
            "• Sí: Normaliza todas las curvas entre 0 y 1 (recomendado para curvas con diferentes rangos)\n"
            "• No: Mantiene los valores originales",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        normalize = (normalize_reply == QMessageBox.Yes)
        
        self.log_activity(f"🎨 Graficando {len(selected_curves)} curvas juntas: {', '.join(selected_curves)}")
        if normalize:
            self.log_activity("📏 Normalizando valores de 0 a 1")
        else:
            self.log_activity("📊 Manteniendo valores originales")
        
        try:
            # Limpiar figura anterior
            self.figure.clear()
            
            # Crear un solo subplot para todas las curvas
            ax = self.figure.add_subplot(111)
            
            # Colores para las curvas
            colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00', '#8B4513', '#00CED1', '#9932CC', '#FF1493']
            
            # Obtener datos del pozo
            try:
                df = self.current_well._well.df()
            except Exception as e:
                self.log_activity(f"❌ Error obteniendo datos: {str(e)}")
                return
            
            # Verificar que tenemos datos
            if df.empty:
                self.log_activity("❌ No hay datos disponibles en el pozo")
                return
            
            # Graficar cada curva
            for i, curve_name in enumerate(selected_curves):
                if curve_name in df.columns:
                    curve_data = df[curve_name].dropna()
                    
                    if len(curve_data) == 0:
                        self.log_activity(f"⚠️ Curva {curve_name} no tiene datos válidos")
                        continue
                    
                    depth = curve_data.index
                    values = curve_data.values
                    
                    # Verificar que no hay valores infinitos o NaN
                    valid_mask = np.isfinite(values) & np.isfinite(depth)
                    if not np.any(valid_mask):
                        self.log_activity(f"⚠️ Curva {curve_name} no tiene valores finitos")
                        continue
                    
                    valid_depth = depth[valid_mask]
                    valid_values = values[valid_mask]
                    
                    # Aplicar normalización si se solicitó
                    if normalize and len(valid_values) > 1:
                        min_val = valid_values.min()
                        max_val = valid_values.max()
                        if max_val > min_val:  # Evitar división por cero
                            values_to_plot = (valid_values - min_val) / (max_val - min_val)
                        else:
                            values_to_plot = valid_values
                    else:
                        values_to_plot = valid_values
                    
                    # Graficar
                    color = colors[i % len(colors)]
                    ax.plot(values_to_plot, valid_depth, linewidth=1.5, color=color, label=curve_name, alpha=0.8)
                else:
                    self.log_activity(f"⚠️ Curva {curve_name} no encontrada en los datos")
            
            # Configurar ejes
            if normalize:
                ax.set_xlabel('Valores Normalizados (0-1)', fontsize=11, fontweight='bold')
            else:
                ax.set_xlabel('Valores Originales', fontsize=11, fontweight='bold')
            
            ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
            ax.set_title(f'Curvas Combinadas - {self.current_well.name}', fontsize=14, fontweight='bold')
            ax.invert_yaxis()  # Profundidad hacia abajo
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            
            # Ajustar layout
            self.figure.tight_layout()
            
            # Actualizar canvas
            self.canvas.draw()
            
            self.log_activity(f"✅ Gráfico combinado creado exitosamente")
            
        except Exception as e:
            self.log_activity(f"❌ Error graficando curvas juntas: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error creando gráfico combinado:\n{str(e)}")
    
    def _plot_curves_to_figure(self, curves: List[str]):
        """Graficar curvas en la figura actual."""
        well = self.current_well
        n_curves = len(curves)
        
        # Obtener datos del pozo
        try:
            df = well._well.df()
        except Exception as e:
            self.log_activity(f"❌ Error obteniendo datos: {str(e)}")
            return
        
        # Verificar que tenemos datos
        if df.empty:
            self.log_activity("❌ No hay datos disponibles en el pozo")
            return
        
        # Limpiar la figura completamente antes de crear nuevos subplots
        self.figure.clf()
        
        # Colores profesionales
        colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00', '#8B4513', '#00CED1', '#9932CC', '#FF1493']
        
        # Determinar el rango de profundidad común para todos los subplots
        all_depths = []
        valid_curves = []
        
        # Primero, recopilar todos los datos válidos y sus rangos de profundidad
        for curve_name in curves:
            if curve_name in df.columns:
                curve_data = df[curve_name].dropna()
                
                if len(curve_data) == 0:
                    self.log_activity(f"⚠️ Curva {curve_name} no tiene datos válidos")
                    continue
                
                depth = curve_data.index
                values = curve_data.values
                
                # Verificar que no hay valores infinitos o NaN
                valid_mask = np.isfinite(values) & np.isfinite(depth)
                if not np.any(valid_mask):
                    self.log_activity(f"⚠️ Curva {curve_name} no tiene valores finitos")
                    continue
                
                valid_depth = depth[valid_mask]
                valid_values = values[valid_mask]
                
                all_depths.extend(valid_depth)
                valid_curves.append((curve_name, valid_depth, valid_values))
            else:
                self.log_activity(f"⚠️ Curva {curve_name} no encontrada en los datos")
        
        if not valid_curves:
            self.log_activity("❌ No se encontraron curvas válidas para graficar")
            return
        
        # Calcular el rango de profundidad común (union de todos los rangos)
        common_depth_min = min(all_depths)
        common_depth_max = max(all_depths)
        
        self.log_activity(f"📊 Rango de profundidad común: {common_depth_min:.1f} - {common_depth_max:.1f} m")
        
        # Crear subplots con eje Y compartido
        axes = []
        for i, (curve_name, depth, values) in enumerate(valid_curves):
            if i == 0:
                # Primer subplot
                ax = self.figure.add_subplot(1, len(valid_curves), i + 1)
                axes.append(ax)
            else:
                # Subplots subsecuentes comparten el eje Y
                ax = self.figure.add_subplot(1, len(valid_curves), i + 1, sharey=axes[0])
                axes.append(ax)
            
            # Graficar
            color = colors[i % len(colors)]
            ax.plot(values, depth, linewidth=1.5, color=color, label=curve_name)
            ax.fill_betweenx(depth, values, alpha=0.3, color=color)
            
            # Obtener unidades para la etiqueta (solo unidades, no repetir nombre)
            units = well.get_curve_units(curve_name)
            xlabel = f'({units})' if units else 'Valores'
            
            # Configurar ejes
            ax.set_xlabel(xlabel, fontsize=11, fontweight='bold')
            ax.set_title(curve_name, fontsize=12, fontweight='bold', pad=10)
            ax.invert_yaxis()  # Profundidad hacia abajo
            ax.grid(True, alpha=0.3)
            
            # Establecer el rango de profundidad común para todos los subplots
            ax.set_ylim(common_depth_max, common_depth_min)  # Invertido para profundidad
            
            # Estadísticas
            stats_text = f'N: {len(values)}\nMin: {values.min():.1f}\nMax: {values.max():.1f}\nμ: {values.mean():.1f}'
            
            ax.text(0.02, 0.02, stats_text, transform=ax.transAxes,
                   verticalalignment='bottom', horizontalalignment='left',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9),
                   fontsize=8, fontfamily='monospace')
            
            # Solo el primer subplot tiene etiqueta Y completa y valores de profundidad
            if i == 0:
                ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
                # Asegurar que se muestren los valores de profundidad
                ax.tick_params(axis='y', labelsize=10)
            else:
                # Los otros subplots NO muestran valores de profundidad para visualización más limpia
                ax.tick_params(axis='y', labelsize=10, labelleft=False)
                # Solo ocultar el label del eje Y y los valores
                ax.set_ylabel('')
        
        # Título principal con más espacio
        title = f'{well.name} | Profundidad: {common_depth_min:.0f}-{common_depth_max:.0f}m | {len(valid_curves)} curvas'
        self.figure.suptitle(title, fontsize=14, fontweight='bold', y=0.95)
        
        # Ajustar layout de forma segura con más espacio arriba
        try:
            self.figure.tight_layout()
            self.figure.subplots_adjust(top=0.85)  # Más espacio para el título
        except Exception as e:
            self.log_activity(f"⚠️ Warning en layout: {str(e)}")
        
        # Actualizar canvas
        self.canvas.draw()
    
    def clear_plot(self):
        """Limpiar el gráfico actual."""
        self.figure.clear()
        self.canvas.draw()
        self.log_activity("🧹 Gráfico limpiado")
    
    def save_current_plot(self):
        """Guardar el gráfico actual."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay gráfico para guardar.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Gráfico",
            f"{self.current_well.name}_plot.png",
            "PNG (*.png);;PDF (*.pdf);;SVG (*.svg);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                self.log_activity(f"💾 Gráfico guardado: {Path(file_path).name}")
                self.status_bar.showMessage(f"Gráfico guardado: {Path(file_path).name}", 3000)
            except Exception as e:
                self.log_activity(f"❌ Error guardando: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error guardando gráfico:\n{str(e)}")
    
    # ========== FUNCIONES DE COMPARACIÓN ==========
    
    def compare_wells(self):
        """Comparar pozos seleccionados."""
        selected_wells = [item.text() for item in self.compare_list.selectedItems()]
        
        if len(selected_wells) < 2:
            QMessageBox.warning(self, "Advertencia", "Seleccione al menos 2 pozos para comparar.")
            return
        
        curve = self.compare_curve_combo.currentText()
        if not curve:
            QMessageBox.warning(self, "Advertencia", "Seleccione una curva para comparar.")
            return
        
        self.log_activity(f"⚖️ Comparando {len(selected_wells)} pozos en curva {curve}")
        
        try:
            # Limpiar figura
            self.figure.clear()
            
            # Crear gráfico de comparación
            ax = self.figure.add_subplot(111)
            
            colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00', '#8B4513', '#00CED1', '#9932CC']
            
            for i, well_name in enumerate(selected_wells):
                well = self.wells[well_name]
                curve_data = well.get_curve_data(curve)
                
                if curve_data is not None:
                    color = colors[i % len(colors)]
                    depth = curve_data.index
                    values = curve_data.values
                    
                    # Filtrar valores válidos
                    valid_mask = np.isfinite(values) & np.isfinite(depth)
                    if np.any(valid_mask):
                        ax.plot(values[valid_mask], depth[valid_mask], 
                               linewidth=1.5, color=color, label=well_name, alpha=0.8)
                    else:
                        self.log_activity(f"⚠️ {well_name}: No hay datos válidos para {curve}")
                else:
                    self.log_activity(f"⚠️ {well_name}: Curva {curve} no encontrada")
                    color = colors[i % len(colors)]
                    ax.plot(curve_data.values, curve_data.index,
                           color=color, linewidth=1.5, label=well_name, alpha=0.8)
            
            ax.set_xlabel(curve, fontsize=12, fontweight='bold')
            ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
            ax.set_title(f'Comparación de {curve}', fontsize=14, fontweight='bold')
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            
            self.figure.tight_layout()
           
           
           

            self.canvas.draw()
            
            self.log_activity(f"✅ Comparación completada")
            
        except Exception as e:
            self.log_activity(f"❌ Error comparando: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error comparando pozos:\n{str(e)}")
    
    # ========== FUNCIONES DE ANÁLISIS Y EXPORTACIÓN ==========
    
    def run_quick_analysis(self):
        """Ejecutar análisis rápido del pozo actual."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        
        try:
            self.log_activity(f"📈 Iniciando análisis rápido de {self.current_well.name}")
            
            well = self.current_well
            analysis_results = []
            
            # Información básica
            analysis_results.append("=== ANÁLISIS RÁPIDO ===\n")
            analysis_results.append(f"Pozo: {well.name}")
            analysis_results.append(f"Profundidad: {well.depth_range[0]:.1f} - {well.depth_range[1]:.1f} m")
            analysis_results.append(f"Intervalo: {well.depth_range[1] - well.depth_range[0]:.1f} m")
            analysis_results.append(f"Curvas disponibles: {len(well.curves)}")
            
            # Análisis de curvas
            analysis_results.append(f"\n=== ANÁLISIS DE CURVAS ===")
            
            for curve in well.curves[:10]:  # Solo las primeras 10
                curve_data = well.get_curve_data(curve)
                if curve_data is not None and len(curve_data) > 0:
                    analysis_results.append(f"{curve}:")
                    analysis_results.append(f"  • Puntos: {len(curve_data)}")
                    analysis_results.append(f"  • Rango: {curve_data.min():.2f} - {curve_data.max():.2f}")
                    analysis_results.append(f"  • Promedio: {curve_data.mean():.2f}")
            
            # Identificar curvas especiales
            analysis_results.append(f"\n=== CURVAS IDENTIFICADAS ===")
            
            # Curvas básicas
            basic_curves = ["GR", "SP", "CAL", "RT", "RHOB", "NPHI"]
            found_basic = [c for c in basic_curves if c in well.curves]
            if found_basic:
                analysis_results.append(f"Básicas: {', '.join(found_basic)}")
            
            # Curvas petrofísicas
            petro_curves = [c for c in well.curves if any(k in c.upper() for k in ['VCL', 'PHIE', 'SW'])]
            if petro_curves:
                analysis_results.append(f"Petrofísicas: {', '.join(petro_curves)}")
            
            # Mostrar resultados en un diálogo
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Análisis Rápido - {well.name}")
            dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            text_widget = QTextEdit()
            text_widget.setReadOnly(True)
            text_widget.setFont(QFont("Courier New", 10))
            text_widget.setPlainText("\n".join(analysis_results))
            layout.addWidget(text_widget)
            
            close_btn = QPushButton("Cerrar")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec_()
            
            self.log_activity(f"✅ Análisis rápido completado")
            
        except Exception as e:
            self.log_activity(f"❌ Error en análisis rápido: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en análisis rápido:\n{str(e)}")
    
    def export_current_well(self):
        """Exportar datos del pozo actual."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        
        # Seleccionar archivo de salida
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Pozo",
            f"{self.current_well.name}_export.las",
            "Archivos LAS (*.las);;Archivos CSV (*.csv);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.las'):
                    # Exportar como LAS
                    success = self.current_well.export_to_las(file_path)
                    if not success:
                        raise Exception("La exportación a LAS falló")
                elif file_path.endswith('.csv'):
                    # Exportar como CSV
                    self.current_well.data.to_csv(file_path, index=True)
                else:
                    # Por defecto, intentar LAS
                    success = self.current_well.export_to_las(file_path)
                    if not success:
                        raise Exception("La exportación a LAS falló")
                
                self.log_activity(f"📤 Pozo exportado: {Path(file_path).name}")
                QMessageBox.information(self, "Éxito", f"Pozo exportado a:\n{file_path}")
                
            except Exception as e:
                self.log_activity(f"❌ Error exportando: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error exportando pozo:\n{str(e)}")
    
    def clear_activity_log(self):
        """Limpiar el log de actividades."""
        self.activity_log.clear()
        self.log_activity("🗑️ Log de actividades limpiado")
    
    def refresh_view(self):
        """Refrescar toda la vista."""
        if self.current_well:
            self.update_well_properties()
            self.update_curves_list()
            self.update_petrophysics_ui()
            self.update_selection_info()
            self.log_activity("🔄 Vista actualizada")
        else:
            self.log_activity("⚠️ No hay pozo seleccionado para actualizar")
    
    def show_about(self):
        """Mostrar información sobre la aplicación."""
        about_text = """
<h2>PyPozo App 2.0</h2>
<p><b>Análisis Profesional de Pozos</b></p>
<p>Versión: 2.0.0<br>
Autor: José María García Márquez<br>
Fecha: Julio 2025</p>

<p><b>Características principales:</b></p>
<ul>
<li>Visualización avanzada de registros</li>
<li>Cálculos petrofísicos completos</li>
<li>Comparación y fusión de pozos</li>
<li>Workflows automatizados</li>
<li>Exportación a múltiples formatos</li>
</ul>

<p><b>Módulos implementados:</b></p>
<ul>
<li>✅ VCL (Volumen de Arcilla)</li>
<li>✅ PHIE (Porosidad Efectiva)</li>
<li>✅ Análisis Litológico</li>
<li>🔄 SW (Saturación de Agua) - Próximamente</li>
<li>🔄 Permeabilidad - Próximamente</li>
</ul>

<p><i>Alternativa Open Source profesional a WellCAD</i></p>
        """
        
        QMessageBox.about(self, "Acerca de PyPozo App", about_text)

    # ==================== MÉTODOS PETROFÍSICOS ====================
    
    def calculate_vcl(self):
        """Calcular volumen de arcilla (VCL)."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Obtener parámetros de la UI
            method = self.vcl_method_combo.currentText()
            gr_curve = self.vcl_gr_combo.currentText()
            gr_min = self.vcl_gr_min.value()
            gr_max = self.vcl_gr_max.value()
            
            if not gr_curve or gr_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva GR '{gr_curve}' no encontrada")
                return
            
            # Realizar cálculo
            vcl_result = self.vcl_calculator.calculate(
                gamma_ray=self.current_well.data[gr_curve],
                method=method,
                gr_clean=gr_min,
                gr_clay=gr_max
            )
            
            # Agregar resultado al pozo
            vcl_name = f"VCL_{method.upper()}"
            success = self.current_well.add_curve(
                curve_name=vcl_name,
                data=vcl_result['vcl'],
                units='fraction',
                description=f'Volume of clay calculated using {method} method'
            )
            
            if not success:
                QMessageBox.critical(self, "Error", f"No se pudo agregar la curva {vcl_name}")
                return
            
            # Mostrar resultados
            self.petro_results.clear()
            self.petro_results.append(f"✅ VCL calculado usando método: {method}")
            self.petro_results.append(f"📊 Curva creada: {vcl_name}")
            self.petro_results.append(f"📈 Estadísticas:")
            
            vcl_data = vcl_result['vcl']
            valid_vcl = vcl_data[~np.isnan(vcl_data)]
            
            if len(valid_vcl) > 0:
                self.petro_results.append(f"   • Promedio: {valid_vcl.mean():.3f}")
                self.petro_results.append(f"   • Mediana: {np.median(valid_vcl):.3f}")
                self.petro_results.append(f"   • Mín: {valid_vcl.min():.3f}")
                self.petro_results.append(f"   • Máx: {valid_vcl.max():.3f}")
            else:
                self.petro_results.append(f"   • No hay datos válidos para estadísticas")
                
            self.petro_results.append(f"🔧 Parámetros:")
            self.petro_results.append(f"   • GR limpia: {gr_min} API")
            self.petro_results.append(f"   • GR arcilla: {gr_max} API")
            
            # Mostrar QC si hay advertencias
            if 'warnings' in vcl_result and vcl_result['warnings']:
                self.petro_results.append(f"\n⚠️ Advertencias QC:")
                for warning in vcl_result['warnings']:
                    self.petro_results.append(f"   • {warning}")
            
            self.log_activity(f"🧮 VCL calculado: {vcl_name} (método: {method})")
            self.update_curves_list()
            
        except Exception as e:
            self.log_activity(f"❌ Error calculando VCL: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error calculando VCL:\n{str(e)}")
    
    def calculate_porosity(self):
        """Calcular porosidad efectiva (PHIE)."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Obtener parámetros de la UI
            method = self.por_method_combo.currentText()
            rhob_curve = self.por_rhob_combo.currentText()
            nphi_curve = self.por_nphi_combo.currentText()
            rhoma = self.por_rhoma.value() / 100.0  # Convertir a g/cc
            rhofl = self.por_rhofl.value() / 100.0  # Convertir a g/cc
            
            # Validar curvas según método
            if method in ["density", "combined"] and (not rhob_curve or rhob_curve not in self.current_well.data.columns):
                QMessageBox.warning(self, "Advertencia", f"Curva RHOB '{rhob_curve}' no encontrada")
                return
            
            if method in ["neutron", "combined"] and (not nphi_curve or nphi_curve not in self.current_well.data.columns):
                QMessageBox.warning(self, "Advertencia", f"Curva NPHI '{nphi_curve}' no encontrada")
                return
            
            # Preparar datos
            kwargs = {
                'matrix_density': rhoma,
                'fluid_density': rhofl
            }
            
            if method == "density":
                result = self.porosity_calculator.calculate_density_porosity(
                    bulk_density=self.current_well.data[rhob_curve],
                    **kwargs
                )
                phie_name = "PHIE_RHOB"
                porosity_key = 'phid'
                
            elif method == "neutron":
                result = self.porosity_calculator.calculate_neutron_porosity(
                    neutron_porosity=self.current_well.data[nphi_curve]
                )
                phie_name = "PHIE_NPHI"
                porosity_key = 'phin'
                
            elif method == "combined":
                result = self.porosity_calculator.calculate_density_neutron_porosity(
                    bulk_density=self.current_well.data[rhob_curve],
                    neutron_porosity=self.current_well.data[nphi_curve],
                    **kwargs
                )
                phie_name = "PHIE_COMBINED"
                porosity_key = 'phie'
            
            # Aplicar correcciones si están habilitadas
            if self.clay_correction_cb.isChecked():
                # Buscar curva VCL existente
                vcl_curves = [col for col in self.current_well.data.columns if 'VCL' in col.upper()]
                if vcl_curves:
                    vcl_curve = vcl_curves[0]  # Usar la primera encontrada
                    result = self.porosity_calculator.apply_clay_correction(
                        result, self.current_well.data[vcl_curve]
                    )
                    phie_name += "_CLAY_CORR"
                    self.petro_results.append(f"🔧 Corrección de arcilla aplicada usando: {vcl_curve}")
                else:
                    QMessageBox.warning(self, "Advertencia", "No se encontró curva VCL para corrección de arcilla")
            
            if self.gas_correction_cb.isChecked():
                # Aplicar corrección de gas genérica
                result = self.porosity_calculator.apply_gas_correction(result)
                phie_name += "_GAS_CORR"
                self.petro_results.append(f"🔧 Corrección de gas aplicada")
            
            # Determinar la clave de porosidad a usar (prioritizar correcciones)
            if 'porosity_corrected' in result and self.clay_correction_cb.isChecked():
                porosity_key = 'porosity_corrected'
            elif 'phie_corrected' in result and self.clay_correction_cb.isChecked():
                porosity_key = 'phie_corrected'
            elif 'porosity_gas_corrected' in result and self.gas_correction_cb.isChecked():
                porosity_key = 'porosity_gas_corrected'
            elif 'phie_gas_corrected' in result and self.gas_correction_cb.isChecked():
                porosity_key = 'phie_gas_corrected'
            elif 'phie' in result:
                porosity_key = 'phie'
            else:
                porosity_key = 'porosity'
            
            # Agregar resultado al pozo
            success = self.current_well.add_curve(
                curve_name=phie_name,
                data=result[porosity_key],
                units='fraction',
                description=f'Effective porosity calculated using {method} method'
            )
            
            if not success:
                QMessageBox.critical(self, "Error", f"No se pudo agregar la curva {phie_name}")
                return
            
            # Mostrar resultados
            self.petro_results.clear()
            self.petro_results.append(f"✅ Porosidad calculada usando método: {method}")
            self.petro_results.append(f"📊 Curva creada: {phie_name}")
            self.petro_results.append(f"📈 Estadísticas:")
            
            porosity_data = result[porosity_key]
            valid_por = porosity_data[~np.isnan(porosity_data)]
            
            if len(valid_por) > 0:
                self.petro_results.append(f"   • Promedio: {valid_por.mean():.3f}")
                self.petro_results.append(f"   • Mediana: {np.median(valid_por):.3f}")
                self.petro_results.append(f"   • Mín: {valid_por.min():.3f}")
                self.petro_results.append(f"   • Máx: {valid_por.max():.3f}")
            else:
                self.petro_results.append(f"   • No hay datos válidos para estadísticas")
                
            self.petro_results.append(f"🔧 Parámetros:")
            self.petro_results.append(f"   • ρma: {rhoma:.2f} g/cc")
            self.petro_results.append(f"   • ρfl: {rhofl:.2f} g/cc")
            
            # Mostrar QC si hay advertencias
            if 'warnings' in result and result['warnings']:
                self.petro_results.append(f"\n⚠️ Advertencias QC:")
                for warning in result['warnings']:
                    self.petro_results.append(f"   • {warning}")
            
            self.log_activity(f"🧮 Porosidad calculada: {phie_name} (método: {method})")
            self.update_curves_list()
            
        except Exception as e:
            self.log_activity(f"❌ Error calculando porosidad: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error calculando porosidad:\n{str(e)}")
    
    def show_vcl_method_info(self):
        """Mostrar información sobre los métodos de VCL."""
        info = self.vcl_calculator.get_method_info()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Información de Métodos VCL")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        text = QTextEdit()
        text.setReadOnly(True)
        text.setFont(QFont("Courier New", 10))
        
        content = "🧮 MÉTODOS DE CÁLCULO DE VCL\n\n"
        
        for method in info['available_methods']:
            content += f"📌 {method.upper()}:\n"
            if method in info['descriptions']:
                content += f"   Descripción: {info['descriptions'][method]}\n"
            if method in info['recommendations']:
                content += f"   Uso recomendado: {info['recommendations'][method]}\n\n"
        
        content += "\n📚 REFERENCIAS:\n"
        content += "• Larionov (1969): The Interpretation of Well Logs\n"
        content += "• Clavier et al. (1971): Theoretical and Experimental Bases for GR Log Interpretation\n"
        content += "• Steiber (1973): Optimization of Shale Volume from GR Log\n"
        
        text.setPlainText(content)
        layout.addWidget(text)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def analyze_lithology(self):
        """Realizar análisis litológico básico."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Buscar curvas disponibles
            rhob_curve = self.por_rhob_combo.currentText()
            nphi_curve = self.por_nphi_combo.currentText()
            
            if not rhob_curve or rhob_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", "Curva RHOB no disponible para análisis")
                return
            
            if not nphi_curve or nphi_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", "Curva NPHI no disponible para análisis")
                return
            
            # Calcular porosidades para análisis litológico
            rhob_data = self.current_well.data[rhob_curve].values
            nphi_data = self.current_well.data[nphi_curve].values
            
            # Calcular porosidad densidad (usando parámetros por defecto)
            phid_result = self.porosity_calculator.calculate_density_porosity(
                bulk_density=rhob_data,
                matrix_density=2.65,  # Arenisca por defecto
                fluid_density=1.0
            )
            
            # Obtener recomendaciones litológicas
            litho_analysis = self.porosity_calculator.get_lithology_recommendations(
                phid=phid_result['porosity'], 
                phin=nphi_data
            )
            
            # Mostrar resultados
            result_text = "🪨 ANÁLISIS LITOLÓGICO AUTOMÁTICO\n\n"
            result_text += f"Litología dominante: {litho_analysis['dominant_lithology']}\n"
            result_text += f"Confianza: {litho_analysis['confidence']:.1%}\n\n"
            
            result_text += "📊 DISTRIBUCIÓN LITOLÓGICA:\n"
            for litho, percentage in litho_analysis['lithology_distribution'].items():
                result_text += f"• {litho.capitalize()}: {percentage:.1%}\n"
            
            result_text += f"\n🎯 DENSIDAD DE MATRIZ RECOMENDADA:\n"
            result_text += f"• {litho_analysis['recommended_matrix_density']:.2f} g/cc\n"
            
            result_text += f"\n📋 RECOMENDACIONES:\n"
            for rec in litho_analysis['recommendations']:
                result_text += f"• {rec}\n"
                
            QMessageBox.information(self, "Análisis Litológico", result_text)
            
            self.log_activity(f"ℹ️ Análisis litológico manual solicitado")
            
        except Exception as e:
            self.log_activity(f"❌ Error en análisis litológico: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en análisis litológico:\n{str(e)}")
    
    def plot_petrophysics_results(self):
        """Graficar resultados petrofísicos."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Buscar curvas petrofísicas calculadas
            petro_curves = []
            for col in self.current_well.data.columns:
                if any(keyword in col.upper() for keyword in ['VCL', 'PHIE']):
                    petro_curves.append(col)
            
            if not petro_curves:
                QMessageBox.warning(self, "Advertencia", "No hay resultados petrofísicos para graficar")
                return
            
            # Limpiar figura actual
            self.figure.clear()
            
            # Crear subplots
            n_curves = len(petro_curves)
            if n_curves == 1:
                ax = self.figure.add_subplot(111)
                axes = [ax]
            else:
                axes = []
                for i, curve in enumerate(petro_curves):
                    ax = self.figure.add_subplot(1, n_curves, i + 1)
                    axes.append(ax)
            
            # Graficar cada curva
            for ax, curve in zip(axes, petro_curves):
                depth = self.current_well.data.index
                values = self.current_well.data[curve]
                
                # Color según tipo de curva
                if 'VCL' in curve.upper():
                    color = 'brown'
                    ax.set_xlabel('VCL (fracción)')
                elif 'PHIE' in curve.upper():
                    color = 'blue'
                    ax.set_xlabel('PHIE (fracción)')
                else:
                    color = 'green'
                    ax.set_xlabel(curve)
                
                ax.plot(values, depth, color=color, linewidth=1.5, label=curve)
                ax.set_ylabel('Profundidad (m)')
                ax.set_title(f'{curve}', fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.invert_yaxis()
                
                # Estadísticas en el gráfico
                mean_val = values.mean()
                ax.axvline(mean_val, color='red', linestyle='--', alpha=0.7, label=f'Media: {mean_val:.3f}')
                ax.legend(fontsize=10)
            
            # Título general
            self.figure.suptitle(f'Resultados Petrofísicos - {self.current_well.name}', 
                               fontsize=14, fontweight='bold')
            
            # Ajustar layout
            self.figure.tight_layout()
            
            # Actualizar canvas
            self.canvas.draw()
            
            self.log_activity(f"📈 Resultados petrofísicos graficados")
            
        except Exception as e:
            self.log_activity(f"❌ Error graficando resultados petrofísicos: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error graficando resultados:\n{str(e)}")
    
    def export_petrophysics_results(self):
        """Exportar resultados petrofísicos."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Buscar curvas petrofísicas calculadas
            petro_curves = []
            for col in self.current_well.data.columns:
                if any(keyword in col.upper() for keyword in ['VCL', 'PHIE']):
                    petro_curves.append(col)
            
            if not petro_curves:
                QMessageBox.warning(self, "Advertencia", "No hay resultados petrofísicos para exportar")
                return
            
            # Seleccionar archivo de salida
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Resultados Petrofísicos",
                f"{self.current_well.name}_petrofisica.las",
                "Archivos LAS (*.las);;Archivos CSV (*.csv)"
            )
            
            if not filename:
                return
            
            # Preparar datos para exportar
            export_data = self.current_well.data[petro_curves].copy()
            
            if filename.endswith('.las'):
                # Exportar como LAS
                self.current_well.export_to_las(filename, curves=petro_curves)
                
            elif filename.endswith('.csv'):
                # Exportar como CSV
                export_data.to_csv(filename, index=True)
            
            self.log_activity(f"💾 Resultados petrofísicos exportados: {Path(filename).name}")
            QMessageBox.information(self, "Éxito", f"Resultados exportados a:\n{filename}")
            
        except Exception as e:
            self.log_activity(f"❌ Error exportando resultados petrofísicos: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error exportando resultados:\n{str(e)}")
    
    def update_petrophysics_ui(self):
        """Actualizar UI de petrofísica según el pozo actual."""
        if not self.current_well:
            # Deshabilitar controles si no hay pozo
            self.calc_vcl_btn.setEnabled(False)
            self.calc_por_btn.setEnabled(False)
            self.analyze_lithology_btn.setEnabled(False)
            self.plot_petro_btn.setEnabled(False)
            self.export_petro_btn.setEnabled(False)
            # Nuevas pestañas
            if hasattr(self, 'calc_sw_btn'):
                self.calc_sw_btn.setEnabled(False)
            if hasattr(self, 'calc_perm_btn'):
                self.calc_perm_btn.setEnabled(False)
            return
        
        # Habilitar controles
        self.calc_vcl_btn.setEnabled(True)
        self.calc_por_btn.setEnabled(True)
        self.analyze_lithology_btn.setEnabled(True)
        self.plot_petro_btn.setEnabled(True)
        self.export_petro_btn.setEnabled(True)
        # Nuevas pestañas
        if hasattr(self, 'calc_sw_btn'):
            self.calc_sw_btn.setEnabled(True)
        if hasattr(self, 'calc_perm_btn'):
            self.calc_perm_btn.setEnabled(True)
        
        try:
            # Actualizar combos de curvas - with error handling
            self.log_activity("🔄 Actualizando UI de petrofísica...")
            
            # Get curves safely
            curves = []
            if hasattr(self.current_well, 'curves'):
                curves = list(self.current_well.curves)
            else:
                # Fallback: try to get from data.columns
                try:
                    curves = list(self.current_well.data.columns)
                except Exception as e:
                    self.log_activity(f"⚠️ Error obteniendo curvas: {str(e)}")
                    curves = []
            
            self.log_activity(f"📊 Curvas encontradas: {len(curves)}")
            
            # VCL - buscar curva GR
            self.vcl_gr_combo.clear()
            gr_curves = [c for c in curves if 'GR' in c.upper()]
            self.vcl_gr_combo.addItems(gr_curves)
            
            # Porosidad - buscar curvas RHOB y NPHI
            self.por_rhob_combo.clear()
            self.por_nphi_combo.clear()
            
            rhob_curves = [c for c in curves if any(keyword in c.upper() for keyword in ['RHOB', 'DEN'])]
            nphi_curves = [c for c in curves if any(keyword in c.upper() for keyword in ['NPHI', 'NEU'])]
            
            self.por_rhob_combo.addItems(rhob_curves)
            self.por_nphi_combo.addItems(nphi_curves)
            
            # Actualizar combos de saturación de agua
            if hasattr(self, 'sw_rt_combo'):
                self.sw_rt_combo.clear()
                self.sw_porosity_combo.clear()
                self.sw_vcl_combo.clear()
                
                rt_curves = [c for c in curves if any(keyword in c.upper() for keyword in ['RT', 'RES', 'ILD', 'LLD'])]
                porosity_curves = [c for c in curves if any(keyword in c.upper() for keyword in ['PHIE', 'NPHI', 'RHOB'])]
                vcl_curves = [c for c in curves if any(keyword in c.upper() for keyword in ['VCL', 'VSH', 'GR'])]
                
                self.sw_rt_combo.addItems(rt_curves)
                self.sw_porosity_combo.addItems(porosity_curves)
                self.sw_vcl_combo.addItems([''] + vcl_curves)  # Opcional
            
            # Actualizar combos de permeabilidad
            if hasattr(self, 'perm_porosity_combo'):
                self.perm_porosity_combo.clear()
                self.perm_sw_combo.clear()
                
                porosity_curves = [c for c in curves if any(keyword in c.upper() for keyword in ['PHIE', 'NPHI', 'RHOB'])]
                sw_curves = [c for c in curves if 'SW' in c.upper()]
                
                self.perm_porosity_combo.addItems(porosity_curves)
                self.perm_sw_combo.addItems([''] + sw_curves)  # Opcional
            
            # Actualizar combos de litología
            if hasattr(self, 'lith_gr_combo'):
                self.lith_gr_combo.clear()
                self.lith_rhob_combo.clear()
                self.lith_nphi_combo.clear()
                self.lith_pef_combo.clear()
                self.lith_rt_combo.clear()
                
                pef_curves = [c for c in curves if 'PEF' in c.upper()]
                
                self.lith_gr_combo.addItems([''] + gr_curves)
                self.lith_rhob_combo.addItems([''] + rhob_curves)
                self.lith_nphi_combo.addItems([''] + nphi_curves)
                self.lith_pef_combo.addItems([''] + pef_curves)
                self.lith_rt_combo.addItems([''] + rt_curves)
            
            self.log_activity("✅ UI de petrofísica actualizada")
            
        except Exception as e:
            self.log_activity(f"❌ Error actualizando UI de petrofísica: {str(e)}")
            # En caso de error, al menos deshabilitar los combos básicos
            self.vcl_gr_combo.clear()
            self.por_rhob_combo.clear()
            self.por_nphi_combo.clear()
    
    # ==================== FIN MÉTODOS PETROFÍSICOS ====================
    
    def update_well_view(self):
        """Actualizar toda la vista del pozo después de cambios."""
        self.update_curves_list()
        self.update_petrophysics_ui()
        self.update_selection_info()
    
    # ========== GESTIÓN DE POZOS ==========
    
    def remove_well(self):
        """Remover el pozo seleccionado."""
        if not self.current_well_name:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de eliminar el pozo '{self.current_well_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remover del diccionario
            if self.current_well_name in self.wells:
                del self.wells[self.current_well_name]
            
            # Remover del árbol
            current_item = self.wells_tree.currentItem()
            if current_item:
                index = self.wells_tree.indexOfTopLevelItem(current_item)
                self.wells_tree.takeTopLevelItem(index)
            
            # Limpiar selección actual
            self.current_well = None
            self.current_well_name = ""
            
            # Actualizar UI
            self.update_wells_count()
            self.update_comparison_list()
            self.update_well_properties()
            self.update_curves_list()
            self.update_petrophysics_ui()
            
            # Deshabilitar botones
            self.remove_well_btn.setEnabled(False)
            self.plot_btn.setEnabled(False)
            self.plot_together_btn.setEnabled(False)
            self.plot_all_btn.setEnabled(False)
            self.save_plot_btn.setEnabled(False)
            
            self.log_activity(f"🗑️ Pozo eliminado: {self.current_well_name}")
    
    def clear_all_wells(self):
        """Limpiar todos los pozos cargados."""
        if not self.wells:
            QMessageBox.information(self, "Información", "No hay pozos cargados")
            return
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self, "Confirmar Limpieza",
            f"¿Está seguro de eliminar todos los pozos cargados ({len(self.wells)})?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Limpiar todo
            self.wells.clear()
            self.wells_tree.clear()
            self.current_well = None

            self.current_well_name = ""
            
            # Actualizar UI
            self.update_wells_count()
            self.update_comparison_list()
            self.update_well_properties()
            self.update_curves_list()
            self.update_petrophysics_ui()
            
            # Deshabilitar botones
            self.remove_well_btn.setEnabled(False)
            self.plot_btn.setEnabled(False)
            self.plot_together_btn.setEnabled(False)
            self.plot_all_btn.setEnabled(False)
            self.save_plot_btn.setEnabled(False)
            
            # Limpiar gráfico
            self.figure.clear()
            self.canvas.draw()
            
            self.log_activity(f"🗃️ Todos los pozos eliminados")
    
    def merge_selected_wells(self):
        """Fusionar pozos seleccionados utilizando fusión real de datos."""
        selected_wells = [item.text() for item in self.compare_list.selectedItems()]
        
        if len(selected_wells) < 2:
            QMessageBox.warning(self, "Advertencia", "Seleccione al menos 2 pozos para fusionar.")
            return
        
        # Obtener nombre para el pozo fusionado
        merged_name, ok = QInputDialog.getText(
            self, "Nombre del Pozo Fusionado",
            "Ingrese el nombre para el pozo fusionado:",
            text=f"MERGED_{'_'.join(selected_wells[:2])}"
        )
        
        if not ok or not merged_name:
            return
        
        try:
            # Verificar que no exista ya un pozo con ese nombre
            if merged_name in self.wells:
                QMessageBox.warning(self, "Advertencia", f"Ya existe un pozo con el nombre '{merged_name}'")
                return
            
            self.log_activity(f"🔗 Iniciando fusión de {len(selected_wells)} pozos...")
            
            # Obtener la lista de pozos a fusionar
            wells_to_merge = []
            for well_name in selected_wells:
                if well_name in self.wells:
                    wells_to_merge.append(self.wells[well_name])
            
            if len(wells_to_merge) < 2:
                QMessageBox.warning(self, "Error", "No se pudieron obtener todos los pozos seleccionados.")
                return
            
            self.log_activity(f"📊 Pozos a fusionar: {[w.name for w in wells_to_merge]}")
            
            # Realizar la fusión real usando el método de WellDataFrame
            from src.pypozo.core.well import WellDataFrame
            merged_well = WellDataFrame.merge_wells(wells_to_merge, merged_name)
            
            if merged_well is None:
                QMessageBox.critical(self, "Error", "Error durante la fusión de pozos.")
                return
            
            # Agregar el pozo fusionado al diccionario
            self.wells[merged_name] = merged_well
            
            # Agregar al árbol
            item = QTreeWidgetItem(self.wells_tree)
            item.setText(0, merged_name)
            item.setData(0, Qt.UserRole, merged_name)
            
            # Actualizar listas
            self.update_wells_count()
            self.update_comparison_list()
            
            # Mostrar información de la fusión
            depth_range = merged_well.depth_range
            self.log_activity(f"✅ Pozos fusionados exitosamente:")
            self.log_activity(f"   📋 Nombre: {merged_name}")
            self.log_activity(f"   📊 Curvas: {len(merged_well.curves)}")
            self.log_activity(f"   🎯 Rango: {depth_range[0]:.1f}-{depth_range[1]:.1f}m")
            
            # Preguntar si desea guardar el pozo fusionado
            save_reply = QMessageBox.question(
                self, "Fusión Exitosa",
                f"Pozos fusionados exitosamente:\n\n"
                f"📋 Nombre: {merged_name}\n"
                f"📊 Curvas: {len(merged_well.curves)}\n"
                f"🎯 Rango: {depth_range[0]:.1f}-{depth_range[1]:.1f}m\n\n"
                f"¿Desea guardar el pozo fusionado como archivo LAS?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if save_reply == QMessageBox.Yes:
                # Seleccionar archivo de salida
                output_file, _ = QFileDialog.getSaveFileName(
                    self,
                    "Guardar Pozo Fusionado",
                    f"{merged_name}.las",
                    "Archivos LAS (*.las);;Todos los archivos (*)"
                )
                
                if output_file:
                    success = merged_well.export_to_las(output_file)
                    if success:
                        self.log_activity(f"💾 Pozo fusionado guardado en: {output_file}")
                        QMessageBox.information(
                            self,
                            "✅ Guardado",
                            f"El pozo fusionado se guardó exitosamente en:\n{output_file}"
                        )
                    else:
                        self.log_activity(f"❌ Error guardando pozo fusionado")
                        QMessageBox.warning(
                            self, "Error de Guardado",
                            "No se pudo guardar el pozo fusionado.\nRevisar log para más detalles."
                        )
            else:
                QMessageBox.information(
                    self, "Fusión Completada",
                    f"Pozo fusionado creado: {merged_name}\n\n"
                    f"Puede exportarlo posteriormente usando:\n"
                    f"Menú → Archivo → Exportar Datos"
                )
            
        except Exception as e:
            self.log_activity(f"❌ Error fusionando pozos: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error fusionando pozos:\n{str(e)}")
    
    def remove_well(self):
        """Remover pozo seleccionado."""
        if not self.current_well_name:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de que desea remover el pozo '{self.current_well_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remover del diccionario
            del self.wells[self.current_well_name]
            
            # Remover del árbol
            item = self.wells_tree.currentItem()
            if item:
                self.wells_tree.takeTopLevelItem(self.wells_tree.indexOfTopLevelItem(item))
            
            # Limpiar selección actual
            self.current_well = None
            self.current_well_name = ""
            
            # Actualizar UI
            self.update_wells_count()
            self.update_comparison_list()
            self.props_text.clear()
            self.curves_list.clear()
            self.current_well_label.setText("Seleccione un pozo")
            
            # Deshabilitar botones
            self.remove_well_btn.setEnabled(False)
            self.plot_btn.setEnabled(False)
            self.plot_together_btn.setEnabled(False)
            self.plot_all_btn.setEnabled(False)
            self.save_plot_btn.setEnabled(False)
            
            self.log_activity(f"🗑️ Pozo removido: {self.current_well_name}")
    
    def clear_all_wells(self):
        """Limpiar todos los pozos."""
        if not self.wells:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Limpieza",
            f"¿Está seguro de que desea remover todos los pozos ({len(self.wells)})?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.wells.clear()
            self.wells_tree.clear()
            self.current_well = None
            self.current_well_name = ""
            
            # Actualizar UI
            self.update_wells_count()
            self.update_comparison_list()
            self.props_text.clear()
            self.curves_list.clear()
            self.current_well_label.setText("Seleccione un pozo")
            
            # Deshabilitar botones
            self.remove_well_btn.setEnabled(False)
            self.plot_btn.setEnabled(False)
            self.plot_together_btn.setEnabled(False)
            self.plot_all_btn.setEnabled(False)
            self.save_plot_btn.setEnabled(False)
            
            # Limpiar gráfico
            self.figure.clear()
            self.canvas.draw()
            
            self.log_activity(f"🗃️ Todos los pozos removidos")
    
    def _cleanup_thread(self, thread):
        """Limpiar thread terminado de la lista de seguimiento."""
        try:
            if thread in self.active_threads:
                self.active_threads.remove(thread)
                logger.info(f"🧹 Thread limpiado de la lista de seguimiento")
        except Exception as e:
            logger.warning(f"⚠️ Error limpiando thread: {e}")
    
    def _merge_duplicate_wells(self, existing_name: str, new_well: WellManager):
        """Fusionar pozo duplicado con el existente."""
        try:
            existing_well = self.wells[existing_name]
            
            # Usar la lógica de fusión real
            self.log_activity(f"🔄 Fusionando datos de {existing_name}...")
            
            # Fusionar los pozos usando la lógica de WellDataFrame (classmethod)
            from src.pypozo.core.well import WellDataFrame
            merged_well = WellDataFrame.merge_wells([existing_well, new_well], existing_name)
            
            # Reemplazar el pozo existente con la versión fusionada
            self.wells[existing_name] = merged_well
            
            # Actualizar la interfaz de usuario
            self.update_wells_count()
            self.update_well_properties()
            
            self.log_activity(f"✅ Pozo {existing_name} fusionado exitosamente")
            
            # Preguntar si quiere guardar el resultado
            self._prompt_save_after_merge(existing_name, merged_well)
            
        except Exception as e:
            self.log_activity(f"❌ Error fusionando pozos: {e}")
            logger.error(f"Error en _merge_duplicate_wells: {e}")
    
    def _prompt_save_after_merge(self, well_name: str, merged_well: WellManager):
        """Preguntar al usuario si quiere guardar después de fusionar."""
        try:
            reply = QMessageBox.question(
                self,
                "💾 Guardar Fusión",
                f"¿Desea guardar el pozo fusionado '{well_name}' en un archivo LAS?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Usar el método de exportación existente
                if hasattr(merged_well, 'export_to_las'):
                    # Generar nombre de archivo sugerido
                    suggested_name = f"{well_name}_MERGED.las"
                    file_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Guardar Pozo Fusionado",
                        suggested_name,
                        "LAS files (*.las);;All files (*.*)"
                    )
                    
                    if file_path:
                        merged_well.export_to_las(file_path)
                        self.log_activity(f"💾 Pozo fusionado guardado en: {file_path}")
                        QMessageBox.information(
                            self,
                            "✅ Guardado",
                            f"El pozo fusionado se guardó exitosamente en:\n{file_path}"
                        )
                else:
                    self.log_activity("❌ Error: El pozo fusionado no tiene método de exportación")
                    
        except Exception as e:
            self.log_activity(f"❌ Error guardando pozo fusionado: {e}")
            logger.error(f"Error en _prompt_save_after_merge: {e}")

# ==================== MÉTODOS PLACEHOLDERS ADICIONALES ====================

    def calculate_water_saturation(self):
        """Calcular saturación de agua (placeholder)."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        self.log_activity("💧 Función de saturación de agua en desarrollo")
        QMessageBox.information(self, "Desarrollo", "Función de saturación de agua en desarrollo")
    
    def calculate_permeability(self):
        """Calcular permeabilidad (placeholder)."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        self.log_activity("🌊 Función de permeabilidad en desarrollo")
        QMessageBox.information(self, "Desarrollo", "Función de permeabilidad en desarrollo")
    
    def analyze_lithology(self):
        """Analizar litología (placeholder)."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        self.log_activity("🪨 Función de análisis litológico en desarrollo")
        QMessageBox.information(self, "Desarrollo", "Función de análisis litológico en desarrollo")
    
    # Métodos auxiliares para las nuevas pestañas
    def update_sw_method_info(self):
        """Actualizar descripción del método de saturación de agua."""
        method = self.sw_method_combo.currentText() if hasattr(self, 'sw_method_combo') else "archie_simple"
        descriptions = {
            'archie_simple': 'Archie Simple: Sw = ((a*Rw)/(φ^m * Rt))^(1/n)',
            'archie_modified': 'Archie con Vclay: Sw = ((a*Rw)/(φe^m * Rt))^(1/n)',
            'simandoux': 'Simandoux: Para formaciones arcillosas (modelo paralelo)',
            'waxman_smits': 'Waxman-Smits: Para formaciones con arcillas conductivas',
            'dual_water': 'Dual Water: Modelo de dos aguas (libre y ligada)',
            'indonesian': 'Ecuación Indonesa: Para formaciones fracturadas'
        }
        if hasattr(self, 'sw_method_description'):
            self.sw_method_description.setText(descriptions.get(method, "Método no implementado"))
    
    def show_sw_method_details(self):
        """Mostrar detalles del método de saturación de agua."""
        QMessageBox.information(self, "Info Sw", "Detalles de métodos de saturación de agua en desarrollo")
    
    def preview_sw_calculation(self):
        """Vista previa del cálculo de Sw."""
        QMessageBox.information(self, "Vista Previa", "Vista previa de Sw en desarrollo")
    
    def reset_sw_parameters(self):
        """Resetear parámetros de Sw a valores por defecto."""
        if hasattr(self, 'sw_a_spinbox'):
            self.sw_a_spinbox.setValue(1.0)
        if hasattr(self, 'sw_m_spinbox'):
            self.sw_m_spinbox.setValue(2.0)
        if hasattr(self, 'sw_n_spinbox'):
            self.sw_n_spinbox.setValue(2.0)
        if hasattr(self, 'sw_rw_spinbox'):
            self.sw_rw_spinbox.setValue(0.05)
        if hasattr(self, 'sw_rsh_spinbox'):
            self.sw_rsh_spinbox.setValue(2.0)
        self.log_activity("🔄 Parámetros Sw reseteados")
    
    def update_perm_method_info(self):
        """Actualizar descripción del método de permeabilidad."""
        method = self.perm_method_combo.currentText() if hasattr(self, 'perm_method_combo') else "timur"
        descriptions = {
            'timur': 'Timur: K = C * (φ/Swi)^n',
            'kozeny_carman': 'Kozeny-Carman: K = C * φ³/(1-φ)²',
            'wyllie_rose': 'Wyllie & Rose: K = C * φ⁶/Swi²',
            'coates_denoo': 'Coates & Denoo: K = C * (φ⁴/Swi²)',
            'empirical': 'Empírico: K = C * φᵃ * Swᵇ'
        }
        if hasattr(self, 'perm_method_description'):
            self.perm_method_description.setText(descriptions.get(method, "Método no implementado"))
    
    def show_perm_method_details(self):
        """Mostrar detalles del método de permeabilidad."""
        QMessageBox.information(self, "Info Permeabilidad", "Detalles de métodos de permeabilidad en desarrollo")
    
    def classify_permeability(self):
        """Clasificar valores de permeabilidad."""
        QMessageBox.information(self, "Clasificación", "Clasificación de permeabilidad en desarrollo")
    
    def reset_perm_parameters(self):
        """Resetear parámetros de permeabilidad."""
        if hasattr(self, 'perm_swi_spinbox'):
            self.perm_swi_spinbox.setValue(0.25)
        if hasattr(self, 'perm_c_factor_spinbox'):
            self.perm_c_factor_spinbox.setValue(0.136)
        if hasattr(self, 'perm_phi_exp_spinbox'):
            self.perm_phi_exp_spinbox.setValue(4.4)
        if hasattr(self, 'perm_sw_exp_spinbox'):
            self.perm_sw_exp_spinbox.setValue(-4.4)
        self.log_activity("🔄 Parámetros permeabilidad reseteados")
    
    def update_lithology_analysis_info(self):
        """Actualizar descripción del análisis litológico."""
        analysis = self.lithology_analysis_combo.currentText() if hasattr(self, 'lithology_analysis_combo') else "crossplots"
        descriptions = {
            'crossplots': 'Crossplots: Análisis de correlaciones entre propiedades petrofísicas',
            'facies_classification': 'Clasificación de Facies: Agrupamiento automático por propiedades',
            'mineral_identification': 'Identificación Mineral: Interpretación basada en registros',
            'reservoir_quality': 'Calidad de Reservorio: Evaluación integrada de propiedades',
            'depositional_environment': 'Ambiente Deposicional: Interpretación sedimentológica'
        }
        if hasattr(self, 'lithology_analysis_description'):
            self.lithology_analysis_description.setText(descriptions.get(analysis, "Análisis no implementado"))
    
    def show_lithology_analysis_details(self):
        """Mostrar detalles del análisis litológico."""
        QMessageBox.information(self, "Info Litología", "Detalles de análisis litológico en desarrollo")
    
    def generate_lithology_crossplots(self):
        """Generar crossplots litológicos."""
        QMessageBox.information(self, "Crossplots", "Generación de crossplots en desarrollo")
    
    def classify_facies(self):
        """Clasificar facies litológicas."""
        QMessageBox.information(self, "Facies", "Clasificación de facies en desarrollo")
    
    def run_comprehensive_analysis(self):
        """Ejecutar análisis petrofísico completo."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        self.log_activity("� Función de análisis completo en desarrollo")
        QMessageBox.information(self, "Desarrollo", "Función de análisis completo en desarrollo")


if __name__ == "__main__":
    if not PYQT5_AVAILABLE:
        print("❌ PyQt5 no está disponible. Instale PyQt5 para usar la GUI: pip install PyQt5")
        sys.exit(1)
    app = QApplication(sys.argv)
    window = PyPozoApp()
    window.show()
    sys.exit(app.exec_())
