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
        QListWidget, QListWidgetItem, QProgressBar, QFrame, QScrollArea
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
        
        self.init_ui()
        self.setup_logging()
        
        logger.info("🚀 PyPozo App iniciada")
        self.status_bar.showMessage("✅ PyPozo App lista para usar")
    
    def init_ui(self):
        """Inicializar la interfaz de usuario."""
        self.setWindowTitle("PyPozo App - Análisis Profesional de Pozos")
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
                logging.FileHandler('pypozo_app.log'),
                logging.StreamHandler()
            ]
        )
    
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
        self.load_thread = WellLoadThread(file_path)
        self.load_thread.well_loaded.connect(self.on_well_loaded)
        self.load_thread.error_occurred.connect(self.on_load_error)
        self.load_thread.progress_updated.connect(self.progress_bar.setValue)
        self.load_thread.start()
    
    def on_well_loaded(self, well: WellManager, filename: str):
        """Manejar pozo cargado exitosamente."""
        well_name = well.name or filename
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
        
        # Crear subplots usando plt.subplot en lugar de self.figure.subplots
        # para evitar problemas con arrays booleanos
        for i, curve_name in enumerate(curves):
            ax = self.figure.add_subplot(1, n_curves, i + 1)
            
            if curve_name in df.columns:
                curve_data = df[curve_name].dropna()
                
                # Verificar que tenemos datos válidos
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
                
                values = values[valid_mask]
                depth = depth[valid_mask]
                
                # Graficar
                color = colors[i % len(colors)]
                ax.plot(values, depth, linewidth=1.5, color=color, label=curve_name)
                ax.fill_betweenx(depth, values, alpha=0.3, color=color)
                
                # Obtener unidades para la etiqueta
                units = well.get_curve_units(curve_name)
                xlabel = f'{curve_name} ({units})' if units else curve_name
                
                # Configurar ejes
                ax.set_xlabel(xlabel, fontsize=11, fontweight='bold')
                ax.set_title(curve_name, fontsize=12, fontweight='bold', pad=15)
                ax.invert_yaxis()  # Profundidad hacia abajo
                ax.grid(True, alpha=0.3)
                
                # Estadísticas
                stats_text = f'N: {len(values)}\nMin: {values.min():.1f}\nMax: {values.max():.1f}\nμ: {values.mean():.1f}'
                
                ax.text(0.02, 0.02, stats_text, transform=ax.transAxes,
                       verticalalignment='bottom', horizontalalignment='left',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9),
                       fontsize=8, fontfamily='monospace')
                
                # Solo el primer subplot tiene etiqueta Y
                if i == 0:
                    ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
            else:
                self.log_activity(f"⚠️ Curva {curve_name} no encontrada en los datos")
        
        # Título principal
        depth_range = well.depth_range
        title = f'{well.name} | Profundidad: {depth_range[0]:.0f}-{depth_range[1]:.0f}m'
        self.figure.suptitle(title, fontsize=14, fontweight='bold')
        
        # Título principal
        depth_range = well.depth_range
        title = f'{well.name} | Profundidad: {depth_range[0]:.0f}-{depth_range[1]:.0f}m'
        self.figure.suptitle(title, fontsize=14, fontweight='bold')
        
        # Ajustar layout de forma segura
        try:
            self.figure.tight_layout()
            self.figure.subplots_adjust(top=0.9)
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
    
    # ========== FUNCIONES AUXILIARES ==========
    
    def remove_well(self):
        """Remover pozo seleccionado."""
        current_item = self.wells_tree.currentItem()
        if not current_item:
            return
        
        well_name = current_item.data(0, Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Eliminar el pozo '{well_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remover del diccionario
            if well_name in self.wells:
                del self.wells[well_name]
            
            # Remover del árbol
            self.wells_tree.takeTopLevelItem(
                self.wells_tree.indexOfTopLevelItem(current_item)
            )
            
            # Limpiar selección actual si es la misma
            if self.current_well_name == well_name:
                self.current_well = None
                self.current_well_name = ""
                self.props_text.clear()
                self.curves_list.clear()
                self.remove_well_btn.setEnabled(False)
                self.plot_btn.setEnabled(False)
                self.plot_together_btn.setEnabled(False)
                self.plot_all_btn.setEnabled(False)
            
            self.update_wells_count()
            self.update_comparison_list()
            self.log_activity(f"🗑️ Pozo removido: {well_name}")
    
    def clear_all_wells(self):
        """Limpiar todos los pozos."""
        if not self.wells:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar todos los pozos ({len(self.wells)})?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.wells.clear()
            self.wells_tree.clear()
            self.compare_list.clear()
            self.current_well = None
            self.current_well_name = ""
            self.props_text.clear()
            self.curves_list.clear()
            self.compare_curve_combo.clear()
            
            # Deshabilitar botones
            self.remove_well_btn.setEnabled(False)
            self.plot_btn.setEnabled(False)
            self.plot_together_btn.setEnabled(False)
            self.plot_all_btn.setEnabled(False)
            self.save_plot_btn.setEnabled(False)
            
            self.update_wells_count()
            self.clear_plot()
            self.log_activity("🗃️ Todos los pozos eliminados")
    
    def run_quick_analysis(self):
        """Ejecutar análisis rápido del pozo actual."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero.")
            return
        
        self.log_activity(f"📈 Iniciando análisis rápido de {self.current_well.name}")
        
        # Por ahora, simplemente graficamos todas las curvas
        self.plot_all_curves()
        
        # Mostrar información básica
        well = self.current_well
        depth_range = well.depth_range
        
        info_text = f"""Análisis Rápido - {well.name}
        
Profundidad: {depth_range[0]:.1f} - {depth_range[1]:.1f} m
Intervalo: {depth_range[1] - depth_range[0]:.1f} m
Curvas disponibles: {len(well.curves)}

Curvas principales encontradas:
"""
        
        main_curves = ["GR", "SP", "RT", "RHOB", "NPHI", "VCL", "PHIE", "SW"]
        found_curves = [curve for curve in main_curves if curve in well.curves]
        
        if found_curves:
            info_text += "• " + ", ".join(found_curves)
        else:
            info_text += "• Curvas estándar no identificadas"
        
        QMessageBox.information(self, "Análisis Rápido", info_text)
        self.log_activity("✅ Análisis rápido completado")
    
    def export_current_well(self):
        """Exportar datos del pozo actual."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Datos",
            f"{self.current_well.name}_export.csv",
            "CSV (*.csv);;Excel (*.xlsx);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                df = self.current_well._well.df()
                
                if file_path.endswith('.xlsx'):
                    df.to_excel(file_path)
                else:
                    df.to_csv(file_path)
                
                self.log_activity(f"📤 Datos exportados: {Path(file_path).name}")
                self.status_bar.showMessage(f"Datos exportados: {Path(file_path).name}", 3000)
                
            except Exception as e:
                self.log_activity(f"❌ Error exportando: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error exportando datos:\n{str(e)}")
    
    def clear_activity_log(self):
        """Limpiar log de actividades."""
        self.activity_log.clear()
        self.log_activity("🧹 Log de actividades limpiado")
    
    def refresh_view(self):
        """Actualizar vista."""
        self.update_wells_count()
        self.update_comparison_list()
        if self.current_well:
            self.update_well_properties()
            self.update_curves_list()
        self.log_activity("🔄 Vista actualizada")
    
    def show_about(self):
        """Mostrar información sobre la aplicación."""
        about_text = """
<h2>PyPozo App 2.0</h2>
<p><b>Sistema Profesional de Análisis de Pozos</b></p>
<p>Alternativa Open Source a WellCAD</p>

<p><b>Características:</b></p>
<ul>
<li>Carga y visualización de archivos LAS</li>
<li>Análisis multi-curva interactivo</li>
<li>Graficado de curvas juntas (superpuestas)</li>
<li>Detección automática de curvas eléctricas</li>
<li>Escala logarítmica automática para resistividad</li>
<li>Visualización de unidades en etiquetas</li>
<li>Comparación de pozos</li>
<li>Exportación profesional</li>
<li>Interface moderna y intuitiva</li>
</ul>

<p><b>Autor:</b> José María García Márquez</p>
<p><b>Fecha:</b> Junio 2025</p>
<p><b>Powered by:</b> PyQt5, Matplotlib, Welly</p>
        """
        QMessageBox.about(self, "Acerca de PyPozo App", about_text)
    
    def plot_curves_together(self):
        """Graficar curvas seleccionadas juntas en la misma figura."""
        if not self.current_well:
            QMessageBox.warning(self, "Advertencia", "Seleccione un pozo primero.")
            return
        
        selected_curves = self.get_selected_curves()
        if len(selected_curves) < 2:
            QMessageBox.warning(self, "Advertencia", "Seleccione al menos 2 curvas para graficar juntas.")
            return
        
        self.log_activity(f"🔗 Graficando curvas juntas: {', '.join(selected_curves)}")
        
        try:
            # Limpiar figura anterior
            self.figure.clear()
            
            # Preguntar al usuario sobre normalización
            reply = QMessageBox.question(
                self, "Opciones de Graficado",
                "¿Desea normalizar las curvas para mejor comparación visual?\n\n"
                "Sí: Escalar todas las curvas al rango 0-1\n"
                "No: Usar valores originales (recomendado si tienen las mismas unidades)",
                QMessageBox.Yes | QMessageBox.No
            )
            
            normalize = reply == QMessageBox.Yes
            
            # Crear gráfico usando el plotter
            ax = self.figure.add_subplot(111)
            
            # Obtener datos del pozo
            df = self.current_well._well.df()
            
            # Colores para cada curva
            colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00', '#8B4513', '#00CED1', '#9932CC', '#FF1493']
            
            # Detectar si usar escala logarítmica
            has_electrical = any(self.plotter._is_electrical_curve(curve, self.current_well) for curve in selected_curves)
            
            # Obtener unidades comunes
            units_list = []
            for curve_name in selected_curves:
                units = self.current_well.get_curve_units(curve_name)
                if units:
                    units_list.append(units)
            
            # Determinar unidades para el xlabel
            if units_list:
                unique_units = list(set(units_list))
                if len(unique_units) == 1:
                    xlabel_units = unique_units[0]
                else:
                    xlabel_units = " / ".join(unique_units)
            else:
                xlabel_units = "Valores"
            
            # Graficar cada curva
            for i, curve_name in enumerate(selected_curves):
                if curve_name in df.columns:
                    curve_data = df[curve_name].dropna()
                    
                    if len(curve_data) == 0:
                        self.log_activity(f"⚠️ Curva {curve_name} no tiene datos válidos")
                        continue
                    
                    depth = curve_data.index
                    values = curve_data.values
                    
                    # Normalizar valores si se solicita
                    if normalize:
                        values_normalized = (values - values.min()) / (values.max() - values.min())
                        plot_values = values_normalized
                        curve_label = f"{curve_name} (normalizado)"
                    else:
                        plot_values = values
                        curve_label = curve_name
                    
                    color = colors[i % len(colors)]
                    ax.plot(plot_values, depth, linewidth=2, color=color, 
                           label=curve_label, alpha=0.8)
            
            # Configurar ejes
            if normalize:
                xlabel = 'Valores Normalizados (0-1)'
            else:
                xlabel = f'Valores ({xlabel_units})'
            
            ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
            ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
            ax.set_title(f'Registros Combinados - {self.current_well.name}', fontsize=14, fontweight='bold')
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best', framealpha=0.9)
            
            # Aplicar escala logarítmica si es necesario
            if has_electrical and not normalize:
                ax.set_xscale('log')
                self.log_activity("📊 Aplicando escala logarítmica al eje X")
            
            # Ajustar layout
            self.figure.tight_layout()
            
            # Actualizar canvas
            self.canvas.draw()
            
            self.log_activity(f"✅ Curvas graficadas juntas exitosamente")
            
        except Exception as e:
            self.log_activity(f"❌ Error graficando curvas juntas: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error creando gráfico:\n{str(e)}")

def main():
    """Función principal."""
    if not PYQT5_AVAILABLE:
        print("\n💡 Para instalar PyQt5:")
        print("   pip install PyQt5")
        print("\n📊 Ejecutando versión de consola como alternativa...")
        
        # Ejecutar versión de consola como fallback
        try:
            exec(open("test_visualizacion.py", "r", encoding="utf-8").read())
        except:
            print("❌ Error ejecutando versión de consola")
        return
    
    # Crear aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("PyPozo App")
    app.setOrganizationName("PyPozo")
    
    # Crear ventana principal
    window = PyPozoApp()
    window.show()
    
    # Log inicial
    window.log_activity("🚀 PyPozo App iniciada")
    window.log_activity("📂 Use 'Archivo > Abrir Pozo' para cargar archivos LAS")
    
    # Ejecutar aplicación
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
