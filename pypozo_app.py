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
import pandas as pd
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

# Detección de DLC Patreon
def check_patreon_dlc():
    """Verificar si el DLC de Patreon está disponible."""
    dlc_path = Path(__file__).parent / "patreon_dlc"
    return dlc_path.exists() and (dlc_path / "__init__.py").exists()

def load_patreon_features():
    """Cargar características de Patreon si están disponibles."""
    if check_patreon_dlc():
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent / "patreon_dlc"))
            import neural_completion
            return neural_completion
        except ImportError:
            return None
    return None

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
        
        # Variables para controlar visibilidad de paneles
        self.left_panel_visible = True
        self.right_panel_visible = True
        self.normal_sizes = [250, 1100, 250]  # Tamaños normales
        
        # Verificar DLC de Patreon
        self.patreon_dlc = load_patreon_features()
        self.has_patreon_dlc = self.patreon_dlc is not None
        
        self.init_ui()
        self.setup_logging()
        
        if self.has_patreon_dlc:
            logger.info("🌟 DLC Patreon detectado - Funciones avanzadas habilitadas")
        else:
            logger.info("ℹ️ DLC Patreon no encontrado - Solo funciones básicas")
        
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
        
        # Paneles
        left_panel = self.create_left_panel()
        center_panel = self.create_center_panel()
        right_panel = self.create_right_panel()
        
        # Guardar referencias para controlar visibilidad
        self.left_panel = left_panel
        self.center_panel = center_panel
        self.right_panel = right_panel
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter = main_splitter  # Guardar referencia
        main_layout.addWidget(main_splitter)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        
        # Configurar proporciones - Balance normal con opción de colapsar paneles
        main_splitter.setSizes([250, 1100, 250])
        
        # Configurar política de redimensionamiento para evitar cambios automáticos de ventana
        main_splitter.setChildrenCollapsible(True)
        main_splitter.setStretchFactor(0, 0)  # Panel izquierdo no se estira
        main_splitter.setStretchFactor(1, 1)  # Panel central se estira
        main_splitter.setStretchFactor(2, 0)  # Panel derecho no se estira
        
        # Crear menús y barras
        self.create_menus()
        self.setup_patreon_menu()  # Agregar menú DLC
        self.create_toolbars()
        self.create_status_bar()
        
        # Aplicar estilo
        self.apply_professional_style()
        
        # Inicializar UI de petrofísica
        self.update_petrophysics_ui()
    
    def create_left_panel(self) -> QWidget:
        """Panel izquierdo - Explorador de pozos."""
        panel = QWidget()
        panel.setMinimumWidth(0)  # Permitir colapso completo
        layout = QVBoxLayout(panel)
        
        # Título compacto
        title = QLabel("📁 Pozos")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #2E8B57; margin: 5px;")
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
        
        # Botones de colapsar paneles - lado izquierdo
        self.toggle_left_btn = QPushButton("◀")
        self.toggle_left_btn.setToolTip("Ocultar/Mostrar panel izquierdo")
        self.toggle_left_btn.setFixedSize(25, 25)
        self.toggle_left_btn.clicked.connect(self.toggle_left_panel)
        self.toggle_left_btn.setStyleSheet("background-color: #6c757d; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(self.toggle_left_btn)
        
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
        
        # Botón de colapsar panel derecho - lado derecho
        self.toggle_right_btn = QPushButton("▶")
        self.toggle_right_btn.setToolTip("Ocultar/Mostrar panel derecho")
        self.toggle_right_btn.setFixedSize(25, 25)
        self.toggle_right_btn.clicked.connect(self.toggle_right_panel)
        self.toggle_right_btn.setStyleSheet("background-color: #6c757d; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(self.toggle_right_btn)
        
        # Botón para maximizar gráficas (ocultar ambos paneles)
        self.maximize_plot_btn = QPushButton("⛶")
        self.maximize_plot_btn.setToolTip("Maximizar área de gráficas (ocultar/mostrar ambos paneles)")
        self.maximize_plot_btn.setFixedSize(25, 25)
        self.maximize_plot_btn.clicked.connect(self.toggle_both_panels)
        self.maximize_plot_btn.setStyleSheet("background-color: #17a2b8; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(self.maximize_plot_btn)
        
        layout.addWidget(header_frame)
        
        # Canvas de matplotlib
        self.figure = Figure(figsize=(14, 10))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Panel derecho - Herramientas."""
        panel = QWidget()
        panel.setObjectName("rightPanel")
        panel.setMinimumWidth(0)  # Permitir colapso completo
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)  # Márgenes normales
        layout.setSpacing(5)  # Espaciado normal
        
        # Título
        title = QLabel("🔧 Herramientas")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #2E8B57; margin: 5px;")
        layout.addWidget(title)
        
        # Tabs - Configuración normal
        self.tools_tabs = QTabWidget()
        
        # Configuración normal de pestañas
        self.tools_tabs.setTabPosition(QTabWidget.North)
        self.tools_tabs.setUsesScrollButtons(True)
        
        # Aplicar estilo normal a las pestañas
        self.tools_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                min-width: 80px;
                min-height: 20px;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
                border: 1px solid #0056b3;
            }
            QTabBar::tab:hover {
                background-color: #17a2b8;
                color: white;
            }
        """)
        
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
        
        # Tab 5: Premium DLC
        premium_tab = self.create_premium_dlc_tab()
        self.tools_tabs.addTab(premium_tab, "🌟 Premium IA")
        
        layout.addWidget(self.tools_tabs)
        
        return panel
    
    def create_curves_tab(self) -> QWidget:
        """Tab para selección de curvas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)  # Márgenes normales
        layout.setSpacing(5)  # Espaciado normal
        
        # Información del pozo actual
        self.current_well_label = QLabel("Pozo actual:")
        self.current_well_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.current_well_label)
        
        # Lista de curvas
        curves_label = QLabel("Curvas disponibles:")
        curves_label.setFont(QFont("Arial", 9, QFont.Bold))
        layout.addWidget(curves_label)
        
        self.curves_list = QListWidget()
        self.curves_list.setSelectionMode(QListWidget.MultiSelection)
        self.curves_list.itemSelectionChanged.connect(self.on_curve_selection_changed)
        layout.addWidget(self.curves_list)
        
        # Botones de selección rápida
        quick_frame = QFrame()
        quick_layout = QVBoxLayout(quick_frame)
        quick_layout.setContentsMargins(2, 2, 2, 2)
        quick_layout.setSpacing(3)
        
        # Primera fila
        row1 = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Seleccionar Todo")
        self.select_all_btn.setToolTip("Seleccionar todas las curvas")
        self.select_all_btn.clicked.connect(self.select_all_curves)
        row1.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("❌ Deseleccionar")
        self.select_none_btn.setToolTip("Deseleccionar todas las curvas")
        self.select_none_btn.clicked.connect(self.select_no_curves)
        row1.addWidget(self.select_none_btn)
        
        quick_layout.addLayout(row1)
        
        # Segunda fila - Presets
        row2 = QHBoxLayout()
        
        self.select_basic_btn = QPushButton("📊 Curvas Básicas")
        self.select_basic_btn.setToolTip("Seleccionar curvas básicas (GR, RT, NPHI, RHOB)")
        self.select_basic_btn.clicked.connect(self.select_basic_curves)
        row2.addWidget(self.select_basic_btn)
        
        self.select_petro_btn = QPushButton("🔬 Petrofísicas")
        self.select_petro_btn.setToolTip("Seleccionar curvas petrofísicas")
        self.select_petro_btn.clicked.connect(self.select_petro_curves)
        row2.addWidget(self.select_petro_btn)
        
        quick_layout.addLayout(row2)
        
        # Tercera fila
        row3 = QHBoxLayout()
        
        self.select_acoustic_btn = QPushButton("🔊 Acústicas")
        self.select_acoustic_btn.setToolTip("Seleccionar curvas acústicas (DT, DTS)")
        self.select_acoustic_btn.clicked.connect(self.select_acoustic_curves)
        row3.addWidget(self.select_acoustic_btn)
        
        self.select_electrical_btn = QPushButton("⚡ Eléctricas")
        self.select_electrical_btn.setToolTip("Seleccionar curvas eléctricas (RT, SP)")
        self.select_electrical_btn.clicked.connect(self.select_electrical_curves)
        row3.addWidget(self.select_electrical_btn)
        
        quick_layout.addLayout(row3)
        
        layout.addWidget(quick_frame)
        
        # Info de selección
        self.selection_info = QLabel("Curvas seleccionadas: 0")
        self.selection_info.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
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
        
        # Separador visual
        layout.addWidget(QLabel(""))
        
        # Botón Premium para Completado Inteligente - siempre visible
        if self.has_patreon_dlc:
            self.premium_completion_btn = QPushButton("🤖 Completado Intra-Pozo IA - ¡ACTIVO!")
            self.premium_completion_btn.clicked.connect(self.open_neural_completion)
            self.premium_completion_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 13px;")
        else:
            self.premium_completion_btn = QPushButton("🤖 Completado Intra-Pozo IA ✨ ¡DESBLOQUEAR!")
            self.premium_completion_btn.clicked.connect(self.show_patreon_invitation)
            self.premium_completion_btn.setStyleSheet("background-color: #ff6b35; color: white; font-weight: bold; padding: 12px; font-size: 13px; border: 2px solid #ffd700;")
        
        layout.addWidget(self.premium_completion_btn)
        
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
        
        # Análisis Premium con IA - siempre visible
        premium_group = QGroupBox("🌟 Análisis Premium con IA")
        premium_layout = QVBoxLayout(premium_group)
        
        if self.has_patreon_dlc:
            self.premium_analysis_btn = QPushButton("🧠 Interpretación Automática IA - ¡ACTIVO!")
            self.premium_analysis_btn.clicked.connect(self.open_advanced_analysis)
            self.premium_analysis_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 13px;")
        else:
            self.premium_analysis_btn = QPushButton("🧠 Interpretación Automática IA ✨ ¡DESBLOQUEAR!")
            self.premium_analysis_btn.clicked.connect(self.show_patreon_invitation)
            self.premium_analysis_btn.setStyleSheet("background-color: #ff6b35; color: white; font-weight: bold; padding: 12px; font-size: 13px; border: 2px solid #ffd700;")
        
        premium_layout.addWidget(self.premium_analysis_btn)
        
        # Descripción de funciones premium
        premium_info = QLabel("🤖 Redes neuronales para análisis automático • 🔬 ML para interpretación geológica • 📊 Predicción inteligente de propiedades")
        premium_info.setStyleSheet("color: #666; font-style: italic; font-size: 10px; padding: 5px;")
        premium_info.setWordWrap(True)
        premium_layout.addWidget(premium_info)
        
        layout.addWidget(premium_group)
        
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
        
        # Botón Premium - siempre visible
        premium_layout = QHBoxLayout()
        self.premium_lithology_btn = QPushButton("🌟 Análisis IA Premium")
        if self.has_patreon_dlc:
            self.premium_lithology_btn.setText("🌟 Análisis IA Premium - ¡ACTIVO!")
            self.premium_lithology_btn.clicked.connect(self.open_advanced_analysis)
            self.premium_lithology_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 13px;")
        else:
            self.premium_lithology_btn.setText("🌟 Análisis IA Premium ✨ ¡DESBLOQUEAR!")
            self.premium_lithology_btn.clicked.connect(self.show_patreon_invitation)
            self.premium_lithology_btn.setStyleSheet("background-color: #ff6b35; color: white; font-weight: bold; padding: 12px; font-size: 12px; border: 2px solid #ffd700;")
        premium_layout.addWidget(self.premium_lithology_btn)
        layout.addLayout(premium_layout)
        
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

    def create_premium_dlc_tab(self) -> QWidget:
        """Tab para funcionalidades Premium/DLC de Patreon."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.has_patreon_dlc:
            # DLC PRESENTE: Mostrar UI premium completa
            title = QLabel("🌟 Premium IA - ¡ACTIVO!")
            title.setFont(QFont("Arial", 16, QFont.Bold))
            title.setStyleSheet("color: #28a745; margin: 10px; text-align: center;")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Información de suscripción activa
            subscription_info = QLabel("✅ Suscripción Patreon Activa - Nivel 3 ($15/mes)")
            subscription_info.setStyleSheet("color: #28a745; font-weight: bold; background-color: #d4edda; padding: 8px; border-radius: 5px; margin: 5px;")
            subscription_info.setAlignment(Qt.AlignCenter)
            layout.addWidget(subscription_info)
            
            # Separador
            layout.addWidget(QLabel(""))
            
            # Sección 1: Completado Inteligente
            completion_group = QGroupBox("🤖 Completado Inteligente con IA")
            completion_layout = QVBoxLayout(completion_group)
            
            completion_desc = QLabel("Usa redes neuronales para completar curvas incompletas dentro del mismo pozo usando correlaciones entre curvas completas e incompletas.")
            completion_desc.setWordWrap(True)
            completion_desc.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
            completion_layout.addWidget(completion_desc)
            
            self.neural_completion_btn = QPushButton("🧠 Abrir Completado Neural Intra-Pozo")
            self.neural_completion_btn.clicked.connect(self.open_neural_completion)
            self.neural_completion_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
            completion_layout.addWidget(self.neural_completion_btn)
            
            layout.addWidget(completion_group)
            
            # Sección 2: Análisis Avanzado
            analysis_group = QGroupBox("🔬 Análisis Litológico Avanzado")
            analysis_layout = QVBoxLayout(analysis_group)
            
            analysis_desc = QLabel("Clasificación automática de litologías usando machine learning y análisis de patrones multivariable.")
            analysis_desc.setWordWrap(True)
            analysis_desc.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
            analysis_layout.addWidget(analysis_desc)
            
            self.advanced_lithology_btn = QPushButton("🪨 Análisis Litológico IA")
            self.advanced_lithology_btn.clicked.connect(self.open_advanced_lithology)
            self.advanced_lithology_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
            analysis_layout.addWidget(self.advanced_lithology_btn)
            
            layout.addWidget(analysis_group)
            
            # Sección 3: Interpretación Automática
            interpreter_group = QGroupBox("🧠 Interpretador Automático")
            interpreter_layout = QVBoxLayout(interpreter_group)
            
            interpreter_desc = QLabel("Interpretación automática de registros geofísicos con comentarios técnicos y recomendaciones.")
            interpreter_desc.setWordWrap(True)
            interpreter_desc.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
            interpreter_layout.addWidget(interpreter_desc)
            
            self.ai_interpreter_btn = QPushButton("🗣️ Interpretador IA")
            self.ai_interpreter_btn.clicked.connect(self.open_ai_interpreter)
            self.ai_interpreter_btn.setStyleSheet("background-color: #6f42c1; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
            interpreter_layout.addWidget(self.ai_interpreter_btn)
            
            layout.addWidget(interpreter_group)
            
            # Estado del DLC
            dlc_status = QLabel("📦 DLC Versión: v1.0.0 | Estado: Completamente Funcional")
            dlc_status.setStyleSheet("color: #28a745; font-size: 10px; font-style: italic; text-align: center;")
            dlc_status.setAlignment(Qt.AlignCenter)
            layout.addWidget(dlc_status)
            
        else:
            # DLC NO PRESENTE: Mostrar invitación/marketing
            title = QLabel("🌟 Premium IA - ¡Desbloquear Funciones Avanzadas!")
            title.setFont(QFont("Arial", 16, QFont.Bold))
            title.setStyleSheet("color: #ff6b35; margin: 10px; text-align: center;")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Mensaje principal
            main_message = QLabel("🚀 Lleva PyPozo al siguiente nivel con IA y Machine Learning")
            main_message.setFont(QFont("Arial", 14, QFont.Bold))
            main_message.setStyleSheet("color: #333; margin: 10px; text-align: center;")
            main_message.setAlignment(Qt.AlignCenter)
            layout.addWidget(main_message)
            
            # Características premium
            features_group = QGroupBox("✨ Funciones Exclusivas Premium")
            features_layout = QVBoxLayout(features_group)
            
            features = [
                "🤖 Completado Inteligente de Registros con IA",
                "🔬 Análisis Litológico Automático con ML", 
                "🧠 Interpretador Automático de Registros",
                "📊 Predicción de Propiedades Petrofísicas",
                "🎯 Clasificación Automática de Facies",
                "🔍 Detección de Anomalías Geológicas",
                "📈 Optimización Automática de Parámetros",
                "🌐 Acceso a Modelos Pre-entrenados"
            ]
            
            for feature in features:
                feature_label = QLabel(feature)
                feature_label.setStyleSheet("color: #333; padding: 3px; font-size: 13px;")
                features_layout.addWidget(feature_label)
            
            layout.addWidget(features_group)
            
            # Precio y botón principal
            price_label = QLabel("💰 Solo $15/mes - Nivel 3 Patreon")
            price_label.setFont(QFont("Arial", 14, QFont.Bold))
            price_label.setStyleSheet("color: #28a745; text-align: center; margin: 10px;")
            price_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(price_label)
            
            # Botón principal CTA
            self.subscribe_btn = QPushButton("🌟 ¡SUSCRIBIRME AHORA!")
            self.subscribe_btn.clicked.connect(self.show_patreon_invitation)
            self.subscribe_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b35;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 15px;
                    border-radius: 8px;
                    border: 3px solid #ffd700;
                }
                QPushButton:hover {
                    background-color: #e55a2b;
                    border: 3px solid #ffed4e;
                }
            """)
            layout.addWidget(self.subscribe_btn)
            
            # Ya soy suscriptor
            existing_subscriber_label = QLabel("¿Ya eres suscriptor?")
            existing_subscriber_label.setStyleSheet("color: #666; text-align: center; margin-top: 15px;")
            existing_subscriber_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(existing_subscriber_label)
            
            self.download_dlc_btn = QPushButton("📥 Descargar DLC")
            self.download_dlc_btn.clicked.connect(self.show_download_instructions)
            self.download_dlc_btn.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold; padding: 8px; border-radius: 5px;")
            layout.addWidget(self.download_dlc_btn)
            
            # Garantía
            guarantee_label = QLabel("💯 30 días de garantía - Cancela cuando quieras")
            guarantee_label.setStyleSheet("color: #28a745; font-size: 11px; text-align: center; font-style: italic; margin-top: 10px;")
            guarantee_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(guarantee_label)
        
        # Spacer para empujar todo hacia arriba
        layout.addStretch()
        
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
        view_menu.addSeparator()
        view_menu.addAction('◀ Ocultar/Mostrar Panel Izquierdo', self.toggle_left_panel, 'Ctrl+1')
        view_menu.addAction('▶ Ocultar/Mostrar Panel Derecho', self.toggle_right_panel, 'Ctrl+2')
        view_menu.addAction('⛶ Maximizar Gráficas', self.toggle_both_panels, 'Ctrl+M')
        
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
        
        # Indicador de estado Premium
        if self.has_patreon_dlc:
            self.premium_status_label = QLabel("🌟 PREMIUM ACTIVO")
            self.premium_status_label.setStyleSheet("color: #28a745; font-weight: bold; background-color: #d4edda; padding: 3px 8px; border-radius: 4px; margin: 0 5px;")
        else:
            self.premium_status_label = QLabel("💎 Premium Disponible")
            self.premium_status_label.setStyleSheet("color: #ff6b35; font-weight: bold; background-color: #fff3cd; padding: 3px 8px; border-radius: 4px; margin: 0 5px; border: 1px solid #ffd700;")
            self.premium_status_label.mousePressEvent = lambda event: self.show_patreon_invitation()
        
        self.status_bar.addPermanentWidget(self.premium_status_label)
        
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
    
    # ========== FUNCIONES DE COLAPSAR PANELES ==========
    
    def toggle_left_panel(self):
        """Alternar visibilidad del panel izquierdo."""
        # Guardar tamaño actual de la ventana para evitar redimensionamiento
        current_geometry = self.geometry()
        
        if self.left_panel_visible:
            # Ocultar panel izquierdo
            self.left_panel.hide()
            self.toggle_left_btn.setText("▶")
            self.toggle_left_btn.setToolTip("Mostrar panel izquierdo")
            self.left_panel_visible = False
            # Ajustar tamaños
            current_sizes = self.main_splitter.sizes()
            new_sizes = [0, current_sizes[1] + current_sizes[0], current_sizes[2]]
            self.main_splitter.setSizes(new_sizes)
        else:
            # Mostrar panel izquierdo
            self.left_panel.show()
            self.toggle_left_btn.setText("◀")
            self.toggle_left_btn.setToolTip("Ocultar panel izquierdo")
            self.left_panel_visible = True
            # Restaurar tamaños
            if self.right_panel_visible:
                self.main_splitter.setSizes(self.normal_sizes)
            else:
                self.main_splitter.setSizes([250, 1350, 0])
        
        # Restaurar el tamaño de la ventana para evitar cambios indeseados
        self.setGeometry(current_geometry)
    
    def toggle_right_panel(self):
        """Alternar visibilidad del panel derecho."""
        # Guardar tamaño actual de la ventana para evitar redimensionamiento
        current_geometry = self.geometry()
        
        if self.right_panel_visible:
            # Ocultar panel derecho
            self.right_panel.hide()
            self.toggle_right_btn.setText("◀")
            self.toggle_right_btn.setToolTip("Mostrar panel derecho")
            self.right_panel_visible = False
            # Ajustar tamaños
            current_sizes = self.main_splitter.sizes()
            new_sizes = [current_sizes[0], current_sizes[1] + current_sizes[2], 0]
            self.main_splitter.setSizes(new_sizes)
        else:
            # Mostrar panel derecho
            self.right_panel.show()
            self.toggle_right_btn.setText("▶")
            self.toggle_right_btn.setToolTip("Ocultar panel derecho")
            self.right_panel_visible = True
            # Restaurar tamaños
            if self.left_panel_visible:
                self.main_splitter.setSizes(self.normal_sizes)
            else:
                self.main_splitter.setSizes([0, 1350, 250])
        
        # Restaurar el tamaño de la ventana para evitar cambios indeseados
        self.setGeometry(current_geometry)
    
    def toggle_both_panels(self):
        """Alternar ambos paneles a la vez (modo full screen gráficas)."""
        # Guardar tamaño actual de la ventana para evitar redimensionamiento
        current_geometry = self.geometry()
        
        if self.left_panel_visible or self.right_panel_visible:
            # Ocultar ambos paneles
            if self.left_panel_visible:
                self.toggle_left_panel()
            if self.right_panel_visible:
                self.toggle_right_panel()
        else:
            # Mostrar ambos paneles
            if not self.left_panel_visible:
                self.toggle_left_panel()
            if not self.right_panel_visible:
                self.toggle_right_panel()
        
        # Restaurar el tamaño de la ventana para evitar cambios indeseados
        self.setGeometry(current_geometry)

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
        basic_curves = ["GR", "SP", "CAL", "CALI", "RT", "RHOB", "NPHI"]
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
        # Buscar curvas de resistividad por nombre y unidades
        for curve in self.current_well.curves:
            curve_upper = curve.upper()
            units = self.current_well.get_curve_units(curve)
            units_lower = units.lower() if units else ""
            
            # Criterios de identificación de curvas eléctricas
            is_electrical = (
                # Por nombre
                any(keyword in curve_upper for keyword in ['RT', 'RES', 'ILD', 'LLD', 'MSFL', 'LLS', 'SP', 'AT90', 'AT60', 'AT30', 'AT20', 'AT10']) or
                # Por unidades
                any(unit in units_lower for unit in ['ohm', 'ohmm', 'mv'])
            )
            
            if is_electrical:
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
                # Verificar si alguna curva es de resistividad para aplicar escala log
                for curve_name in selected_curves:
                    if curve_name in self.current_well.curves:
                        units = self.current_well.get_curve_units(curve_name)
                        if units and ('ohm' in units.lower() or 'ohmm' in units.lower()):
                            ax.set_xscale('log')
                            self.log_activity(f"📊 Aplicando escala logarítmica (resistividad detectada)")
                            break
            
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
            
            # Configurar escala logarítmica para curvas de resistividad
            if units and ('ohm' in units.lower() or 'ohmm' in units.lower()):
                ax.set_xscale('log')
                self.log_activity(f"📊 Aplicando escala logarítmica a {curve_name} (resistividad)")
            
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
            basic_curves = ["GR", "SP", "CAL", "CALI", "RT", "RHOB", "NPHI"]
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
<li>✅ SW (Saturación de Agua) - 6 métodos disponibles</li>
<li>✅ Análisis Litológico</li>
<li>✅ Permeabilidad - 5 métodos disponibles</li>
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
                porosity_key = 'porosity'  # Corregido: usar 'porosity' en lugar de 'phid'
                
            elif method == "neutron":
                result = self.porosity_calculator.calculate_neutron_porosity(
                    neutron_porosity=self.current_well.data[nphi_curve]
                )
                phie_name = "PHIE_NPHI"
                porosity_key = 'porosity'  # Corregido: usar 'porosity' en lugar de 'phin'
                
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
            
            # Debug: mostrar claves disponibles en el resultado
            available_keys = list(result.keys()) if isinstance(result, dict) else ['result_not_dict']
            self.log_activity(f"Debug - Claves disponibles en resultado: {available_keys}")
            
            # Determinar la clave de porosidad a usar (prioritizar correcciones)
            if 'porosity_corrected' in result:
                porosity_key = 'porosity_corrected'
            elif 'phie_corrected' in result:
                porosity_key = 'phie_corrected'
            elif 'porosity_gas_corrected' in result:
                porosity_key = 'porosity_gas_corrected'
            elif 'phie_gas_corrected' in result:
                porosity_key = 'phie_gas_corrected'
            elif 'phie' in result:
                porosity_key = 'phie'
            elif 'porosity' in result:
                porosity_key = 'porosity'
            else:
                # Fallback: usar la primera clave numérica disponible
                numeric_keys = [k for k, v in result.items() if isinstance(v, (np.ndarray, list, pd.Series)) and k != 'warnings']
                if numeric_keys:
                    porosity_key = numeric_keys[0]
                else:
                    raise ValueError("No se encontró ninguna clave de datos de porosidad válida en el resultado")
            
            # Agregar resultado al pozo
            try:
                porosity_values = result[porosity_key]
                self.log_activity(f"Debug - Usando clave '{porosity_key}' para porosidad")
            except KeyError as ke:
                self.log_activity(f"❌ Error: Clave '{porosity_key}' no encontrada. Claves disponibles: {list(result.keys())}")
                QMessageBox.critical(self, "Error", f"Clave de porosidad '{porosity_key}' no encontrada en resultado.\nClaves disponibles: {list(result.keys())}")
                return
            
            success = self.current_well.add_curve(
                curve_name=phie_name,
                data=porosity_values,
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
            
            valid_por = porosity_values[~np.isnan(porosity_values)] if isinstance(porosity_values, np.ndarray) else porosity_values.dropna()
            
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
        """Realizar análisis litológico completo."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Obtener tipo de análisis seleccionado
            analysis_type = self.lithology_analysis_combo.currentText()
            
            # Obtener curvas seleccionadas
            gr_curve = self.lith_gr_combo.currentText()
            rhob_curve = self.lith_rhob_combo.currentText()
            nphi_curve = self.lith_nphi_combo.currentText()
            pef_curve = self.lith_pef_combo.currentText()
            rt_curve = self.lith_rt_combo.currentText()
            
            # Validar curvas mínimas según el tipo de análisis
            if analysis_type == "crossplots":
                if not rhob_curve or rhob_curve not in self.current_well.data.columns:
                    QMessageBox.warning(self, "Advertencia", "Curva RHOB requerida para crossplots")
                    return
                if not nphi_curve or nphi_curve not in self.current_well.data.columns:
                    QMessageBox.warning(self, "Advertencia", "Curva NPHI requerida para crossplots")
                    return
                
                # Ejecutar análisis de crossplots
                self.generate_lithology_crossplots()
                return
                
            elif analysis_type == "facies_classification":
                required = [('GR', gr_curve), ('RHOB', rhob_curve), ('NPHI', nphi_curve)]
                missing = []
                for name, curve in required:
                    if not curve or curve not in self.current_well.data.columns:
                        missing.append(name)
                
                if missing:
                    QMessageBox.warning(self, "Advertencia", 
                                      f"Curvas requeridas para facies: {', '.join(missing)}")
                    return
                
                # Ejecutar clasificación de facies
                self.classify_facies()
                return
                
            elif analysis_type == "mineral_identification":
                # Análisis de identificación mineral usando PEF
                if not pef_curve or pef_curve not in self.current_well.data.columns:
                    QMessageBox.warning(self, "Advertencia", "Curva PEF requerida para identificación mineral")
                    return
                if not rhob_curve or rhob_curve not in self.current_well.data.columns:
                    QMessageBox.warning(self, "Advertencia", "Curva RHOB requerida para identificación mineral")
                    return
                
                self._perform_mineral_identification()
                return
                
            elif analysis_type == "reservoir_quality":
                # Evaluación de calidad de reservorio
                self._perform_reservoir_quality_assessment()
                return
                
            elif analysis_type == "depositional_environment":
                # Análisis de ambiente deposicional
                if not gr_curve or gr_curve not in self.current_well.data.columns:
                    QMessageBox.warning(self, "Advertencia", "Curva GR requerida para análisis deposicional")
                    return
                
                self._perform_depositional_analysis()
                return
            
            else:
                QMessageBox.information(self, "Información", f"Análisis '{analysis_type}' en desarrollo")
                
        except Exception as e:
            self.log_activity(f"❌ Error en análisis litológico: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en análisis litológico:\n{str(e)}")
    
    def _perform_mineral_identification(self):
        """Realizar identificación mineral usando PEF y RHOB."""
        try:
            pef_curve = self.lith_pef_combo.currentText()
            rhob_curve = self.lith_rhob_combo.currentText()
            nphi_curve = self.lith_nphi_combo.currentText()
            
            pef_data = self.current_well.data[pef_curve]
            rhob_data = self.current_well.data[rhob_curve]
            nphi_data = self.current_well.data[nphi_curve] if nphi_curve and nphi_curve in self.current_well.data.columns else None
            
            self.log_activity(f"🔬 Identificando minerales usando PEF-RHOB...")
            
            # Usar el analizador de litología
            result = self.lithology_analyzer.photoelectric_analysis(
                pe=pef_data,
                rhob=rhob_data,
                nphi=nphi_data
            )
            
            if not result.get('success', False):
                QMessageBox.critical(self, "Error", f"Error en identificación mineral: {result.get('error', 'Error desconocido')}")
                return
            
            # Agregar resultado al pozo
            mineral_ids = result['mineral_identification']
            mineral_curve_name = "MINERAL_ID"
            
            success = self.current_well.add_curve(
                curve_name=mineral_curve_name,
                data=mineral_ids,
                units='category',
                description='Mineral identification from PEF-RHOB analysis'
            )
            
            if not success:
                QMessageBox.critical(self, "Error", f"No se pudo agregar curva {mineral_curve_name}")
                return
            
            # Mostrar resultados
            self.lithology_results_text.clear()
            self.lithology_results_text.append("✅ Identificación mineral completada")
            self.lithology_results_text.append(f"📊 Curva creada: {mineral_curve_name}")
            
            # Estadísticas por mineral
            mineral_stats = result['mineral_statistics']
            self.lithology_results_text.append(f"\n📊 Distribución Mineralógica:")
            
            for mineral, stats in mineral_stats.items():
                if stats['count'] > 0:
                    self.lithology_results_text.append(f"\n🪨 {mineral.upper()}:")
                    self.lithology_results_text.append(f"   • Puntos: {stats['count']} ({stats['percentage']:.1f}%)")
                    self.lithology_results_text.append(f"   • PEF promedio: {stats['avg_pe']:.2f}")
                    self.lithology_results_text.append(f"   • RHOB promedio: {stats['avg_rhob']:.3f} g/cm³")
            
            # Generar gráfico mineralógico
            self._plot_mineral_identification(pef_data, rhob_data, mineral_ids)
            
            self.log_activity(f"✅ Identificación mineral: {mineral_curve_name}")
            self.update_curves_list()
            
        except Exception as e:
            self.log_activity(f"❌ Error en identificación mineral: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en identificación mineral:\n{str(e)}")
    
    def _perform_reservoir_quality_assessment(self):
        """Evaluar calidad de reservorio."""
        try:
            # Buscar curvas necesarias (calculadas o originales)
            porosity_curves = [col for col in self.current_well.data.columns if any(p in col.upper() for p in ['PHIE', 'PHI', 'NPHI'])]
            permeability_curves = [col for col in self.current_well.data.columns if 'PERM' in col.upper()]
            vcl_curves = [col for col in self.current_well.data.columns if 'VCL' in col.upper()]
            sw_curves = [col for col in self.current_well.data.columns if 'SW' in col.upper()]
            
            if not porosity_curves:
                QMessageBox.warning(self, "Advertencia", "No se encontraron curvas de porosidad para evaluación")
                return
            
            # Seleccionar curvas más adecuadas
            porosity_curve = porosity_curves[0]  # Preferir PHIE si existe
            if any('PHIE' in curve for curve in porosity_curves):
                porosity_curve = [c for c in porosity_curves if 'PHIE' in c][0]
            
            permeability_curve = permeability_curves[0] if permeability_curves else None
            vcl_curve = vcl_curves[0] if vcl_curves else None
            sw_curve = sw_curves[0] if sw_curves else None
            
            self.log_activity(f"🏆 Evaluando calidad de reservorio...")
            
            # Obtener datos
            porosity_data = self.current_well.data[porosity_curve]
            permeability_data = self.current_well.data[permeability_curve] if permeability_curve else None
            vcl_data = self.current_well.data[vcl_curve] if vcl_curve else None
            sw_data = self.current_well.data[sw_curve] if sw_curve else None
            
            # Si no hay permeabilidad, estimar usando Timur
            if permeability_data is None:
                self.log_activity("⚠️ No hay permeabilidad, estimando con Timur...")
                # Estimar permeabilidad básica para el análisis
                phi_valid = porosity_data.dropna()
                if len(phi_valid) > 0:
                    swi_est = 0.25  # Estimación por defecto
                    perm_est = 0.136 * (phi_valid / swi_est) ** 4.4
                    # Crear serie completa
                    permeability_data = pd.Series(index=porosity_data.index, dtype=float)
                    permeability_data[phi_valid.index] = perm_est
                else:
                    QMessageBox.warning(self, "Advertencia", "No hay datos válidos de porosidad")
                    return
            
            # Usar el analizador de litología
            result = self.lithology_analyzer.reservoir_quality_assessment(
                porosity=porosity_data,
                permeability=permeability_data,
                vclay=vcl_data,
                sw=sw_data
            )
            
            if not result.get('success', False):
                QMessageBox.critical(self, "Error", f"Error en evaluación de calidad: {result.get('error', 'Error desconocido')}")
                return
            
            # Agregar curva de calidad al pozo
            quality_classes = result['reservoir_quality']
            quality_curve_name = "RES_QUALITY"
            
            success = self.current_well.add_curve(
                curve_name=quality_curve_name,
                data=quality_classes,
                units='category',
                description='Reservoir quality assessment'
            )
            
            if success:
                self.log_activity(f"📊 Curva de calidad creada: {quality_curve_name}")
            
            # Mostrar resultados detallados
            self.lithology_results_text.clear()
            self.lithology_results_text.append("✅ Evaluación de calidad de reservorio completada")
            self.lithology_results_text.append(f"📊 Curva creada: {quality_curve_name}")
            
            # Mostrar estadísticas por clase de calidad
            quality_stats = result['quality_statistics']
            self.lithology_results_text.append(f"\n📊 Distribución de Calidad:")
            
            quality_order = ['Excellent', 'Good', 'Fair', 'Poor', 'Non-reservoir']
            for quality in quality_order:
                if quality in quality_stats:
                    stats = quality_stats[quality]
                    self.lithology_results_text.append(f"\n🏷️ {quality}:")
                    self.lithology_results_text.append(f"   • Porcentaje: {stats['percentage']:.1f}%")
                    self.lithology_results_text.append(f"   • Puntos: {stats['count']}")
                    if 'avg_porosity' in stats:
                        self.lithology_results_text.append(f"   • φ promedio: {stats['avg_porosity']:.3f}")
                    if 'avg_permeability' in stats:
                        self.lithology_results_text.append(f"   • K promedio: {stats['avg_permeability']:.1f} mD")
            
            # Interpretación automática
            excellent_good = quality_stats.get('Excellent', {}).get('percentage', 0) + quality_stats.get('Good', {}).get('percentage', 0)
            
            self.lithology_results_text.append(f"\n🔍 Interpretación:")
            if excellent_good > 50:
                interpretation = "🟢 Reservorio de alta calidad con buen potencial comercial"
            elif excellent_good > 25:
                interpretation = "🟡 Reservorio de calidad moderada, evaluar viabilidad económica"
            else:
                interpretation = "🔴 Reservorio de baja calidad, requiere tecnologías especiales"
            
            self.lithology_results_text.append(f"   {interpretation}")
            
            self.log_activity(f"✅ Evaluación de calidad completada")
            self.update_curves_list()
            
        except Exception as e:
            self.log_activity(f"❌ Error en evaluación de calidad: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en evaluación de calidad:\n{str(e)}")
    
    def _perform_depositional_analysis(self):
        """Realizar análisis de ambiente deposicional."""
        try:
            gr_curve = self.lith_gr_combo.currentText()
            gr_data = self.current_well.data[gr_curve]
            
            self.log_activity(f"🌊 Analizando ambiente deposicional...")
            
            # Análisis básico de patrones de GR
            # Calcular tendencias y variabilidad
            window_size = max(10, len(gr_data) // 50)  # Ventana adaptiva
            
            # Tendencia general (regresión lineal simple)
            depth_values = np.arange(len(gr_data))
            valid_mask = ~np.isnan(gr_data)
            
            if np.sum(valid_mask) < 10:
                QMessageBox.warning(self, "Advertencia", "Datos insuficientes para análisis deposicional")
                return
            
            # Calcular estadísticas móviles
            gr_trend = np.full_like(gr_data, np.nan)
            gr_variability = np.full_like(gr_data, np.nan)
            
            for i in range(len(gr_data)):
                start_idx = max(0, i - window_size // 2)
                end_idx = min(len(gr_data), i + window_size // 2)
                
                window_data = gr_data[start_idx:end_idx]
                valid_window = window_data[~np.isnan(window_data)]
                
                if len(valid_window) > 3:
                    gr_trend[i] = np.mean(valid_window)
                    gr_variability[i] = np.std(valid_window)
            
            # Clasificación de ambientes basada en características de GR
            environment_class = np.full_like(gr_data, 'Unknown', dtype='<U20')
            
            for i, (gr_val, trend_val, var_val) in enumerate(zip(gr_data, gr_trend, gr_variability)):
                if np.isnan(gr_val) or np.isnan(trend_val) or np.isnan(var_val):
                    continue
                
                # Lógica simplificada de clasificación
                if gr_val < 50:  # Bajo GR
                    if var_val < 10:
                        environment_class[i] = 'Marino_Somero'
                    else:
                        environment_class[i] = 'Fluvial_Canal'
                elif gr_val < 100:  # GR moderado
                    if var_val < 15:
                        environment_class[i] = 'Deltaico'
                    else:
                        environment_class[i] = 'Fluvial_Llanura'
                else:  # Alto GR
                    if var_val < 20:
                        environment_class[i] = 'Marino_Profundo'
                    else:
                        environment_class[i] = 'Lacustre'
            
            # Agregar curvas al pozo
            trend_curve_name = "GR_TREND"
            var_curve_name = "GR_VARIABILITY"
            env_curve_name = "DEPO_ENVIRONMENT"
            
            # Agregar tendencia
            success1 = self.current_well.add_curve(
                curve_name=trend_curve_name,
                data=gr_trend,
                units='API',
                description='GR trend analysis for depositional environment'
            )
            
            # Agregar variabilidad
            success2 = self.current_well.add_curve(
                curve_name=var_curve_name,
                data=gr_variability,
                units='API',
                description='GR variability analysis'
            )
            
            # Agregar clasificación ambiental
            success3 = self.current_well.add_curve(
                curve_name=env_curve_name,
                data=environment_class,
                units='category',
                description='Depositional environment interpretation'
            )
            
            # Mostrar resultados
            self.lithology_results_text.clear()
            self.lithology_results_text.append("✅ Análisis de ambiente deposicional completado")
            
            if success1:
                self.lithology_results_text.append(f"📊 Tendencia GR: {trend_curve_name}")
            if success2:
                self.lithology_results_text.append(f"📊 Variabilidad GR: {var_curve_name}")
            if success3:
                self.lithology_results_text.append(f"📊 Ambiente: {env_curve_name}")
            
            # Estadísticas ambientales
            unique_envs, counts = np.unique(environment_class[environment_class != 'Unknown'], return_counts=True)
            total_valid = np.sum(counts)
            
            if total_valid > 0:
                self.lithology_results_text.append(f"\n📊 Distribución de Ambientes:")
                for env, count in zip(unique_envs, counts):
                    percentage = (count / total_valid) * 100
                    self.lithology_results_text.append(f"   • {env}: {count} puntos ({percentage:.1f}%)")
            
            # Generar gráfico de análisis deposicional
            self._plot_depositional_analysis(gr_data, gr_trend, gr_variability, environment_class)
            
            self.log_activity(f"✅ Análisis deposicional completado")
            self.update_curves_list()
            
        except Exception as e:
            self.log_activity(f"❌ Error en análisis deposicional: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en análisis deposicional:\n{str(e)}")
    
    def _plot_mineral_identification(self, pef_data, rhob_data, mineral_ids):
        """Generar gráfico de identificación mineral."""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Datos válidos
            valid_mask = (~np.isnan(pef_data)) & (~np.isnan(rhob_data))
            pef_valid = pef_data[valid_mask]
            rhob_valid = rhob_data[valid_mask]
            minerals_valid = mineral_ids[valid_mask]
            
            # Colores para minerales
            mineral_colors = {
                'quartz': 'red',
                'calcite': 'blue', 
                'dolomite': 'green',
                'clay': 'orange',
                'anhydrite': 'purple',
                'unknown': 'gray'
            }
            
            # Plotear por mineral
            for mineral in np.unique(minerals_valid):
                if mineral in mineral_colors:
                    mask = minerals_valid == mineral
                    ax.scatter(rhob_valid[mask], pef_valid[mask], 
                             c=mineral_colors[mineral], alpha=0.6, s=20, label=mineral.capitalize())
            
            # Líneas de referencia mineralógica
            ax.axhline(y=1.81, color='red', linestyle='--', alpha=0.5, label='Cuarzo (1.81)')
            ax.axhline(y=5.08, color='blue', linestyle='--', alpha=0.5, label='Calcita (5.08)')
            ax.axhline(y=3.14, color='green', linestyle='--', alpha=0.5, label='Dolomita (3.14)')
            ax.axhline(y=2.8, color='orange', linestyle='--', alpha=0.5, label='Arcilla (2.8)')
            
            ax.set_xlabel('RHOB (g/cm³)')
            ax.set_ylabel('PEF (barns/electron)')
            ax.set_title('Identificación Mineral - PEF vs RHOB')
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.log_activity(f"⚠️ Error en gráfico mineral: {str(e)}")
    
    def _plot_depositional_analysis(self, gr_data, gr_trend, gr_variability, environment_class):
        """Generar gráfico de análisis deposicional."""
        try:
            self.figure.clear()
            
            # Crear subplots
            gs = self.figure.add_gridspec(1, 3, hspace=0.3, wspace=0.4)
            ax1 = self.figure.add_subplot(gs[0, 0])  # GR original
            ax2 = self.figure.add_subplot(gs[0, 1])  # Tendencia
            ax3 = self.figure.add_subplot(gs[0, 2])  # Variabilidad
            
            depth = np.arange(len(gr_data))
            
            # GR original
            ax1.plot(gr_data, depth, 'b-', linewidth=0.5)
            ax1.set_ylabel('Depth Index')
            ax1.set_xlabel('GR (API)')
            ax1.set_title('GR Original')
            ax1.grid(True, alpha=0.3)
            ax1.invert_yaxis()
            
            # Tendencia
            valid_trend = ~np.isnan(gr_trend)
            ax2.plot(gr_trend[valid_trend], depth[valid_trend], 'r-', linewidth=1)
            ax2.set_xlabel('GR Trend (API)')
            ax2.set_title('Tendencia')
            ax2.grid(True, alpha=0.3)
            ax2.invert_yaxis()
            
            # Variabilidad
            valid_var = ~np.isnan(gr_variability)
            ax3.plot(gr_variability[valid_var], depth[valid_var], 'g-', linewidth=1)
            ax3.set_xlabel('GR Variability')
            ax3.set_title('Variabilidad')
            ax3.grid(True, alpha=0.3)
            ax3.invert_yaxis()
            
            well_name = self.current_well.name or "Pozo Actual"
            self.figure.suptitle(f'Análisis Deposicional - {well_name}', fontsize=12, fontweight='bold')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.log_activity(f"⚠️ Error en gráfico deposicional: {str(e)}")
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
                
                rt_curves = [c for c in curves if any(keyword in c.upper() for keyword in ['RT', 'RES', 'ILD', 'LLD', 'MSFL', 'LLS', 'AT90', 'AT60', 'AT30', 'AT20', 'AT10'])]
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
        """Calcular saturación de agua usando ecuación de Archie."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Obtener parámetros de la UI
            method = self.sw_method_combo.currentText()
            rt_curve = self.sw_rt_combo.currentText()
            porosity_curve = self.sw_porosity_combo.currentText()
            vcl_curve = self.sw_vcl_combo.currentText() if self.sw_vcl_combo.currentText() else None
            
            # Parámetros de Archie
            a = self.sw_a_spinbox.value()
            m = self.sw_m_spinbox.value()
            n = self.sw_n_spinbox.value()
            rw = self.sw_rw_spinbox.value()
            rsh = self.sw_rsh_spinbox.value()
            
            # Validar curvas requeridas
            if not rt_curve or rt_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva de resistividad '{rt_curve}' no encontrada")
                return
            
            if not porosity_curve or porosity_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva de porosidad '{porosity_curve}' no encontrada")
                return
            
            # Obtener datos
            rt_data = self.current_well.data[rt_curve].values
            porosity_data = self.current_well.data[porosity_curve].values
            vcl_data = None
            
            if vcl_curve and vcl_curve in self.current_well.data.columns:
                vcl_data = self.current_well.data[vcl_curve].values
            
            self.log_activity(f"💧 Calculando Sw usando método: {method}")
            
            # Calcular según el método seleccionado
            if method == "archie_simple":
                # Archie Simple: Sw = ((a * Rw) / (φ^m * Rt))^(1/n)
                sw_data = np.power((a * rw) / (np.power(porosity_data, m) * rt_data), 1/n)
                sw_name = "SW_ARCHIE"
                description = f"Water saturation calculated using Archie equation (a={a}, m={m}, n={n}, Rw={rw})"
                
            elif method == "archie_modified":
                # Archie Modificado con VCL: φe = φ * (1 - VCL)
                if vcl_data is not None:
                    effective_porosity = porosity_data * (1 - vcl_data)
                    sw_data = np.power((a * rw) / (np.power(effective_porosity, m) * rt_data), 1/n)
                    description = f"Water saturation calculated using modified Archie equation with VCL correction"
                else:
                    # Fallback a Archie simple si no hay VCL
                    self.log_activity("⚠️ VCL no disponible para Archie modificado, usando Archie simple")
                    sw_data = np.power((a * rw) / (np.power(porosity_data, m) * rt_data), 1/n)
                    description = f"Water saturation calculated using Archie equation (VCL not available)"
                sw_name = "SW_ARCHIE_MOD"
                
            elif method == "simandoux":
                # Simandoux: Para formaciones arcillosas
                if vcl_data is not None:
                    # Sw = (a * Rw / (2 * φ^m)) * [√(((VCL/Rsh) + (2*φ^m/a*Rw))^2 + 4*φ^m/(a*Rw*Rt)) - (VCL/Rsh + 2*φ^m/(a*Rw))]
                    term1 = a * rw / (2 * np.power(porosity_data, m))
                    term2 = vcl_data / rsh + 2 * np.power(porosity_data, m) / (a * rw)
                    term3 = 4 * np.power(porosity_data, m) / (a * rw * rt_data)
                    
                    sw_data = term1 * (np.sqrt(np.power(term2, 2) + term3) - term2)
                    description = f"Water saturation calculated using Simandoux equation for shaly formations"
                else:
                    # Fallback a Archie simple si no hay VCL
                    self.log_activity("⚠️ VCL no disponible para Simandoux, usando Archie simple")
                    sw_data = np.power((a * rw) / (np.power(porosity_data, m) * rt_data), 1/n)
                    description = f"Water saturation calculated using Archie equation (VCL not available for Simandoux)"
                sw_name = "SW_SIMANDOUX"
                
            elif method == "waxman_smits":
                # Waxman-Smits: Para formaciones con arcillas conductivas
                if vcl_data is not None:
                    # Sw^n = (a * Rw * (1 + B * Qv)) / (φ^m * Rt)
                    # Donde B = 0.045 y Qv ≈ VCL (aproximación)
                    B = 0.045
                    Qv = vcl_data  # Aproximación simple
                    sw_data = np.power((a * rw * (1 + B * Qv)) / (np.power(porosity_data, m) * rt_data), 1/n)
                    description = f"Water saturation calculated using Waxman-Smits equation for conductive clays"
                else:
                    # Fallback a Archie simple si no hay VCL
                    self.log_activity("⚠️ VCL no disponible para Waxman-Smits, usando Archie simple")
                    sw_data = np.power((a * rw) / (np.power(porosity_data, m) * rt_data), 1/n)
                    description = f"Water saturation calculated using Archie equation (VCL not available for Waxman-Smits)"
                sw_name = "SW_WAXMAN_SMITS"
                
            elif method == "dual_water":
                # Dual Water: Modelo de dos aguas (simplificado)
                # Asume que Swb = 0.1 * VCL (agua ligada) y calcula agua libre
                if vcl_data is not None:
                    swb = 0.1 * vcl_data  # Agua ligada
                    # Sw_free usando Archie en porosidad efectiva
                    effective_porosity = porosity_data - swb
                    effective_porosity = np.maximum(effective_porosity, 0.01)  # Evitar valores negativos
                    sw_free = np.power((a * rw) / (np.power(effective_porosity, m) * rt_data), 1/n)
                    sw_data = sw_free + swb  # Saturación total
                    description = f"Water saturation calculated using Dual Water model with VCL"
                else:
                    # Usar un valor estimado de agua ligada del 10%
                    self.log_activity("⚠️ VCL no disponible para Dual Water, estimando agua ligada = 10%")
                    swb = 0.1  # Agua ligada estimada
                    effective_porosity = porosity_data - swb
                    effective_porosity = np.maximum(effective_porosity, 0.01)
                    sw_free = np.power((a * rw) / (np.power(effective_porosity, m) * rt_data), 1/n)
                    sw_data = sw_free + swb
                    description = f"Water saturation calculated using Dual Water model (estimated bound water)"
                sw_name = "SW_DUAL_WATER"
                
            elif method == "indonesian":
                # Ecuación Indonesa: Para formaciones fracturadas
                if vcl_data is not None:
                    # 1/√Rt = Vcl/√Rsh + φ^m/n * Sw^n/√(a*Rw) (simplificada)
                    # Sw^n = √(a*Rw) * (1/√Rt - VCL/√Rsh) / φ^m/n
                    term1 = np.sqrt(a * rw)
                    term2 = 1/np.sqrt(rt_data) - vcl_data/np.sqrt(rsh)
                    term3 = np.power(porosity_data, m/n)
                    sw_data = np.power(np.maximum(term1 * term2 / term3, 0.001), 1/n)
                    description = f"Water saturation calculated using Indonesian equation for fractured formations"
                else:
                    # Fallback a Archie si no hay VCL
                    self.log_activity("⚠️ VCL no disponible para Ecuación Indonesa, usando Archie simple")
                    sw_data = np.power((a * rw) / (np.power(porosity_data, m) * rt_data), 1/n)
                    description = f"Water saturation calculated using Archie equation (VCL not available for Indonesian)"
                sw_name = "SW_INDONESIAN"
                
            else:
                # Método no reconocido, usar Archie simple
                self.log_activity(f"⚠️ Método {method} no reconocido, usando Archie simple")
                sw_data = np.power((a * rw) / (np.power(porosity_data, m) * rt_data), 1/n)
                sw_name = "SW_ARCHIE"
                description = f"Water saturation calculated using Archie equation (unknown method fallback)"
            
            # Aplicar límites físicos (0 ≤ Sw ≤ 1)
            sw_data = np.clip(sw_data, 0.0, 1.0)
            
            # Manejar valores no válidos
            sw_data = np.where(np.isfinite(sw_data), sw_data, np.nan)
            
            # Agregar resultado al pozo
            success = self.current_well.add_curve(
                curve_name=sw_name,
                data=sw_data,
                units='fraction',
                description=description
            )
            
            if not success:
                QMessageBox.critical(self, "Error", f"No se pudo agregar la curva {sw_name}")
                return
            
            # Mostrar resultados
            self.sw_results_text.clear()
            self.sw_results_text.append(f"✅ Saturación de agua calculada usando: {method}")
            self.sw_results_text.append(f"📊 Curva creada: {sw_name}")
            self.sw_results_text.append(f"📈 Estadísticas:")
            
            valid_sw = sw_data[np.isfinite(sw_data)]
            
            if len(valid_sw) > 0:
                self.sw_results_text.append(f"   • Promedio: {valid_sw.mean():.3f}")
                self.sw_results_text.append(f"   • Mediana: {np.median(valid_sw):.3f}")
                self.sw_results_text.append(f"   • Mín: {valid_sw.min():.3f}")
                self.sw_results_text.append(f"   • Máx: {valid_sw.max():.3f}")
                self.sw_results_text.append(f"   • P90: {np.percentile(valid_sw, 90):.3f}")
                self.sw_results_text.append(f"   • P10: {np.percentile(valid_sw, 10):.3f}")
            else:
                self.sw_results_text.append(f"   • No hay datos válidos")
                
            self.sw_results_text.append(f"🔧 Parámetros:")
            self.sw_results_text.append(f"   • a (tortuosidad): {a}")
            self.sw_results_text.append(f"   • m (cementación): {m}")
            self.sw_results_text.append(f"   • n (saturación): {n}")
            self.sw_results_text.append(f"   • Rw: {rw} ohm-m")
            if method in ["simandoux", "archie_modified"]:
                self.sw_results_text.append(f"   • Rsh: {rsh} ohm-m")
            
            # QC warnings
            if len(valid_sw) > 0:
                high_sw = np.sum(valid_sw > 0.8) / len(valid_sw) * 100
                low_sw = np.sum(valid_sw < 0.2) / len(valid_sw) * 100
                
                self.sw_results_text.append(f"\n📊 Control de Calidad:")
                self.sw_results_text.append(f"   • Sw > 80%: {high_sw:.1f}% de muestras")
                self.sw_results_text.append(f"   • Sw < 20%: {low_sw:.1f}% de muestras")
                
                if high_sw > 70:
                    self.sw_results_text.append(f"   ⚠️ Alta Sw dominante - revisar parámetros")
                if low_sw > 50:
                    self.sw_results_text.append(f"   ⚠️ Baja Sw dominante - posible hidrocarburo")
            
            self.log_activity(f"🧮 Sw calculada: {sw_name} (método: {method})")
            self.update_curves_list()
            self.update_petrophysics_ui()
            
        except Exception as e:
            self.log_activity(f"❌ Error calculando Sw: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error calculando saturación de agua:\n{str(e)}")
    
    def calculate_permeability(self):
        """Calcular permeabilidad usando varios métodos empíricos."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Obtener parámetros de la UI
            method = self.perm_method_combo.currentText()
            porosity_curve = self.perm_porosity_combo.currentText()
            sw_curve = self.perm_sw_combo.currentText()
            
            # Verificar si se usarán curvas calculadas
            use_calc_porosity = self.perm_use_calc_porosity.isChecked()
            use_calc_sw = self.perm_use_calc_sw.isChecked()
            
            # Buscar curvas de porosidad calculada si está habilitado
            if use_calc_porosity:
                calc_porosity_curves = [col for col in self.current_well.data.columns if 'PHIE' in col.upper()]
                if calc_porosity_curves:
                    porosity_curve = calc_porosity_curves[-1]  # Usar la más reciente
                    self.log_activity(f"🔧 Usando porosidad calculada: {porosity_curve}")
                else:
                    QMessageBox.warning(self, "Advertencia", "No se encontró curva PHIE calculada")
                    return
            
            # Buscar curvas de Sw calculada si está habilitado
            if use_calc_sw:
                calc_sw_curves = [col for col in self.current_well.data.columns if 'SW_' in col.upper()]
                if calc_sw_curves:
                    sw_curve = calc_sw_curves[-1]  # Usar la más reciente
                    self.log_activity(f"🔧 Usando Sw calculada: {sw_curve}")
                else:
                    QMessageBox.warning(self, "Advertencia", "No se encontró curva SW calculada")
                    return
            
            # Validar curvas
            if not porosity_curve or porosity_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva de porosidad '{porosity_curve}' no encontrada")
                return
            
            if not sw_curve or sw_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva de Sw '{sw_curve}' no encontrada")
                return
            
            # Obtener parámetros del modelo
            swi = self.perm_swi_spinbox.value()
            c_factor = self.perm_c_factor_spinbox.value()
            phi_exp = self.perm_phi_exp_spinbox.value()
            sw_exp = self.perm_sw_exp_spinbox.value()
            
            # Preparar datos
            porosity_data = self.current_well.data[porosity_curve]
            sw_data = self.current_well.data[sw_curve]
            
            # Calcular permeabilidad según el método
            if method == "timur":
                result = self.permeability_calculator.calculate_timur_permeability(
                    porosity=porosity_data,
                    sw_irreducible=swi,
                    c_factor=c_factor,
                    phi_exponent=phi_exp,
                    sw_exponent=abs(sw_exp)  # Timur usa exponente positivo
                )
                perm_name = "PERM_TIMUR"
                
            elif method == "kozeny_carman":
                result = self.permeability_calculator.calculate_kozeny_carman_permeability(
                    porosity=porosity_data,
                    specific_surface=c_factor,  # Factor C se usa como superficie específica
                    tortuosity=2.0  # Valor típico
                )
                perm_name = "PERM_KC"
                
            elif method == "wyllie_rose":
                result = self.permeability_calculator.calculate_wyllie_rose_permeability(
                    porosity=porosity_data,
                    irreducible_saturation=swi,
                    c_factor=c_factor
                )
                perm_name = "PERM_WR"
                
            elif method == "coates_denoo":
                result = self.permeability_calculator.calculate_coates_denoo_permeability(
                    porosity=porosity_data,
                    sw_irreducible=swi,
                    c_factor=c_factor
                )
                perm_name = "PERM_CD"
                
            elif method == "empirical":
                # Modelo empírico general: K = C * φ^a * Sw^b
                permeability = c_factor * (porosity_data ** phi_exp) * (sw_data ** sw_exp)
                permeability = np.maximum(permeability, 0.001)  # Mínimo 0.001 mD
                
                result = {
                    'permeability': permeability,
                    'statistics': {
                        'mean': np.nanmean(permeability),
                        'median': np.nanmedian(permeability),
                        'min': np.nanmin(permeability),
                        'max': np.nanmax(permeability)
                    }
                }
                perm_name = "PERM_EMP"
            
            # Determinar la clave de permeabilidad en el resultado
            if 'permeability' in result:
                perm_key = 'permeability'
            elif 'perm' in result:
                perm_key = 'perm'
            else:
                # Usar la primera clave numérica
                numeric_keys = [k for k, v in result.items() if isinstance(v, (np.ndarray, list, pd.Series))]
                if numeric_keys:
                    perm_key = numeric_keys[0]
                else:
                    raise ValueError("No se encontró clave de permeabilidad válida en el resultado")
            
            # Agregar resultado al pozo
            permeability_values = result[perm_key]
            success = self.current_well.add_curve(
                curve_name=perm_name,
                data=permeability_values,
                units='mD',
                description=f'Permeability calculated using {method} method'
            )
            
            if not success:
                QMessageBox.critical(self, "Error", f"No se pudo agregar la curva {perm_name}")
                return
            
            # Mostrar resultados
            self.perm_results_text.clear()
            self.perm_results_text.append(f"✅ Permeabilidad calculada usando método: {method}")
            self.perm_results_text.append(f"📊 Curva creada: {perm_name}")
            self.perm_results_text.append(f"📈 Estadísticas:")
            
            valid_perm = permeability_values[~np.isnan(permeability_values)] if isinstance(permeability_values, np.ndarray) else permeability_values.dropna()
            
            if len(valid_perm) > 0:
                self.perm_results_text.append(f"   • Promedio: {valid_perm.mean():.2f} mD")
                self.perm_results_text.append(f"   • Mediana: {np.median(valid_perm):.2f} mD")
                self.perm_results_text.append(f"   • Mín: {valid_perm.min():.2f} mD")
                self.perm_results_text.append(f"   • Máx: {valid_perm.max():.2f} mD")
            else:
                self.perm_results_text.append(f"   • No hay datos válidos para estadísticas")
                
            self.perm_results_text.append(f"\n🔧 Parámetros utilizados:")
            self.perm_results_text.append(f"   • Swi: {swi:.3f}")
            self.perm_results_text.append(f"   • Factor C: {c_factor:.3f}")
            if method == "empirical":
                self.perm_results_text.append(f"   • Exponente φ: {phi_exp:.1f}")
                self.perm_results_text.append(f"   • Exponente Sw: {sw_exp:.1f}")
            
            # Mostrar curvas utilizadas
            self.perm_results_text.append(f"\n📊 Curvas utilizadas:")
            self.perm_results_text.append(f"   • Porosidad: {porosity_curve}")
            self.perm_results_text.append(f"   • Sw: {sw_curve}")
            
            # Mostrar advertencias si las hay
            if 'warnings' in result and result['warnings']:
                self.perm_results_text.append(f"\n⚠️ Advertencias QC:")
                for warning in result['warnings']:
                    self.perm_results_text.append(f"   • {warning}")
            
            self.log_activity(f"🌊 Permeabilidad calculada: {perm_name} (método: {method})")
            self.update_curves_list()
            
        except Exception as e:
            self.log_activity(f"❌ Error calculando permeabilidad: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error calculando permeabilidad:\n{str(e)}")
    

    
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
        method = self.sw_method_combo.currentText() if hasattr(self, 'sw_method_combo') else "archie_simple"
        
        info_texts = {
            'archie_simple': """
🧮 ARCHIE SIMPLE
================

📌 Ecuación:
Sw = ((a * Rw) / (φ^m * Rt))^(1/n)

📊 Parámetros:
• a: Factor de tortuosidad (típico: 0.5-2.0)
• m: Exponente de cementación (típico: 1.5-2.5)
• n: Exponente de saturación (típico: 1.8-2.5)
• Rw: Resistividad del agua de formación (ohm-m)
• φ: Porosidad efectiva (fracción)
• Rt: Resistividad verdadera (ohm-m)

🎯 Aplicación:
• Formaciones limpias (VCL < 10%)
• Rocas consolidadas
• Porosidad intergranular

⚠️ Limitaciones:
• No válido para formaciones arcillosas
• Asume conductividad por agua de formación únicamente

📚 Referencias:
• Archie (1942): "The Electrical Resistivity Log as an Aid in Determining Some Reservoir Characteristics"
            """,
            
            'archie_modified': """
🧮 ARCHIE MODIFICADO CON VCL
===========================

📌 Ecuación:
φe = φ * (1 - VCL)
Sw = ((a * Rw) / (φe^m * Rt))^(1/n)

📊 Parámetros:
• Todos los de Archie simple
• VCL: Volumen de arcilla (fracción)
• φe: Porosidad efectiva corregida

🎯 Aplicación:
• Formaciones ligeramente arcillosas (VCL: 10-25%)
• Corrección simple por arcilla
• Transición entre limpio y arcilloso

⚠️ Limitaciones:
• Corrección simplificada
• No considera conductividad de arcillas
• VCL debe ser confiable

📚 Referencias:
• Modificación práctica de Archie (1942)
            """,
            
            'simandoux': """
🧮 SIMANDOUX
============

📌 Ecuación:
Sw = (a*Rw/(2*φ^m)) * [√(((VCL/Rsh) + (2*φ^m/a*Rw))^2 + 4*φ^m/(a*Rw*Rt)) - (VCL/Rsh + 2*φ^m/(a*Rw))]

📊 Parámetros:
• Todos los de Archie
• Rsh: Resistividad de la arcilla (ohm-m)
• VCL: Volumen de arcilla (fracción)

🎯 Aplicación:
• Formaciones moderadamente arcillosas (VCL: 15-40%)
• Modelo de resistores en paralelo
• Arcillas dispersas

⚠️ Limitaciones:
• Requiere conocer Rsh
• Asume arcillas dispersas uniformemente
• Puede subestimar Sw en alta VCL

📚 Referencias:
• Simandoux (1963): "Dielectric measurements on porous media"
            """,
            
            'waxman_smits': """
🧮 WAXMAN-SMITS
===============

📌 Ecuación:
Sw^n = (a * Rw * (1 + B * Qv)) / (φ^m * Rt)

📊 Parámetros:
• Todos los de Archie
• B: Factor de movilidad iónica (típico: 0.045)
• Qv: Capacidad de intercambio catiónico por unidad de volumen

🎯 Aplicación:
• Formaciones arcillosas con arcillas conductivas
• Arcillas montmorilloníticas
• Intercambio catiónico significativo

⚠️ Limitaciones:
• Requiere determinación de Qv
• Complejo en la práctica
• Parámetro B variable con temperatura

📚 Referencias:
• Waxman & Smits (1968): "Electrical Conductivities in Oil-Bearing Shaly Sands"
            """,
            
            'dual_water': """
🧮 DUAL WATER
=============

📌 Concepto:
Modelo de dos tipos de agua:
• Agua libre (en poros grandes)
• Agua ligada (en arcillas)

📊 Ecuación Simplificada:
Sw_total = Sw_free + Sw_bound
Sw_free = ((a * Rw) / (φeff^m * Rt))^(1/n)
Sw_bound ≈ 0.1 * VCL

🎯 Aplicación:
• Formaciones con arcillas hidratadas
• Distingue agua móvil vs inmóvil
• Análisis de productividad

⚠️ Limitaciones:
• Modelo simplificado implementado
• Requiere calibración local
• Complejo determinar parámetros

📚 Referencias:
• Clavier et al. (1984): "Theoretical and Experimental Bases for the Dual-Water Model"
            """,
            
            'indonesian': """
🧮 ECUACIÓN INDONESA
===================

📌 Ecuación:
1/√Rt = VCL/√Rsh + φ^(m/n) * Sw^n / √(a*Rw)

📊 Parámetros:
• Todos los de Archie y Simandoux
• Desarrollada para formaciones fracturadas

🎯 Aplicación:
• Formaciones fracturadas
• Porosidad secundaria
• Geología compleja (vulcanoclásticos)

⚠️ Limitaciones:
• Específica para cierto tipo de rocas
• Requiere calibración local
• Complejidad en la aplicación

📚 Referencias:
• Poupon & Leveaux (1971): "Evaluation of Water Saturations in Shaly Formations"
            """
        }
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Información Detallada - {method.upper()}")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setFont(QFont("Courier New", 10))
        text_widget.setPlainText(info_texts.get(method, "Información no disponible para este método"))
        layout.addWidget(text_widget)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def preview_sw_calculation(self):
        """Vista previa del cálculo de Sw."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        
        try:
            # Obtener parámetros de la UI
            method = self.sw_method_combo.currentText()
            rt_curve = self.sw_rt_combo.currentText()
            porosity_curve = self.sw_porosity_combo.currentText()
            
            # Parámetros de Archie
            a = self.sw_a_spinbox.value()
            m = self.sw_m_spinbox.value()
            n = self.sw_n_spinbox.value()
            rw = self.sw_rw_spinbox.value()
            rsh = self.sw_rsh_spinbox.value()
            
            # Validaciones básicas
            if not rt_curve or rt_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva de resistividad '{rt_curve}' no encontrada")
                return
            
            if not porosity_curve or porosity_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva de porosidad '{porosity_curve}' no encontrada")
                return
            
            # Obtener muestra de datos (primeros 10 valores válidos)
            rt_data = self.current_well.data[rt_curve].dropna().head(10)
            porosity_data = self.current_well.data[porosity_curve].dropna().head(10)
            
            if len(rt_data) == 0 or len(porosity_data) == 0:
                QMessageBox.warning(self, "Advertencia", "No hay datos válidos para la vista previa")
                return
            
            # Calcular muestra con Archie simple
            rt_sample = rt_data.iloc[0] if len(rt_data) > 0 else 10.0
            phi_sample = porosity_data.iloc[0] if len(porosity_data) > 0 else 0.2
            
            sw_sample = ((a * rw) / (phi_sample**m * rt_sample))**(1/n)
            sw_sample = np.clip(sw_sample, 0.0, 1.0)
            
            # Crear mensaje de vista previa
            preview_msg = f"""
🔍 VISTA PREVIA - CÁLCULO SW

📊 Método seleccionado: {method.upper()}

📈 Datos de muestra:
• Resistividad (Rt): {rt_sample:.1f} ohm-m
• Porosidad (φ): {phi_sample:.3f}

🔧 Parámetros:
• a (tortuosidad): {a}
• m (cementación): {m}
• n (saturación): {n}
• Rw: {rw} ohm-m

💧 Resultado (Archie Simple):
• Sw calculada: {sw_sample:.3f} ({sw_sample*100:.1f}%)

📝 Ecuación aplicada:
Sw = ((a × Rw) / (φ^m × Rt))^(1/n)
Sw = (({a} × {rw}) / ({phi_sample:.3f}^{m} × {rt_sample:.1f}))^(1/{n})

⚠️ Esta es solo una muestra. El cálculo completo procesará todos los datos del pozo.
            """
            
            QMessageBox.information(self, "Vista Previa SW", preview_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en vista previa:\n{str(e)}")
    
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
        method = self.perm_method_combo.currentText()
        
        details = {
            'timur': {
                'title': 'Método de Timur',
                'formula': 'K = C × (φ/Swi)^n',
                'description': 'Correlación empírica desarrollada por Timur (1968) para areniscas.',
                'parameters': {
                    'C': 'Constante empírica (típico: 0.136)',
                    'φ': 'Porosidad (fracción)',
                    'Swi': 'Saturación de agua irreducible',
                    'n': 'Exponente (típico: 4.4)'
                },
                'range': 'Mejor para areniscas limpias con porosidad > 10%',
                'units': 'Permeabilidad en miliDarcys (mD)'
            },
            'kozeny_carman': {
                'title': 'Ecuación de Kozeny-Carman',
                'formula': 'K = (φ³/((1-φ)² × S²)) × (1/τ)',
                'description': 'Ecuación fundamental basada en principios físicos de flujo en medios porosos.',
                'parameters': {
                    'φ': 'Porosidad (fracción)',
                    'S': 'Superficie específica (área/volumen)',
                    'τ': 'Tortuosidad (típico: 2-3)'
                },
                'range': 'Aplicable a todos los tipos de roca, requiere superficie específica',
                'units': 'Permeabilidad en Darcys'
            },
            'wyllie_rose': {
                'title': 'Método de Wyllie & Rose',
                'formula': 'K = C × (φ⁶/Swi²)',
                'description': 'Correlación empírica para carbonatos desarrollada por Wyllie & Rose (1950).',
                'parameters': {
                    'C': 'Constante empírica (típico: 79-318)',
                    'φ': 'Porosidad (fracción)',
                    'Swi': 'Saturación de agua irreducible'
                },
                'range': 'Optimizado para carbonatos, especialmente calizas',
                'units': 'Permeabilidad en miliDarcys (mD)'
            },
            'coates_denoo': {
                'title': 'Método de Coates & Denoo',
                'formula': 'K = C × (φ⁴/Swi²)',
                'description': 'Correlación para areniscas basada en análisis de núcleos.',
                'parameters': {
                    'C': 'Constante empírica (típico: 10-100)',
                    'φ': 'Porosidad (fracción)',
                    'Swi': 'Saturación de agua irreducible'
                },
                'range': 'Areniscas con buena clasificación granulométrica',
                'units': 'Permeabilidad en miliDarcys (mD)'
            },
            'empirical': {
                'title': 'Modelo Empírico General',
                'formula': 'K = C × φᵃ × Swᵇ',
                'description': 'Modelo flexible que permite ajustar exponentes según datos locales.',
                'parameters': {
                    'C': 'Constante empírica (calibrar localmente)',
                    'φ': 'Porosidad (fracción)',
                    'Sw': 'Saturación de agua',
                    'a, b': 'Exponentes ajustables'
                },
                'range': 'Adaptable a cualquier litología con calibración',
                'units': 'Permeabilidad en miliDarcys (mD)'
            }
        }
        
        if method not in details:
            QMessageBox.warning(self, "Advertencia", f"Detalles no disponibles para método: {method}")
            return
        
        info = details[method]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalles - {info['title']}")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Título
        title_label = QLabel(f"🌊 {info['title']}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E8B57; margin: 10px;")
        layout.addWidget(title_label)
        
        # Contenido
        content = QTextEdit()
        content.setReadOnly(True)
        content.setFont(QFont("Segoe UI", 10))
        
        text = f"""
<h3>📐 Fórmula:</h3>
<p style="font-family: 'Courier New'; font-size: 12px; background: #f0f0f0; padding: 10px; border-radius: 5px;">
<b>{info['formula']}</b>
</p>

<h3>📝 Descripción:</h3>
<p>{info['description']}</p>

<h3>⚙️ Parámetros:</h3>
<ul>
"""
        for param, desc in info['parameters'].items():
            text += f"<li><b>{param}:</b> {desc}</li>"
        
        text += f"""
</ul>

<h3>🎯 Rango de Aplicación:</h3>
<p>{info['range']}</p>

<h3>📏 Unidades:</h3>
<p>{info['units']}</p>

<h3>💡 Recomendaciones:</h3>
<ul>
<li>Calibrar constantes con datos de núcleos locales cuando sea posible</li>
<li>Verificar consistencia con pruebas de pozo</li>
<li>Considerar heterogeneidad litológica en la interpretación</li>
<li>Usar múltiples métodos para validación cruzada</li>
</ul>
"""
        
        content.setHtml(text)
        layout.addWidget(content)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def classify_permeability(self):
        """Clasificar valores de permeabilidad según estándares de la industria."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Buscar curvas de permeabilidad calculadas
            perm_curves = [col for col in self.current_well.data.columns if 'PERM' in col.upper()]
            
            if not perm_curves:
                QMessageBox.warning(self, "Advertencia", "No se encontraron curvas de permeabilidad calculadas")
                return
            
            # Seleccionar curva más reciente
            perm_curve = perm_curves[-1]
            perm_data = self.current_well.data[perm_curve].dropna()
            
            if len(perm_data) == 0:
                QMessageBox.warning(self, "Advertencia", f"No hay datos válidos en {perm_curve}")
                return
            
            # Clasificación estándar de permeabilidad (en mD)
            classifications = {
                'Excelente': {'min': 1000, 'max': float('inf'), 'color': '#228B22'},
                'Muy Buena': {'min': 100, 'max': 1000, 'color': '#32CD32'},
                'Buena': {'min': 10, 'max': 100, 'color': '#90EE90'},
                'Regular': {'min': 1, 'max': 10, 'color': '#FFD700'},
                'Pobre': {'min': 0.1, 'max': 1, 'color': '#FFA500'},
                'Muy Pobre': {'min': 0.01, 'max': 0.1, 'color': '#FF6347'},
                'Impermeable': {'min': 0, 'max': 0.01, 'color': '#DC143C'}
            }
            
            # Calcular distribución por categorías
            results = {}
            total_points = len(perm_data)
            
            for category, limits in classifications.items():
                mask = (perm_data >= limits['min']) & (perm_data < limits['max'])
                count = mask.sum()
                percentage = (count / total_points) * 100
                results[category] = {
                    'count': count,
                    'percentage': percentage,
                    'color': limits['color']
                }
            
            # Crear curva de clasificación categórica
            classification_data = np.full(len(self.current_well.data), np.nan, dtype=object)
            perm_full = self.current_well.data[perm_curve]
            
            for i, perm_val in enumerate(perm_full):
                if pd.notna(perm_val):
                    for category, limits in classifications.items():
                        if limits['min'] <= perm_val < limits['max']:
                            classification_data[i] = category
                            break
            
            # Agregar curva de clasificación al pozo
            class_curve_name = f"{perm_curve}_CLASS"
            success = self.current_well.add_curve(
                curve_name=class_curve_name,
                data=classification_data,
                units='category',
                description=f'Permeability classification for {perm_curve}'
            )
            
            if success:
                self.log_activity(f"📊 Clasificación creada: {class_curve_name}")
            
            # Mostrar resultados en un diálogo detallado
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Clasificación de Permeabilidad - {perm_curve}")
            dialog.setMinimumSize(500, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Título
            title = QLabel("📊 Clasificación de Permeabilidad")
            title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(title)
            
            # Estadísticas generales
            stats_text = QTextEdit()
            stats_text.setMaximumHeight(150)
            stats_text.setReadOnly(True)
            
            stats_content = f"""
<b>Curva analizada:</b> {perm_curve}<br>
<b>Total de puntos:</b> {total_points}<br>
<b>Rango:</b> {perm_data.min():.3f} - {perm_data.max():.3f} mD<br>
<b>Promedio:</b> {perm_data.mean():.3f} mD<br>
<b>Mediana:</b> {perm_data.median():.3f} mD<br>
<b>Desviación estándar:</b> {perm_data.std():.3f} mD
"""
            stats_text.setHtml(stats_content)
            layout.addWidget(stats_text)
            
            # Tabla de distribución
            table_label = QLabel("📈 Distribución por Categorías:")
            table_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(table_label)
            
            results_text = QTextEdit()
            results_text.setReadOnly(True)
            
            table_content = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
            table_content += "<tr style='background-color: #f0f0f0;'><th>Clasificación</th><th>Rango (mD)</th><th>Puntos</th><th>Porcentaje</th></tr>"
            
            for category, limits in classifications.items():
                result = results[category]
                color = result['color']
                range_text = f"{limits['min']:.3f} - {limits['max']:.1f}" if limits['max'] != float('inf') else f"> {limits['min']:.3f}"
                
                table_content += f"""
                <tr>
                    <td style='background-color: {color}; color: white; font-weight: bold; padding: 5px;'>{category}</td>
                    <td style='padding: 5px;'>{range_text}</td>
                    <td style='text-align: center; padding: 5px;'>{result['count']}</td>
                    <td style='text-align: center; padding: 5px;'>{result['percentage']:.1f}%</td>
                </tr>
                """
            
            table_content += "</table>"
            results_text.setHtml(table_content)
            layout.addWidget(results_text)
            
            # Interpretación automática
            interpretation = QLabel("🔍 Interpretación Automática:")
            interpretation.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(interpretation)
            
            interp_text = QTextEdit()
            interp_text.setMaximumHeight(100)
            interp_text.setReadOnly(True)
            
            # Lógica de interpretación
            excellent_good = results['Excelente']['percentage'] + results['Muy Buena']['percentage'] + results['Buena']['percentage']
            poor_imperme = results['Pobre']['percentage'] + results['Muy Pobre']['percentage'] + results['Impermeable']['percentage']
            
            if excellent_good > 60:
                interp = "🟢 Reservorio de alta calidad con excelente potencial de flujo."
            elif excellent_good > 30:
                interp = "🟡 Reservorio de calidad moderada a buena."
            elif poor_imperme > 50:
                interp = "🔴 Reservorio de baja calidad con limitaciones de flujo significativas."
            else:
                interp = "🟡 Reservorio de calidad variable, requiere análisis detallado."
            
            interp_text.setPlainText(interp)
            layout.addWidget(interp_text)
            
            # Botón cerrar
            close_btn = QPushButton("Cerrar")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec_()
            
            # Actualizar UI
            self.update_curves_list()
            
        except Exception as e:
            self.log_activity(f"❌ Error clasificando permeabilidad: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en clasificación de permeabilidad:\n{str(e)}")
    
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
        """Mostrar detalles completos del análisis litológico."""
        info_text = """
<h2>🪨 Análisis Litológico en PyPozo</h2>

<h3>📊 Métodos de Análisis Disponibles</h3>

<h4>1. 📈 Análisis por Crossplots</h4>
<p><b>¿Qué es?</b> Gráficos de correlación entre diferentes registros de pozo para identificar patrones litológicos.</p>
<p><b>Tipos de Crossplots:</b></p>
<ul>
<li><b>Neutrón vs Densidad:</b> Identifica areniscas, calizas, dolomitas y efectos de gas</li>
<li><b>Neutrón vs PEF:</b> Separación precisa de minerales por propiedades nucleares</li>
<li><b>Densidad vs PEF:</b> Análisis mineralógico detallado independiente de porosidad</li>
<li><b>GR vs PEF:</b> Discriminación entre arcillas y minerales pesados</li>
<li><b>Thorium vs Potasio:</b> Análisis de tipos de arcilla y ambientes deposicionales</li>
</ul>
<p><b>Ventajas:</b> Identificación visual rápida, validación cruzada entre registros, detección de zonas anómalas</p>

<h4>2. 🎯 Clasificación de Facies Petrofísicas</h4>
<p><b>¿Qué es?</b> Agrupamiento automático de intervalos con propiedades similares para definir unidades de flujo.</p>
<p><b>Métodos de Clasificación:</b></p>
<ul>
<li><b>K-means Clustering:</b> Agrupamiento no supervisado basado en múltiples propiedades</li>
<li><b>Análisis Discriminante:</b> Clasificación supervisada con muestras de referencia</li>
<li><b>Redes Neuronales:</b> Reconocimiento de patrones complejos en datos</li>
<li><b>Árboles de Decisión:</b> Reglas lógicas para clasificación basada en umbrales</li>
</ul>
<p><b>Aplicaciones:</b> Definición de unidades de flujo, caracterización de heterogeneidades, optimización de terminaciones</p>

<h4>3. 🔬 Identificación Mineral</h4>
<p><b>¿Qué es?</b> Determinación cuantitativa de composición mineralógica usando respuestas específicas de registros.</p>
<p><b>Técnicas de Identificación:</b></p>
<ul>
<li><b>Inversión de Registros:</b> Solución de ecuaciones simultáneas para fracciones minerales</li>
<li><b>Análisis Espectral:</b> Uso de registros especializados (ECS, Litho-Density)</li>
<li><b>Modelos Probabilísticos:</b> Asignación de probabilidades a diferentes litologías</li>
<li><b>Análisis Multi-mineral:</b> Separación de mezclas complejas de minerales</li>
</ul>
<p><b>Resultados:</b> Porcentajes de cuarzo, calcita, dolomita, arcillas, feldespatos, etc.</p>

<h4>4. 🏆 Evaluación de Calidad de Reservorio</h4>
<p><b>¿Qué es?</b> Clasificación integral de intervalos según su potencial de producción de hidrocarburos.</p>
<p><b>Parámetros de Evaluación:</b></p>
<ul>
<li><b>Índice de Porosidad:</b> Clasificación de capacidad de almacenamiento</li>
<li><b>Índice de Permeabilidad:</b> Evaluación de capacidad de flujo</li>
<li><b>RQI (Reservoir Quality Index):</b> Índice integral de calidad</li>
<li><b>Índice de Arcillosidad:</b> Impacto de arcillas en las propiedades</li>
<li><b>Saturación de Hidrocarburos:</b> Potencial de producción comercial</li>
</ul>
<p><b>Clasificaciones Resultantes:</b> Excelente, Buena, Regular, Pobre, No-reservorio</p>

<h4>5. 🌊 Análisis de Ambiente Deposicional</h4>
<p><b>¿Qué es?</b> Interpretación del contexto geológico de depositación basado en patrones de registros.</p>
<p><b>Indicadores Utilizados:</b></p>
<ul>
<li><b>Patrones de GR:</b> Tendencias transgresivas/regresivas, ciclicidad</li>
<li><b>Espectroscopía de GR:</b> Relaciones Th/K para tipos de arcilla</li>
<li><b>Texturas de Resistividad:</b> Continuidad lateral, heterogeneidades</li>
<li><b>Variabilidad de Porosidad:</b> Energía del ambiente deposicional</li>
</ul>
<p><b>Ambientes Identificados:</b> Fluvial, deltaico, marino somero, turbidítico, eólico, lacustre</p>

<h3>🔧 Flujo de Trabajo Integrado</h3>
<ol>
<li><b>Control de Calidad:</b> Validación de registros y correcciones ambientales</li>
<li><b>Análisis Exploratorio:</b> Crossplots para identificar patrones principales</li>
<li><b>Clasificación Automática:</b> Agrupamiento de facies petrofísicas</li>
<li><b>Identificación Mineral:</b> Cuantificación de composición litológica</li>
<li><b>Evaluación de Calidad:</b> Clasificación de intervalos productivos</li>
<li><b>Interpretación Geológica:</b> Contexto deposicional y estructural</li>
<li><b>Validación y Reporte:</b> Comparación con datos independientes</li>
</ol>

<h3>💡 Mejores Prácticas</h3>
<ul>
<li><b>Validación Cruzada:</b> Use múltiples métodos para confirmar interpretaciones</li>
<li><b>Calibración Local:</b> Ajuste modelos con datos de núcleos y pruebas de pozo</li>
<li><b>Análisis de Incertidumbre:</b> Evalúe confiabilidad de resultados</li>
<li><b>Integración de Escalas:</b> Combine datos de pozo, núcleos y sísmica</li>
<li><b>Actualización Continua:</b> Refine interpretaciones con nueva información</li>
</ul>

<p><i>💻 PyPozo - Análisis litológico profesional para caracterización de reservorios</i></p>
"""
        
        # Crear ventana de información con scroll
        dialog = QDialog(self)
        dialog.setWindowTitle("📚 Guía Completa - Análisis Litológico")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # Área de texto con scroll
        text_widget = QTextEdit()
        text_widget.setHtml(info_text)
        text_widget.setReadOnly(True)
        
        layout.addWidget(text_widget)
        
        # Botón cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def generate_lithology_crossplots(self):
        """Generar crossplots litológicos."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Obtener curvas seleccionadas
            rhob_curve = self.lith_rhob_combo.currentText()
            nphi_curve = self.lith_nphi_combo.currentText()
            pef_curve = self.lith_pef_combo.currentText()
            gr_curve = self.lith_gr_combo.currentText()
            
            # Validar que tengamos al menos RHOB y NPHI
            if not rhob_curve or rhob_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva RHOB '{rhob_curve}' no disponible")
                return
            
            if not nphi_curve or nphi_curve not in self.current_well.data.columns:
                QMessageBox.warning(self, "Advertencia", f"Curva NPHI '{nphi_curve}' no disponible")
                return
            
            # Usar el analizador de litología
            rhob_data = self.current_well.data[rhob_curve]
            nphi_data = self.current_well.data[nphi_curve]
            pef_data = self.current_well.data[pef_curve] if pef_curve and pef_curve in self.current_well.data.columns else None
            
            self.log_activity(f"📊 Generando crossplots litológicos...")
            
            # Realizar análisis neutrón-densidad
            nd_result = self.lithology_analyzer.neutron_density_analysis(
                rhob=rhob_data,
                nphi=nphi_data,
                pe=pef_data,
                fluid_type='fresh_water'
            )
            
            if not nd_result.get('success', False):
                QMessageBox.critical(self, "Error", f"Error en análisis N-D: {nd_result.get('error', 'Error desconocido')}")
                return
            
            # Limpiar figura
            self.figure.clear()
            
            # Crear subplots para crossplots
            if pef_data is not None:
                # Con PEF: 3 crossplots
                gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
                ax1 = self.figure.add_subplot(gs[0, 0])  # NPHI vs RHOB
                ax2 = self.figure.add_subplot(gs[0, 1])  # PEF vs RHOB
                ax3 = self.figure.add_subplot(gs[1, :])  # NPHI vs PEF
            else:
                # Sin PEF: 1 crossplot principal
                ax1 = self.figure.add_subplot(111)
                ax2 = ax3 = None
            
            # Preparar datos válidos
            valid_mask = (~np.isnan(rhob_data)) & (~np.isnan(nphi_data))
            rhob_valid = rhob_data[valid_mask]
            nphi_valid = nphi_data[valid_mask]
            
            if len(rhob_valid) == 0:
                QMessageBox.warning(self, "Advertencia", "No hay datos válidos para generar crossplots")
                return
            
            # Crossplot 1: NPHI vs RHOB (Principal)
            scatter = ax1.scatter(rhob_valid, nphi_valid, c=rhob_valid, cmap='viridis', alpha=0.6, s=20)
            ax1.set_xlabel('RHOB (g/cm³)')
            ax1.set_ylabel('NPHI (fracción)')
            ax1.set_title('Crossplot Neutrón-Densidad')
            ax1.grid(True, alpha=0.3)
            
            # Añadir líneas de referencia mineralógica
            rhob_range = np.linspace(1.8, 3.0, 100)
            
            # Líneas de cuarzo
            ax1.plot([2.65, 2.65], [ax1.get_ylim()[0], ax1.get_ylim()[1]], 'r--', alpha=0.5, label='Cuarzo')
            # Líneas de calcita
            ax1.plot([2.71, 2.71], [ax1.get_ylim()[0], ax1.get_ylim()[1]], 'b--', alpha=0.5, label='Calcita')
            # Líneas de dolomita
            ax1.plot([2.87, 2.87], [ax1.get_ylim()[0], ax1.get_ylim()[1]], 'g--', alpha=0.5, label='Dolomita')
            
            ax1.legend(fontsize=8)
            
            # Colorbar para densidad
            cbar1 = self.figure.colorbar(scatter, ax=ax1)
            cbar1.set_label('RHOB (g/cm³)')
            
            # Crossplot 2: PEF vs RHOB (si disponible)
            if ax2 is not None and pef_data is not None:
                pef_valid = pef_data[valid_mask & (~np.isnan(pef_data))]
                rhob_pef = rhob_valid[~np.isnan(pef_data[valid_mask])]
                
                if len(pef_valid) > 0:
                    scatter2 = ax2.scatter(rhob_pef, pef_valid, c=pef_valid, cmap='plasma', alpha=0.6, s=20)
                    ax2.set_xlabel('RHOB (g/cm³)')
                    ax2.set_ylabel('PEF (barns/electron)')
                    ax2.set_title('Crossplot PEF-Densidad')
                    ax2.grid(True, alpha=0.3)
                    
                    # Líneas de referencia mineralógica para PEF
                    ax2.axhline(y=1.81, color='r', linestyle='--', alpha=0.5, label='Cuarzo (1.81)')
                    ax2.axhline(y=5.08, color='b', linestyle='--', alpha=0.5, label='Calcita (5.08)')
                    ax2.axhline(y=3.14, color='g', linestyle='--', alpha=0.5, label='Dolomita (3.14)')
                    ax2.axhline(y=2.8, color='orange', linestyle='--', alpha=0.5, label='Arcilla (2.8)')
                    
                    ax2.legend(fontsize=8)
                    
                    cbar2 = self.figure.colorbar(scatter2, ax=ax2)
                    cbar2.set_label('PEF (barns/electron)')
            
            # Crossplot 3: NPHI vs PEF (si disponible)
            if ax3 is not None and pef_data is not None:
                nphi_pef = nphi_valid[~np.isnan(pef_data[valid_mask])]
                
                if len(pef_valid) > 0:
                    scatter3 = ax3.scatter(nphi_pef, pef_valid, c=rhob_pef, cmap='coolwarm', alpha=0.6, s=20)
                    ax3.set_xlabel('NPHI (fracción)')
                    ax3.set_ylabel('PEF (barns/electron)')
                    ax3.set_title('Crossplot Neutrón-PEF')
                    ax3.grid(True, alpha=0.3)
                    
                    cbar3 = self.figure.colorbar(scatter3, ax=ax3)
                    cbar3.set_label('RHOB (g/cm³)')
            
            # Título general
            well_name = self.current_well.name or "Pozo Actual"
            self.figure.suptitle(f'Crossplots Litológicos - {well_name}', fontsize=14, fontweight='bold')
            
            # Actualizar canvas
            self.canvas.draw()
            
            # Mostrar resultados en el área de texto
            self.lithology_results_text.clear()
            self.lithology_results_text.append("✅ Crossplots litológicos generados")
            self.lithology_results_text.append(f"📊 Datos procesados: {len(rhob_valid)} puntos")
            self.lithology_results_text.append(f"📈 Curvas utilizadas:")
            self.lithology_results_text.append(f"   • RHOB: {rhob_curve}")
            self.lithology_results_text.append(f"   • NPHI: {nphi_curve}")
            if pef_data is not None:
                self.lithology_results_text.append(f"   • PEF: {pef_curve}")
            
            # Añadir estadísticas básicas
            self.lithology_results_text.append(f"\n📊 Estadísticas RHOB:")
            self.lithology_results_text.append(f"   • Promedio: {rhob_valid.mean():.3f} g/cm³")
            self.lithology_results_text.append(f"   • Rango: {rhob_valid.min():.3f} - {rhob_valid.max():.3f} g/cm³")
            
            self.lithology_results_text.append(f"\n📊 Estadísticas NPHI:")
            self.lithology_results_text.append(f"   • Promedio: {nphi_valid.mean():.3f}")
            self.lithology_results_text.append(f"   • Rango: {nphi_valid.min():.3f} - {nphi_valid.max():.3f}")
            
            if 'warnings' in nd_result and nd_result['warnings']:
                self.lithology_results_text.append(f"\n⚠️ Advertencias QC:")
                for warning in nd_result['warnings']:
                    self.lithology_results_text.append(f"   • {warning}")
            
            self.log_activity(f"✅ Crossplots generados exitosamente")
            
        except Exception as e:
            self.log_activity(f"❌ Error generando crossplots: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error generando crossplots litológicos:\n{str(e)}")
    
    def classify_facies(self):
        """Clasificar facies litológicas."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
                return
            
            # Obtener parámetros de la UI
            n_facies = self.lith_n_facies_spinbox.value()
            auto_detect = self.lith_auto_facies.isChecked()
            vcl_cutoff = self.lith_vcl_cutoff_spinbox.value()
            porosity_cutoff = self.lith_porosity_cutoff_spinbox.value()
            
            # Obtener curvas
            gr_curve = self.lith_gr_combo.currentText()
            rhob_curve = self.lith_rhob_combo.currentText()
            nphi_curve = self.lith_nphi_combo.currentText()
            pef_curve = self.lith_pef_combo.currentText()
            
            # Verificar curvas mínimas requeridas
            required_curves = {'GR': gr_curve, 'RHOB': rhob_curve, 'NPHI': nphi_curve}
            missing_curves = []
            
            for curve_type, curve_name in required_curves.items():
                if not curve_name or curve_name not in self.current_well.data.columns:
                    missing_curves.append(curve_type)
            
            if missing_curves:
                QMessageBox.warning(self, "Advertencia", 
                                  f"Curvas faltantes para clasificación: {', '.join(missing_curves)}")
                return
            
            self.log_activity(f"🎯 Clasificando facies litológicas...")
            
            # Preparar datos
            data_for_clustering = []
            curve_names = []
            
            # GR (normalizado)
            gr_data = self.current_well.data[gr_curve]
            gr_norm = (gr_data - gr_data.min()) / (gr_data.max() - gr_data.min())
            data_for_clustering.append(gr_norm)
            curve_names.append('GR_norm')
            
            # RHOB
            rhob_data = self.current_well.data[rhob_curve]
            data_for_clustering.append(rhob_data)
            curve_names.append('RHOB')
            
            # NPHI
            nphi_data = self.current_well.data[nphi_curve]
            data_for_clustering.append(nphi_data)
            curve_names.append('NPHI')
            
            # PEF si está disponible
            if pef_curve and pef_curve in self.current_well.data.columns:
                pef_data = self.current_well.data[pef_curve]
                data_for_clustering.append(pef_data)
                curve_names.append('PEF')
            
            # Crear matriz de datos
            X = np.column_stack(data_for_clustering)
            
            # Remover filas con NaN
            valid_mask = ~np.isnan(X).any(axis=1)
            X_clean = X[valid_mask]
            
            if len(X_clean) < 10:
                QMessageBox.warning(self, "Advertencia", "Datos insuficientes para clasificación de facies")
                return
            
            # Normalizar los datos para clustering
            from sklearn.preprocessing import StandardScaler
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_clean)
            
            # Determinar número óptimo de clusters si auto_detect está habilitado
            if auto_detect:
                silhouette_scores = []
                inertias = []
                k_range = range(2, min(9, len(X_clean) // 10))  # Máximo 8 clusters
                
                if len(k_range) == 0:
                    k_range = [2, 3]
                
                for k in k_range:
                    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                    cluster_labels = kmeans.fit_predict(X_scaled)
                    
                    if len(np.unique(cluster_labels)) > 1:  # Asegurar que hay múltiples clusters
                        sil_score = silhouette_score(X_scaled, cluster_labels)
                        silhouette_scores.append(sil_score)
                        inertias.append(kmeans.inertia_)
                    else:
                        silhouette_scores.append(0)
                        inertias.append(float('inf'))
                
                # Seleccionar k óptimo basado en silhouette score
                if silhouette_scores:
                    best_k = k_range[np.argmax(silhouette_scores)]
                    n_facies = best_k
                    self.log_activity(f"🔍 Número óptimo de facies detectado: {n_facies}")
            
            # Realizar clustering final
            kmeans = KMeans(n_clusters=n_facies, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            # Crear array de facies para todo el dataset
            facies_full = np.full(len(self.current_well.data), np.nan)
            facies_full[valid_mask] = cluster_labels
            
            # Asignar nombres descriptivos a las facies basados en características
            facies_names = self._assign_facies_names(kmeans.cluster_centers_, scaler, curve_names)
            
            # Crear curva de facies categórica
            facies_categorical = np.full(len(self.current_well.data), 'Unknown', dtype='<U20')
            for i, facies_id in enumerate(facies_full):
                if not np.isnan(facies_id):
                    facies_categorical[i] = facies_names[int(facies_id)]
            
            # Agregar curva de facies al pozo
            facies_curve_name = "FACIES_CLASS"
            success = self.current_well.add_curve(
                curve_name=facies_curve_name,
                data=facies_categorical,
                units='category',
                description=f'Petrophysical facies classification ({n_facies} facies)'
            )
            
            if not success:
                QMessageBox.critical(self, "Error", f"No se pudo agregar curva {facies_curve_name}")
                return
            
            # Calcular estadísticas por facies
            facies_stats = {}
            for i, facies_name in enumerate(facies_names):
                mask = cluster_labels == i
                if np.sum(mask) > 0:
                    stats = {
                        'count': np.sum(mask),
                        'percentage': (np.sum(mask) / len(cluster_labels)) * 100,
                        'avg_gr': np.mean(gr_data[valid_mask][mask]),
                        'avg_rhob': np.mean(rhob_data[valid_mask][mask]),
                        'avg_nphi': np.mean(nphi_data[valid_mask][mask])
                    }
                    
                    if pef_curve and pef_curve in self.current_well.data.columns:
                        pef_facies = pef_data[valid_mask][mask]
                        stats['avg_pef'] = np.mean(pef_facies[~np.isnan(pef_facies)])
                    
                    facies_stats[facies_name] = stats
            
            # Mostrar resultados
            self.lithology_results_text.clear()
            self.lithology_results_text.append(f"✅ Clasificación de facies completada")
            self.lithology_results_text.append(f"🎯 Número de facies: {n_facies}")
            self.lithology_results_text.append(f"📊 Puntos clasificados: {len(cluster_labels)}")
            self.lithology_results_text.append(f"📈 Curva creada: {facies_curve_name}")
            
            if auto_detect:
                self.lithology_results_text.append(f"🔍 Detección automática activada")
            
            self.lithology_results_text.append(f"\n📊 Distribución de Facies:")
            
            for facies_name, stats in facies_stats.items():
                self.lithology_results_text.append(f"\n🏷️ {facies_name}:")
                self.lithology_results_text.append(f"   • Puntos: {stats['count']} ({stats['percentage']:.1f}%)")
                self.lithology_results_text.append(f"   • GR promedio: {stats['avg_gr']:.1f}")
                self.lithology_results_text.append(f"   • RHOB promedio: {stats['avg_rhob']:.3f} g/cm³")
                self.lithology_results_text.append(f"   • NPHI promedio: {stats['avg_nphi']:.3f}")
                if 'avg_pef' in stats:
                    self.lithology_results_text.append(f"   • PEF promedio: {stats['avg_pef']:.2f}")
            
            # Generar gráfico de facies si hay espacio
            self._plot_facies_visualization(cluster_labels, X_clean, curve_names, facies_names)
            
            self.log_activity(f"✅ Facies clasificadas: {facies_curve_name}")
            self.update_curves_list()
            
        except ImportError:
            QMessageBox.critical(self, "Error", 
                               "Scikit-learn no está disponible. Instale con: pip install scikit-learn")
        except Exception as e:
            self.log_activity(f"❌ Error clasificando facies: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en clasificación de facies:\n{str(e)}")
    
    def _assign_facies_names(self, cluster_centers, scaler, curve_names):
        """Asignar nombres descriptivos a las facies basados en características del cluster."""
        n_clusters = len(cluster_centers)
        facies_names = []
        
        # Desnormalizar los centros para interpretación
        centers_original = scaler.inverse_transform(cluster_centers)
        
        for i, center in enumerate(centers_original):
            # Obtener índices de las curvas
            gr_idx = curve_names.index('GR_norm') if 'GR_norm' in curve_names else 0
            rhob_idx = curve_names.index('RHOB') if 'RHOB' in curve_names else 1
            nphi_idx = curve_names.index('NPHI') if 'NPHI' in curve_names else 2
            pef_idx = curve_names.index('PEF') if 'PEF' in curve_names else None
            
            gr_val = center[gr_idx]
            rhob_val = center[rhob_idx]
            nphi_val = center[nphi_idx]
            pef_val = center[pef_idx] if pef_idx is not None else None
            
            # Lógica de clasificación basada en propiedades
            if gr_val < 0.3:  # Bajo GR
                if rhob_val > 2.7:  # Alta densidad
                    if pef_val and pef_val > 4.0:
                        name = "Carbonato_Limpio"
                    else:
                        name = "Arenisca_Limpia"
                else:
                    name = "Arena_Porosa"
            elif gr_val < 0.7:  # GR moderado
                if rhob_val > 2.6:
                    name = "Carbonato_Arcilloso"
                else:
                    name = "Arenisca_Arcillosa"
            else:  # Alto GR
                if nphi_val > 0.3:
                    name = "Lutita_Porosa"
                else:
                    name = "Lutita_Compacta"
            
            facies_names.append(f"F{i+1}_{name}")
        
        return facies_names
    
    def _plot_facies_visualization(self, cluster_labels, X_clean, curve_names, facies_names):
        """Crear visualización de las facies clasificadas."""
        try:
            # Limpiar figura para mostrar facies
            self.figure.clear()
            
            # Crear subplot para visualización 2D principal
            ax = self.figure.add_subplot(111)
            
            # Usar las dos primeras componentes más significativas
            # Típicamente GR vs RHOB o NPHI vs RHOB
            if len(curve_names) >= 2:
                x_data = X_clean[:, 1]  # RHOB generalmente
                y_data = X_clean[:, 2]  # NPHI generalmente
                x_label = curve_names[1] if len(curve_names) > 1 else 'Component 1'
                y_label = curve_names[2] if len(curve_names) > 2 else 'Component 2'
            else:
                x_data = X_clean[:, 0]
                y_data = X_clean[:, 1] if X_clean.shape[1] > 1 else X_clean[:, 0]
                x_label = curve_names[0] if curve_names else 'Component 1'
                y_label = curve_names[1] if len(curve_names) > 1 else 'Component 2'
            
            # Definir colores para las facies
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            
            # Plotear cada facies con color diferente
            for i, facies_name in enumerate(facies_names):
                mask = cluster_labels == i
                if np.sum(mask) > 0:
                    color = colors[i % len(colors)]
                    ax.scatter(x_data[mask], y_data[mask], 
                             c=color, alpha=0.6, s=20, label=facies_name)
            
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(f'Clasificación de Facies Petrofísicas - {len(facies_names)} Facies')
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            
            # Ajustar layout
            self.figure.tight_layout()
            
            # Actualizar canvas
            self.canvas.draw()
            
        except Exception as e:
            # Si falla la visualización, continuar sin ella
            self.log_activity(f"⚠️ Error en visualización de facies: {str(e)}")
    
    def run_comprehensive_analysis(self):
        """Ejecutar análisis petrofísico completo."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "No hay pozo seleccionado")
            return
        
        try:
            # Mostrar diálogo de confirmación con opciones
            dialog = QDialog(self)
            dialog.setWindowTitle("Análisis Petrofísico Completo")
            dialog.setMinimumSize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # Título
            title = QLabel("🔬 Análisis Petrofísico Completo")
            title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E8B57; margin: 10px;")
            layout.addWidget(title)
            
            # Descripción
            desc = QLabel("Este análisis ejecutará todos los cálculos petrofísicos disponibles:")
            layout.addWidget(desc)
            
            # Lista de análisis
            analysis_list = QLabel("""
• Volumen de Arcilla (VCL)
• Porosidad Efectiva (PHIE)
• Saturación de Agua (Sw)
• Permeabilidad (múltiples métodos)
• Análisis Litológico Completo
• Clasificación de Facies
• Evaluación de Calidad de Reservorio
            """)
            analysis_list.setStyleSheet("margin: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
            layout.addWidget(analysis_list)
            
            # Opciones
            options_group = QGroupBox("Opciones de Análisis")
            options_layout = QVBoxLayout(options_group)
            
            self.comp_calc_vcl = QCheckBox("Calcular VCL")
            self.comp_calc_vcl.setChecked(True)
            options_layout.addWidget(self.comp_calc_vcl)
            
            self.comp_calc_porosity = QCheckBox("Calcular Porosidad")
            self.comp_calc_porosity.setChecked(True)
            options_layout.addWidget(self.comp_calc_porosity)
            
            self.comp_calc_sw = QCheckBox("Calcular Saturación de Agua")
            self.comp_calc_sw.setChecked(True)
            options_layout.addWidget(self.comp_calc_sw)
            
            self.comp_calc_perm = QCheckBox("Calcular Permeabilidad")
            self.comp_calc_perm.setChecked(True)
            options_layout.addWidget(self.comp_calc_perm)
            
            self.comp_lithology_analysis = QCheckBox("Análisis Litológico Completo")
            self.comp_lithology_analysis.setChecked(True)
            options_layout.addWidget(self.comp_lithology_analysis)
            
            layout.addWidget(options_group)
            
            # Botones
            buttons_layout = QHBoxLayout()
            
            run_btn = QPushButton("🚀 Ejecutar Análisis")
            run_btn.clicked.connect(dialog.accept)
            buttons_layout.addWidget(run_btn)
            
            cancel_btn = QPushButton("Cancelar")
            cancel_btn.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_btn)
            
            layout.addLayout(buttons_layout)
            
            # Ejecutar diálogo
            if dialog.exec_() != QDialog.Accepted:
                return
            
            # Iniciar análisis completo
            self.log_activity("🚀 Iniciando análisis petrofísico completo...")
            
            # Limpiar resultados anteriores
            self.petro_results.clear()
            
            total_steps = 0
            current_step = 0
            
            # Contar pasos habilitados
            if self.comp_calc_vcl.isChecked():
                total_steps += 1
            if self.comp_calc_porosity.isChecked():
                total_steps += 1
            if self.comp_calc_sw.isChecked():
                total_steps += 1
            if self.comp_calc_perm.isChecked():
                total_steps += 1
            if self.comp_lithology_analysis.isChecked():
                total_steps += 3  # Crossplots, facies, quality
            
            # Mostrar barra de progreso
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(total_steps)
            self.progress_bar.setValue(0)
            
            # Ejecutar análisis paso a paso
            success_count = 0
            error_count = 0
            
            # 1. VCL
            if self.comp_calc_vcl.isChecked():
                try:
                    self.log_activity("🏔️ Calculando VCL...")
                    self.calculate_vcl()
                    success_count += 1
                    self.petro_results.append("✅ VCL calculado")
                except Exception as e:
                    error_count += 1
                    self.petro_results.append(f"❌ Error VCL: {str(e)[:50]}...")
                    self.log_activity(f"❌ Error VCL: {str(e)}")
                
                current_step += 1
                self.progress_bar.setValue(current_step)
                QApplication.processEvents()  # Actualizar UI
            
            # 2. Porosidad
            if self.comp_calc_porosity.isChecked():
                try:
                    self.log_activity("🕳️ Calculando Porosidad...")
                    self.calculate_porosity()
                    success_count += 1
                    self.petro_results.append("✅ Porosidad calculada")
                except Exception as e:
                    error_count += 1
                    self.petro_results.append(f"❌ Error Porosidad: {str(e)[:50]}...")
                    self.log_activity(f"❌ Error Porosidad: {str(e)}")
                
                current_step += 1
                self.progress_bar.setValue(current_step)
                QApplication.processEvents()
            
            # 3. Saturación de Agua
            if self.comp_calc_sw.isChecked():
                try:
                    self.log_activity("💧 Calculando Saturación de Agua...")
                    self.calculate_water_saturation()
                    success_count += 1
                    self.petro_results.append("✅ Saturación de agua calculada")
                except Exception as e:
                    error_count += 1
                    self.petro_results.append(f"❌ Error Sw: {str(e)[:50]}...")
                    self.log_activity(f"❌ Error Sw: {str(e)}")
                
                current_step += 1
                self.progress_bar.setValue(current_step)
                QApplication.processEvents()
            
            # 4. Permeabilidad
            if self.comp_calc_perm.isChecked():
                try:
                    self.log_activity("🌊 Calculando Permeabilidad...")
                    self.calculate_permeability()
                    success_count += 1
                    self.petro_results.append("✅ Permeabilidad calculada")
                except Exception as e:
                    error_count += 1
                    self.petro_results.append(f"❌ Error Permeabilidad: {str(e)[:50]}...")
                    self.log_activity(f"❌ Error Permeabilidad: {str(e)}")
                
                current_step += 1
                self.progress_bar.setValue(current_step)
                QApplication.processEvents()
            
            # 5. Análisis Litológico
            if self.comp_lithology_analysis.isChecked():
                # 5.1 Crossplots
                try:
                    self.log_activity("📊 Generando crossplots litológicos...")
                    self.generate_lithology_crossplots()
                    success_count += 1
                    self.petro_results.append("✅ Crossplots generados")
                except Exception as e:
                    error_count += 1
                    self.petro_results.append(f"❌ Error Crossplots: {str(e)[:50]}...")
                    self.log_activity(f"❌ Error Crossplots: {str(e)}")
                
                current_step += 1
                self.progress_bar.setValue(current_step)
                QApplication.processEvents()
                
                # 5.2 Clasificación de Facies
                try:
                    self.log_activity("🎯 Clasificando facies...")
                    self.classify_facies()
                    success_count += 1
                    self.petro_results.append("✅ Facies clasificadas")
                except Exception as e:
                    error_count += 1
                    self.petro_results.append(f"❌ Error Facies: {str(e)[:50]}...")
                    self.log_activity(f"❌ Error Facies: {str(e)}")
                
                current_step += 1
                self.progress_bar.setValue(current_step)
                QApplication.processEvents()
                
                # 5.3 Evaluación de Calidad
                try:
                    self.log_activity("🏆 Evaluando calidad de reservorio...")
                    self._perform_reservoir_quality_assessment()
                    success_count += 1
                    self.petro_results.append("✅ Calidad evaluada")
                except Exception as e:
                    error_count += 1
                    self.petro_results.append(f"❌ Error Calidad: {str(e)[:50]}...")
                    self.log_activity(f"❌ Error Calidad: {str(e)}")
                
                current_step += 1
                self.progress_bar.setValue(current_step)
                QApplication.processEvents()
            
            # Finalizar
            self.progress_bar.setVisible(False)
            
            # Resumen final
            total_analyses = success_count + error_count
            success_rate = (success_count / total_analyses * 100) if total_analyses > 0 else 0
            
            self.petro_results.append(f"\n📊 RESUMEN DEL ANÁLISIS COMPLETO:")
            self.petro_results.append(f"✅ Exitosos: {success_count}")
            self.petro_results.append(f"❌ Errores: {error_count}")
            self.petro_results.append(f"📈 Tasa de éxito: {success_rate:.1f}%")
            
            # Actualizar listas de curvas
            self.update_curves_list()
            self.update_petrophysics_ui()
            
            # Mensaje final
            if success_count > 0:
                if error_count == 0:
                    final_msg = f"✅ Análisis completo exitoso!\n\n{success_count} análisis completados correctamente."
                else:
                    final_msg = f"⚠️ Análisis parcialmente completado.\n\n✅ Exitosos: {success_count}\n❌ Errores: {error_count}\n\nRevise el log para detalles de errores."
                
                QMessageBox.information(self, "Análisis Completado", final_msg)
            else:
                QMessageBox.critical(self, "Error", "No se pudo completar ningún análisis.\nRevise las curvas disponibles y configuraciones.")
            
            self.log_activity(f"🔬 Análisis completo finalizado: {success_count}/{total_analyses} exitosos")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.log_activity(f"❌ Error en análisis completo: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en análisis completo:\n{str(e)}")

    # ==================== FUNCIONES DLC PATREON ====================
    
    def setup_patreon_menu(self):
        """Configurar menú de funciones Patreon DLC."""
        if self.has_patreon_dlc:
            # Crear menú experimental
            experimental_menu = self.menuBar().addMenu('🌟 Experimental')
            experimental_menu.addAction('🤖 Completar Registros IA', self.open_neural_completion)
            experimental_menu.addAction('🔬 Análisis Avanzado', self.open_advanced_analysis)
            experimental_menu.addSeparator()
            experimental_menu.addAction('ℹ️ Acerca del DLC', self.show_patreon_info)
        else:
            # Mostrar menú de invitación - más llamativo
            patreon_menu = self.menuBar().addMenu('💎 Premium ✨')
            patreon_menu.addAction('🚀 ¡Ver Funciones IA Premium!', self.show_patreon_invitation)
            patreon_menu.addSeparator()
            patreon_menu.addAction('🌟 Únete a Patreon - $15/mes', self.open_patreon_page)
            patreon_menu.addAction('📥 Ya soy Patreon - Descargar DLC', self.download_patreon_dlc)
    
    def open_neural_completion(self):
        """Abrir diálogo de completado intra-pozo con IA."""
        try:
            if len(self.wells) < 1:
                QMessageBox.warning(self, "Advertencia", 
                                  "Se requiere al menos 1 pozo para el completado inteligente intra-pozo")
                return
            
            if not self.has_patreon_dlc:
                self.show_patreon_invitation()
                return
            
            # Llamar al DLC con el nuevo workflow intra-pozo
            dialog = self.patreon_dlc.create_completion_dialog(self.wells, self)
            result = dialog.exec_()
            
            # Si el completado fue exitoso, actualizar la interfaz
            if result == QDialog.Accepted:
                self.log_activity("🤖 Completado neural intra-pozo ejecutado exitosamente")
                # Refrescar la vista de curvas si hay un pozo seleccionado
                if self.current_well:
                    self.update_curves_list()
            
        except Exception as e:
            error_msg = f"Error abriendo completado IA:\n{str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def open_advanced_analysis(self):
        """Abrir análisis avanzado."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero")
                return
            
            # Llamar al DLC
            dialog = self.patreon_dlc.create_advanced_analysis_dialog(self.current_well, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo análisis avanzado:\n{str(e)}")
    
    def open_advanced_lithology(self):
        """Abrir análisis litológico avanzado con IA."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero")
                return
            
            # Llamar al DLC
            dialog = self.patreon_dlc.advanced_lithology.create_dialog(self.current_well, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo análisis litológico IA:\n{str(e)}")
    
    def open_ai_interpreter(self):
        """Abrir interpretador automático de IA."""
        try:
            if not self.current_well:
                QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero")
                return
            
            # Llamar al DLC
            dialog = self.patreon_dlc.ai_interpreter.create_dialog(self.current_well, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo interpretador IA:\n{str(e)}")
    
    def show_patreon_info(self):
        """Mostrar información del DLC Patreon."""
        info_text = """
<h2>🌟 PyPozo Premium DLC</h2>

<h3>✨ Funciones Experimentales Activas:</h3>
<ul>
<li>🤖 <b>Completado Inteligente de Registros</b> - IA para extender rangos de profundidad</li>
<li>🔬 <b>Análisis Petrofísico Avanzado</b> - Modelos ML para interpretación</li>
<li>🧠 <b>Redes Neuronales para Litología</b> - Clasificación automática avanzada</li>
<li>📊 <b>Predicción de Propiedades</b> - Estimación de parámetros faltantes</li>
</ul>

<h3>🙏 Gracias por el apoyo en Patreon!</h3>
<p>Tu suscripción permite el desarrollo continuo de nuevas funcionalidades.</p>

<p><i>💻 PyPozo Premium - Análisis de pozos con IA</i></p>
"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Acerca del DLC Premium")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        text_widget = QTextEdit()
        text_widget.setHtml(info_text)
        text_widget.setReadOnly(True)
        layout.addWidget(text_widget)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def show_patreon_invitation(self):
        """Mostrar invitación a Patreon."""
        invitation_text = """
<h2>� ¡Desbloquea el Poder de la Inteligencia Artificial en PyPozo!</h2>

<div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #28a745; margin: 10px 0;">
<h3>💡 ¿Qué acabas de intentar usar?</h3>
<p><b>Funcionalidades experimentales con IA</b> que transformarán tu flujo de trabajo de análisis de pozos.</p>
</div>

<h3>🤖 Completado Inteligente Intra-Pozo con LSTM</h3>
<ul>
<li>🎯 <b>Redes Neuronales LSTM</b> que aprenden patrones entre curvas del mismo pozo</li>
<li>⚡ <b>Extiende curvas incompletas automáticamente</b> usando correlaciones internas</li>
<li>📊 <b>Elimina gaps y completa rangos faltantes</b> con precisión neural</li>
<li>✅ <b>Validación cruzada en tiempo real</b> con métricas de confianza</li>
<li>🔬 <b>Análisis inteligente de rangos</b> por cada curva individual</li>
</ul>

<h3>🧠 Análisis Petrofísico Avanzado con Machine Learning</h3>
<ul>
<li>🔬 <b>Interpretación automática de litologías</b> usando modelos entrenados</li>
<li>💎 <b>Identificación inteligente de zonas productivas</b> con IA</li>
<li>📈 <b>Predicción de propiedades faltantes</b> basada en correlaciones ocultas</li>
<li>🎲 <b>Análisis de incertidumbre cuantificado</b> matemáticamente</li>
</ul>

<h3>⭐ Clasificación Litológica de Nueva Generación</h3>
<ul>
<li>🌟 <b>Redes neuronales</b> entrenadas en miles de pozos reales</li>
<li>🏷️ <b>Reconocimiento automático de facies</b> sedimentarias</li>
<li>🎯 <b>Crossplots inteligentes</b> con clustering automático</li>
<li>📊 <b>Interpretación geológica asistida</b> por IA nivel profesional</li>
</ul>

<div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
<h3>💰 ¡Acceso Completo por Solo $15/mes!</h3>
<p><b>� Beneficios del Patreon Premium:</b></p>
<ul>
<li>🚀 <b>Todas las funciones IA</b> desbloqueadas inmediatamente</li>
<li>⚡ <b>Updates prioritarios</b> - nuevas funciones antes que nadie</li>
<li>💬 <b>Soporte técnico directo</b> conmigo (el desarrollador)</li>
<li>�️ <b>Voz en el desarrollo</b> - decides qué funciones implementar</li>
<li>📚 <b>Tutoriales exclusivos</b> y casos de estudio reales</li>
</ul>
</div>

<h3>🙏 Apoya el Desarrollo Independiente</h3>
<p>PyPozo es un <b>proyecto independiente</b> desarrollado con pasión para la comunidad geológica. 
Tu suscripción permite:</p>
<ul>
<li>⚗️ <b>Investigación continua</b> en IA aplicada a geociencias</li>
<li>🔧 <b>Desarrollo de nuevas funcionalidades</b> avanzadas</li>
<li>📖 <b>Documentación y tutoriales</b> de calidad profesional</li>
<li>🆓 <b>Mantener la versión básica siempre gratuita</b></li>
</ul>

<div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; text-align: center; margin: 10px 0;">
<b>💝 ¡Tu apoyo hace la diferencia! Únete a la revolución de la IA en geociencias</b>
</div>
"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("� ¡Desbloquea Funciones Premium!")
        dialog.resize(800, 750)
        
        layout = QVBoxLayout(dialog)
        
        text_widget = QTextEdit()
        text_widget.setHtml(invitation_text)
        text_widget.setReadOnly(True)
        layout.addWidget(text_widget)
        
        buttons_layout = QHBoxLayout()
        
        patreon_btn = QPushButton("🌟 ¡ÚNETE AHORA! - patreon.com/chemitas")
        patreon_btn.clicked.connect(self.open_patreon_page)
        patreon_btn.setStyleSheet("""
            background-color: #ff424d; 
            color: white; 
            font-weight: bold; 
            padding: 15px; 
            font-size: 16px;
            border-radius: 8px;
            border: 3px solid #ffd700;
        """)
        buttons_layout.addWidget(patreon_btn)
        
        download_btn = QPushButton("📥 Ya soy Patreon - Descargar DLC")
        download_btn.clicked.connect(self.download_patreon_dlc)
        download_btn.setStyleSheet("""
            background-color: #007bff; 
            color: white; 
            font-weight: bold; 
            padding: 12px;
            border-radius: 5px;
        """)
        buttons_layout.addWidget(download_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("padding: 10px;")
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        dialog.exec_()
    
    def open_patreon_page(self):
        """Abrir página de Patreon."""
        import webbrowser
        webbrowser.open("https://www.patreon.com/chemitas")  # Tu URL real de Patreon
        
    def download_patreon_dlc(self):
        """Descargar DLC de Patreon."""
        download_text = """
¡Gracias por ser un suscriptor de Patreon! 🎉

Para acceder a las funciones Premium de PyPozo:

📥 INSTRUCCIONES DE DESCARGA:

1. 📱 Ve a tu página de Patreon: patreon.com/chemitas
2. 📁 Busca la publicación "PyPozo Premium DLC"
3. ⬇️ Descarga el archivo "patreon_dlc.zip"
4. 📂 Extrae la carpeta "patreon_dlc" en la misma ubicación que pypozo_app.py
5. 🔄 Reinicia PyPozo para activar las funciones

🔧 ESTRUCTURA CORRECTA:
tu_carpeta/
├── pypozo_app.py
├── patreon_dlc/          ← Esta carpeta debe estar aquí
│   ├── __init__.py
│   ├── neural_completion.py
│   └── ...

✅ Una vez instalado correctamente:
• El menú cambiará a "🌟 Experimental" 
• Los botones Premium mostrarán "¡ACTIVO!"
• Tendrás acceso completo a todas las funciones IA

❓ ¿PROBLEMAS? 
Envíame un mensaje directo en Patreon y te ayudo personalmente.

💝 ¡Gracias por apoyar el desarrollo de PyPozo!
        """
        
        QMessageBox.information(self, "📥 Descarga DLC Premium", download_text)

    def show_download_instructions(self):
        """Mostrar instrucciones de descarga para suscriptores."""
        # Reutilizar la funcionalidad existente
        self.download_patreon_dlc()


if __name__ == "__main__":
    if not PYQT5_AVAILABLE:
        print("❌ PyQt5 no está disponible. Instale PyQt5 para usar la GUI: pip install PyQt5")
        sys.exit(1)
    app = QApplication(sys.argv)
    window = PyPozoApp()
    window.show()
    sys.exit(app.exec_())
