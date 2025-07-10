"""
Dialog UI for Neural Completion (PyQt5).
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QComboBox, QHBoxLayout, QProgressBar
from PyQt5.QtCore import Qt

class NeuralCompletionDialog(QDialog):
    def __init__(self, wells, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✨ Premium Neural Curve Completion ✨")
        self.setMinimumSize(650, 480)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #232526, stop:1 #414345);
                border-radius: 16px;
            }
            QLabel, QGroupBox {
                color: #f3f3f3;
                font-size: 15px;
            }
            QGroupBox {
                background: #232526;
                border: 1.5px solid #43cea2;
                border-radius: 10px;
                margin-top: 8px;
                font-weight: bold;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                background: #232526;
                color: #f3f3f3;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #444;
            }
            QComboBox QAbstractItemView {
                background: #232526;
                color: #f3f3f3;
                selection-background-color: #2575fc;
                selection-color: #fff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6a11cb, stop:1 #2575fc);
                color: #fff;
                border-radius: 10px;
                padding: 8px 18px;
                font-weight: bold;
                font-size: 15px;
                border: none;
            }
            QPushButton:disabled {
                background: #444;
                color: #aaa;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 8px;
                text-align: center;
                background: #232526;
                color: #f3f3f3;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #43cea2, stop:1 #185a9d);
                border-radius: 8px;
            }
        """)
        self.wells = wells
        self.selected_well = None
        self.selected_curve = None
        self._setup_ui()

    def _setup_ui(self):
        from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QGroupBox, QFrame
        layout = QVBoxLayout(self)

        # Header with icon and title
        header = QHBoxLayout()
        icon_label = QLabel("<span style='font-size:32px;'>🤖</span>")
        header.addWidget(icon_label)
        title = QLabel("<b style='font-size:22px;'>Completado Neuronal Premium</b>")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Well/curve selection group
        select_group = QGroupBox("Selección de pozo y curva")
        select_group.setStyleSheet("QGroupBox { border: 1.5px solid #43cea2; border-radius: 10px; margin-top: 8px; font-weight: bold; } QGroupBox:title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        select_layout = QVBoxLayout()
        select_layout.addWidget(QLabel("Selecciona el pozo y la curva a completar:"))
        self.well_combo = QComboBox()
        self.well_combo.addItems(list(self.wells.keys()))
        self.well_combo.currentTextChanged.connect(self._on_well_changed)
        select_layout.addWidget(self.well_combo)
        self.curve_combo = QComboBox()
        select_layout.addWidget(self.curve_combo)
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)

        # Neural network parameters group
        param_group = QGroupBox("Parámetros de la Red Neuronal")
        param_group.setStyleSheet("QGroupBox { border: 1.5px solid #2575fc; border-radius: 10px; margin-top: 8px; font-weight: bold; } QGroupBox:title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Épocas:"))
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setMinimum(10)
        self.epochs_spin.setMaximum(1000)
        self.epochs_spin.setValue(100)
        param_layout.addWidget(self.epochs_spin)
        param_layout.addWidget(QLabel("Capas ocultas:"))
        self.hidden_spin = QSpinBox()
        self.hidden_spin.setMinimum(1)
        self.hidden_spin.setMaximum(5)
        self.hidden_spin.setValue(2)
        param_layout.addWidget(self.hidden_spin)
        param_layout.addWidget(QLabel("Neur. por capa:"))
        self.neurons_spin = QSpinBox()
        self.neurons_spin.setMinimum(4)
        self.neurons_spin.setMaximum(256)
        self.neurons_spin.setValue(32)
        param_layout.addWidget(self.neurons_spin)
        param_layout.addWidget(QLabel("Learning rate:"))
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setDecimals(4)
        self.lr_spin.setSingleStep(0.0001)
        self.lr_spin.setMinimum(0.0001)
        self.lr_spin.setMaximum(1.0)
        self.lr_spin.setValue(0.001)
        param_layout.addWidget(self.lr_spin)
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # Status and progress group
        status_group = QGroupBox("Estado y Progreso")
        status_group.setStyleSheet("QGroupBox { border: 1.5px solid #43cea2; border-radius: 10px; margin-top: 8px; font-weight: bold; } QGroupBox:title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        status_layout = QVBoxLayout()
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(90)
        status_layout.addWidget(self.status_text)
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        status_layout.addWidget(self.progress)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Buttons
        btns = QHBoxLayout()
        self.run_btn = QPushButton("✨ Completar con IA Premium ✨")
        self.run_btn.clicked.connect(self._run_completion)
        btns.addWidget(self.run_btn)
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        btns.addWidget(self.close_btn)
        layout.addLayout(btns)

        # Initialize combos after all widgets are created
        self._on_well_changed(self.well_combo.currentText())

    def _on_well_changed(self, well_name):
        self.selected_well = self.wells[well_name]
        self.curve_combo.clear()
        self.run_btn.setEnabled(True)
        if hasattr(self.selected_well, 'data'):
            columns = list(self.selected_well.data.columns)
            self.curve_combo.addItems(columns)
            # Check for valid input curves for the first curve
            if columns:
                self._check_valid_input_curves(columns[0])
        self.curve_combo.currentTextChanged.connect(self._check_valid_input_curves)

    def _check_valid_input_curves(self, curve_name):
        # Solo permitir el completado si hay curvas de entrada válidas (existen y tienen datos)
        if not hasattr(self.selected_well, 'data'):
            self.status_text.append("❌ No hay datos disponibles para este pozo.")
            self.run_btn.setEnabled(False)
            self.valid_input_curves = []
            return
        df = self.selected_well.data
        input_curves = [col for col in df.columns if col != curve_name]
        # Solo curvas con datos válidos
        valid_inputs = [col for col in input_curves if df[col].notna().sum() > 0]
        self.valid_input_curves = valid_inputs
        if not valid_inputs:
            self.status_text.append("❌ No hay curvas de entrada válidas para completar la curva seleccionada. Agregue más curvas o seleccione otra curva.")
            self.run_btn.setEnabled(False)
        else:
            self.run_btn.setEnabled(True)

    def _run_completion(self):
        from patreon_dlc.completion.neural_completion import NeuralCompletion
        from PyQt5.QtWidgets import QMessageBox
        well_name = self.well_combo.currentText()
        curve_name = self.curve_combo.currentText()
        self.status_text.append(f"Iniciando completado neuronal para curva '{curve_name}' en pozo '{well_name}'...")
        self.progress.setValue(10)
        well = self.wells[well_name]
        # Get neural net parameters from UI
        epochs = self.epochs_spin.value()
        n_layers = self.hidden_spin.value()
        n_neurons = self.neurons_spin.value()
        learning_rate = self.lr_spin.value()
        # Usar solo curvas de entrada válidas
        input_curves = getattr(self, 'valid_input_curves', None)
        try:
            nc = NeuralCompletion(well)
            # Analizar relaciones solo con curvas válidas
            stats = nc.analyze_curve_relations(curve_name, input_curves=input_curves)
            self.status_text.append("\nCorrelaciones con otras curvas:")
            for k, v in stats['correlations'].items():
                self.status_text.append(f"  {k}: {v:.3f}")
            # Intentar completar (primero sin forzar)
            self.status_text.append("\nComprobando cantidad de datos para entrenamiento...")
            self.progress.setValue(30)
            # Pass neural net params to complete()
            result = nc.complete(
                curve_name,
                model_type='mlp',
                epochs=epochs,
                force=False,
                input_curves=input_curves,
                verbose=False,
                hidden_layer_sizes=tuple([n_neurons]*n_layers),
                learning_rate_init=learning_rate
            )
            if result.get('few_data', False):
                n_train = result.get('n_train', 0)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Pocos datos para entrenamiento")
                msg.setText(f"Solo hay {n_train} datos válidos para entrenar el modelo.\nLa calidad del completado puede ser baja o poco confiable.\n¿Desea continuar de todos modos?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                user_choice = msg.exec_()
                if user_choice == QMessageBox.No:
                    self.status_text.append("❌ Operación cancelada por el usuario (pocos datos para entrenar).")
                    self.progress.setValue(0)
                    return
                # Si el usuario acepta, forzar el completado
                self.status_text.append("⚠️ Continuando con pocos datos (baja calidad esperada)...")
                self.progress.setValue(40)
                result = nc.complete(
                    curve_name,
                    model_type='mlp',
                    epochs=epochs,
                    force=True,
                    input_curves=None,
                    verbose=False,
                    hidden_layer_sizes=tuple([n_neurons]*n_layers),
                    learning_rate_init=learning_rate
                )
            else:
                self.status_text.append("\nCompletando con red neuronal...")
                self.progress.setValue(40)
            self.progress.setValue(90)
            if result['completed'] > 0:
                self.status_text.append(f"✅ Completado exitoso: {result['completed']} valores rellenados.")
                self.status_text.append(f"R² entrenamiento: {result['train_r2']:.3f}  |  RMSE: {result['train_rmse']:.3f}")
            else:
                self.status_text.append("⚠️ No se encontraron valores faltantes para completar.")
            self.progress.setValue(100)
        except TypeError as te:
            # If complete() doesn't accept new params, fallback to old signature
            self.status_text.append("⚠️ El backend no soporta ajuste de parámetros avanzados. Usando configuración por defecto.")
            try:
                result = nc.complete(curve_name, force=False)
                if result.get('few_data', False):
                    n_train = result.get('n_train', 0)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Pocos datos para entrenamiento")
                    msg.setText(f"Solo hay {n_train} datos válidos para entrenar el modelo.\nLa calidad del completado puede ser baja o poco confiable.\n¿Desea continuar de todos modos?")
                    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    user_choice = msg.exec_()
                    if user_choice == QMessageBox.No:
                        self.status_text.append("❌ Operación cancelada por el usuario (pocos datos para entrenar).")
                        self.progress.setValue(0)
                        return
                    self.status_text.append("⚠️ Continuando con pocos datos (baja calidad esperada)...")
                    self.progress.setValue(40)
                    result = nc.complete(curve_name, force=True)
                else:
                    self.status_text.append("\nCompletando con red neuronal...")
                    self.progress.setValue(40)
                self.progress.setValue(90)
                if result['completed'] > 0:
                    self.status_text.append(f"✅ Completado exitoso: {result['completed']} valores rellenados.")
                    self.status_text.append(f"R² entrenamiento: {result['train_r2']:.3f}  |  RMSE: {result['train_rmse']:.3f}")
                else:
                    self.status_text.append("⚠️ No se encontraron valores faltantes para completar.")
                self.progress.setValue(100)
            except Exception as e:
                self.status_text.append(f"❌ Error: {str(e)}")
                self.progress.setValue(0)
        except Exception as e:
            self.status_text.append(f"❌ Error: {str(e)}")
            self.progress.setValue(0)
