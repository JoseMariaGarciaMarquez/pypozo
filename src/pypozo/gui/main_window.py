"""
PyPozo 2.0 - Ventana Principal de la GUI
========================================

Interfaz gráfica profesional para análisis de pozos, construida con PyQt5.
Esta será nuestra alternativa a WellCAD con capacidades avanzadas de:

- Carga y visualización de archivos LAS
- Análisis petrofísico interactivo
- Comparación de pozos
- Exportación profesional
- Workflows automatizados

Autor: José María García Márquez
Fecha: Junio 2025
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QTextEdit,
        QMenuBar, QToolBar, QStatusBar, QFileDialog, QMessageBox,
        QPushButton, QLabel, QComboBox, QCheckBox, QSpinBox, QGroupBox,
        QListWidget, QListWidgetItem, QProgressBar, QFrame
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QIcon, QFont, QPixmap
    
    # Para integrar matplotlib con PyQt5
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

if PYQT5_AVAILABLE:
    from ..core.well import WellManager
    from ..core.project import ProjectManager
    from ..visualization.plotter import WellPlotter
    from ..workflows.standard import StandardWorkflow

logger = logging.getLogger(__name__)

class PyPozoMainWindow(QMainWindow):
    """
    Ventana principal de PyPozo 2.0 - Alternativa profesional a WellCAD.
    
    Características:
    - Interface moderna y profesional
    - Árbol de pozos y proyectos
    - Visualización interactiva de registros
    - Panel de propiedades y análisis
    - Barra de herramientas completa
    - Sistema de plugins y workflows
    """
    
    def __init__(self):
        super().__init__()
        
        self.wells: Dict[str, WellManager] = {}
        self.current_well: Optional[WellManager] = None
        self.project_manager = ProjectManager()
        self.plotter = WellPlotter()
        
        self.init_ui()
        self.setup_logging()
        
        logger.info("🚀 PyPozo 2.0 GUI iniciada")
    
    def init_ui(self):
        """Inicializar la interfaz de usuario."""
        self.setWindowTitle("PyPozo 2.0 - Análisis Profesional de Pozos")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (horizontal)
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Panel izquierdo - Navegación y propiedades
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Panel central - Visualización
        center_panel = self.create_center_panel()
        main_splitter.addWidget(center_panel)
        
        # Panel derecho - Herramientas y análisis
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        main_splitter.setSizes([300, 800, 300])
        
        # Crear menús y barras de herramientas
        self.create_menus()
        self.create_toolbars()
        self.create_status_bar()
        
        # Aplicar estilo profesional
        self.apply_professional_style()
    
    def create_left_panel(self) -> QWidget:
        """Crear panel izquierdo con navegación de pozos."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Título del panel
        title = QLabel("📁 Explorador de Pozos")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Árbol de pozos
        self.wells_tree = QTreeWidget()
        self.wells_tree.setHeaderLabel("Pozos y Proyectos")
        self.wells_tree.itemClicked.connect(self.on_well_selected)
        layout.addWidget(self.wells_tree)
        
        # Botones de acción
        buttons_layout = QVBoxLayout()
        
        self.load_well_btn = QPushButton("📂 Cargar Pozo")
        self.load_well_btn.clicked.connect(self.load_well)
        buttons_layout.addWidget(self.load_well_btn)
        
        self.load_project_btn = QPushButton("📁 Cargar Proyecto")
        self.load_project_btn.clicked.connect(self.load_project)
        buttons_layout.addWidget(self.load_project_btn)
        
        self.remove_well_btn = QPushButton("🗑️ Remover")
        self.remove_well_btn.clicked.connect(self.remove_well)
        buttons_layout.addWidget(self.remove_well_btn)
        
        layout.addLayout(buttons_layout)
        
        # Propiedades del pozo seleccionado
        props_group = QGroupBox("📊 Propiedades")
        props_layout = QVBoxLayout(props_group)
        
        self.props_text = QTextEdit()
        self.props_text.setMaximumHeight(200)
        self.props_text.setReadOnly(True)
        props_layout.addWidget(self.props_text)
        
        layout.addWidget(props_group)
        
        return panel
    
    def create_center_panel(self) -> QWidget:
        """Crear panel central de visualización."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Título y controles
        header_layout = QHBoxLayout()
        
        title = QLabel("📈 Visualización de Registros")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title)
        
        # Controles de visualización
        self.plot_btn = QPushButton("🎨 Graficar")
        self.plot_btn.clicked.connect(self.plot_selected_curves)
        header_layout.addWidget(self.plot_btn)
        
        self.save_plot_btn = QPushButton("💾 Guardar")
        self.save_plot_btn.clicked.connect(self.save_current_plot)
        header_layout.addWidget(self.save_plot_btn)
        
        layout.addLayout(header_layout)
        
        # Canvas de matplotlib
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Crear panel derecho con herramientas."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Título
        title = QLabel("🔧 Herramientas")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Tabs para diferentes herramientas
        tabs = QTabWidget()
        
        # Tab 1: Selección de curvas
        curves_tab = self.create_curves_tab()
        tabs.addTab(curves_tab, "📊 Curvas")
        
        # Tab 2: Análisis petrofísico
        analysis_tab = self.create_analysis_tab()
        tabs.addTab(analysis_tab, "🔬 Análisis")
        
        # Tab 3: Comparación
        comparison_tab = self.create_comparison_tab()
        tabs.addTab(comparison_tab, "⚖️ Comparar")
        
        layout.addWidget(tabs)
        
        return panel
    
    def create_curves_tab(self) -> QWidget:
        """Tab para selección de curvas."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de curvas disponibles
        curves_label = QLabel("Curvas Disponibles:")
        layout.addWidget(curves_label)
        
        self.curves_list = QListWidget()
        self.curves_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.curves_list)
        
        # Botones de selección rápida
        quick_buttons = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Todo")
        self.select_all_btn.clicked.connect(self.select_all_curves)
        quick_buttons.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("❌ Nada")
        self.select_none_btn.clicked.connect(self.select_no_curves)
        quick_buttons.addWidget(self.select_none_btn)
        
        self.select_standard_btn = QPushButton("📊 Estándar")
        self.select_standard_btn.clicked.connect(self.select_standard_curves)
        quick_buttons.addWidget(self.select_standard_btn)
        
        layout.addLayout(quick_buttons)
        
        return tab
    
    def create_analysis_tab(self) -> QWidget:
        """Tab para análisis petrofísico."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Análisis automático
        auto_group = QGroupBox("🤖 Análisis Automático")
        auto_layout = QVBoxLayout(auto_group)
        
        self.calc_vsh_btn = QPushButton("📊 Calcular VSH")
        self.calc_vsh_btn.clicked.connect(self.calculate_vsh)
        auto_layout.addWidget(self.calc_vsh_btn)
        
        self.calc_porosity_btn = QPushButton("🕳️ Calcular Porosidad")
        self.calc_porosity_btn.clicked.connect(self.calculate_porosity)
        auto_layout.addWidget(self.calc_porosity_btn)
        
        self.calc_saturation_btn = QPushButton("💧 Calcular Saturación")
        self.calc_saturation_btn.clicked.connect(self.calculate_saturation)
        auto_layout.addWidget(self.calc_saturation_btn)
        
        layout.addWidget(auto_group)
        
        # Parámetros
        params_group = QGroupBox("⚙️ Parámetros")
        params_layout = QVBoxLayout(params_group)
        
        # VSH cutoff
        vsh_layout = QHBoxLayout()
        vsh_layout.addWidget(QLabel("VSH Cutoff:"))
        self.vsh_cutoff = QSpinBox()
        self.vsh_cutoff.setRange(0, 100)
        self.vsh_cutoff.setValue(50)
        self.vsh_cutoff.setSuffix(" API")
        vsh_layout.addWidget(self.vsh_cutoff)
        params_layout.addLayout(vsh_layout)
        
        layout.addWidget(params_group)
        
        return tab
    
    def create_comparison_tab(self) -> QWidget:
        """Tab para comparación de pozos."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        compare_label = QLabel("Comparar Pozos:")
        layout.addWidget(compare_label)
        
        self.compare_list = QListWidget()
        self.compare_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.compare_list)
        
        self.compare_btn = QPushButton("⚖️ Comparar Seleccionados")
        self.compare_btn.clicked.connect(self.compare_wells)
        layout.addWidget(self.compare_btn)
        
        return tab
    
    def create_menus(self):
        """Crear menús de la aplicación."""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu('📁 Archivo')
        file_menu.addAction('📂 Abrir Pozo...', self.load_well)
        file_menu.addAction('📁 Abrir Proyecto...', self.load_project)
        file_menu.addSeparator()
        file_menu.addAction('💾 Guardar Proyecto...', self.save_project)
        file_menu.addAction('📤 Exportar...', self.export_data)
        file_menu.addSeparator()
        file_menu.addAction('❌ Salir', self.close)
        
        # Menú Ver
        view_menu = menubar.addMenu('👁️ Ver')
        view_menu.addAction('🔄 Actualizar', self.refresh_view)
        view_menu.addAction('🔍 Zoom Fit', self.zoom_fit)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu('🔧 Herramientas')
        tools_menu.addAction('🤖 Workflow Automático', self.run_auto_workflow)
        tools_menu.addAction('📊 Análisis Completo', self.run_full_analysis)
        
        # Menú Ayuda
        help_menu = menubar.addMenu('❓ Ayuda')
        help_menu.addAction('📖 Acerca de PyPozo', self.show_about)
    
    def create_toolbars(self):
        """Crear barras de herramientas."""
        # Barra principal
        main_toolbar = self.addToolBar('Principal')
        main_toolbar.addAction('📂 Abrir', self.load_well)
        main_toolbar.addAction('💾 Guardar', self.save_project)
        main_toolbar.addSeparator()
        main_toolbar.addAction('🎨 Graficar', self.plot_selected_curves)
        main_toolbar.addAction('🔄 Actualizar', self.refresh_view)
    
    def create_status_bar(self):
        """Crear barra de estado."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("✅ PyPozo 2.0 listo para usar")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def apply_professional_style(self):
        """Aplicar estilo profesional a la interfaz."""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QTreeWidget, QListWidget {
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: white;
        }
        QTabWidget::pane {
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #4CAF50;
            color: white;
        }
        """
        self.setStyleSheet(style)
    
    def setup_logging(self):
        """Configurar logging para la GUI."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Métodos de funcionalidad (se implementarán a continuación)
    def load_well(self):
        """Cargar un archivo de pozo."""
        pass
    
    def load_project(self):
        """Cargar un proyecto."""
        pass
    
    def on_well_selected(self, item):
        """Manejar selección de pozo."""
        pass
    
    def plot_selected_curves(self):
        """Graficar curvas seleccionadas."""
        pass
    
    def save_current_plot(self):
        """Guardar el gráfico actual."""
        pass
    
    def select_all_curves(self):
        """Seleccionar todas las curvas."""
        pass
    
    def select_no_curves(self):
        """Deseleccionar todas las curvas."""
        pass
    
    def select_standard_curves(self):
        """Seleccionar curvas estándar."""
        pass
    
    def calculate_vsh(self):
        """Calcular VSH."""
        pass
    
    def calculate_porosity(self):
        """Calcular porosidad."""
        pass
    
    def calculate_saturation(self):
        """Calcular saturación."""
        pass
    
    def compare_wells(self):
        """Comparar pozos seleccionados."""
        pass
    
    def remove_well(self):
        """Remover pozo."""
        pass
    
    def save_project(self):
        """Guardar proyecto."""
        pass
    
    def export_data(self):
        """Exportar datos."""
        pass
    
    def refresh_view(self):
        """Actualizar vista."""
        pass
    
    def zoom_fit(self):
        """Ajustar zoom."""
        pass
    
    def run_auto_workflow(self):
        """Ejecutar workflow automático."""
        pass
    
    def run_full_analysis(self):
        """Ejecutar análisis completo."""
        pass
    
    def show_about(self):
        """Mostrar información sobre PyPozo."""
        QMessageBox.about(self, "Acerca de PyPozo 2.0", 
                         "PyPozo 2.0\n\n"
                         "Sistema Profesional de Análisis de Pozos\n"
                         "Alternativa Open Source a WellCAD\n\n"
                         "Autor: José María García Márquez\n"
                         "Junio 2025")

def main():
    """Función principal para ejecutar la GUI."""
    if not PYQT5_AVAILABLE:
        print("❌ PyQt5 no está disponible. Instale PyQt5 para usar la GUI.")
        return
    
    app = QApplication(sys.argv)
    app.setApplicationName("PyPozo 2.0")
    
    window = PyPozoMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
