"""
Diálogo de Bienvenida para PyPozo con promoción Buy Me a Coffee
============================================================

Ventana de bienvenida que aparece al iniciar PyPozo con botones
para apoyar el proyecto a través de Buy Me a Coffee.

Autor: José María García Márquez
Fecha: Julio 2025
"""

import webbrowser
from pathlib import Path
try:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
        QFrame, QSpacerItem, QSizePolicy, QTextEdit, QGroupBox
    )
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QPixmap, QPalette, QIcon
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

class WelcomeDialog(QDialog):
    """Diálogo de bienvenida con promoción de Buy Me a Coffee."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("¡Bienvenido a PyPozo! 🚀")
        self.setModal(True)
        self.setFixedSize(600, 550)
        
        # Configurar ícono
        try:
            icon_path = Path(__file__).parent / "images" / "icono.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except:
            pass
            
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header con logo y título
        header_frame = self.create_header()
        layout.addWidget(header_frame)
        
        # Mensaje de bienvenida
        welcome_group = self.create_welcome_message()
        layout.addWidget(welcome_group)
        
        # Sección de apoyo
        support_group = self.create_support_section()
        layout.addWidget(support_group)
        
        # Botones de acción
        buttons_frame = self.create_action_buttons()
        layout.addWidget(buttons_frame)
        
        # Botón para continuar
        continue_button = QPushButton("🚀 ¡Empezar con PyPozo!")
        continue_button.setObjectName("continueButton")
        continue_button.clicked.connect(self.accept)
        layout.addWidget(continue_button)
        
    def create_header(self):
        """Crear el header con logo y título."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignCenter)
        
        # Título principal
        title = QLabel("🚀 ¡Bienvenido a PyPozo!")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Análisis Geofísico Profesional Open Source")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        return frame
        
    def create_welcome_message(self):
        """Crear el mensaje de bienvenida."""
        group = QGroupBox("🎉 ¡Gracias por usar PyPozo!")
        layout = QVBoxLayout(group)
        
        message = QTextEdit()
        message.setMaximumHeight(100)
        message.setReadOnly(True)
        message.setHtml("""
        <div style='font-family: Arial; font-size: 12px; line-height: 1.5;'>
        <b>PyPozo</b> es una herramienta profesional <b>100% gratuita</b> para análisis geofísico de pozos.
        <br><br>
        🌟 Una alternativa open source a software comercial como WellCAD, desarrollada con amor para la comunidad geofísica.
        </div>
        """)
        layout.addWidget(message)
        
        return group
        
    def create_support_section(self):
        """Crear la sección de apoyo al proyecto."""
        group = QGroupBox("💖 ¿Te gusta PyPozo? ¡Apóyanos!")
        layout = QVBoxLayout(group)
        
        message = QTextEdit()
        message.setMaximumHeight(80)
        message.setReadOnly(True)
        message.setHtml("""
        <div style='font-family: Arial; font-size: 11px; line-height: 1.4;'>
        Tu apoyo nos ayuda a <b>mantener PyPozo gratuito</b> y desarrollar nuevas funcionalidades.
        <br>
        ☕ <b>¡Invítanos un café!</b> Cada contribución impulsa la innovación en geofísica.
        </div>
        """)
        layout.addWidget(message)
        
        return group
        
    def create_action_buttons(self):
        """Crear los botones de acción."""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setSpacing(10)
        
        # Botón Buy Me a Coffee
        coffee_button = QPushButton("☕ Buy me a Coffee")
        coffee_button.setObjectName("coffeeButton")
        coffee_button.clicked.connect(self.open_buy_me_coffee)
        layout.addWidget(coffee_button)
        
        # Botón GitHub
        github_button = QPushButton("⭐ Ver en GitHub")
        github_button.setObjectName("githubButton")
        github_button.clicked.connect(self.open_github)
        layout.addWidget(github_button)
        
        # Botón documentación
        docs_button = QPushButton("📚 Documentación")
        docs_button.setObjectName("docsButton")
        docs_button.clicked.connect(self.open_docs)
        layout.addWidget(docs_button)
        
        return frame
        
    def setup_styles(self):
        """Configurar estilos del diálogo."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
            }
            
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
            
            QLabel#subtitleLabel {
                font-size: 14px;
                color: #6c757d;
                padding-bottom: 10px;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #f8f9fa;
            }
            
            QPushButton#coffeeButton {
                background-color: #ff813f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            
            QPushButton#coffeeButton:hover {
                background-color: #e6732c;
            }
            
            QPushButton#githubButton {
                background-color: #24292e;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            
            QPushButton#githubButton:hover {
                background-color: #1b1f23;
            }
            
            QPushButton#docsButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            
            QPushButton#docsButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton#continueButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            
            QPushButton#continueButton:hover {
                background-color: #218838;
            }
            
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
                selection-background-color: #007bff;
            }
        """)
        
    def open_buy_me_coffee(self):
        """Abrir Buy Me a Coffee en el navegador."""
        try:
            webbrowser.open("https://buymeacoffee.com/ingjoma")
            print("🌐 Abriendo Buy Me a Coffee...")
        except Exception as e:
            print(f"❌ Error abriendo Buy Me a Coffee: {e}")
            
    def open_github(self):
        """Abrir repositorio de GitHub en el navegador."""
        try:
            webbrowser.open("https://github.com/JoseMariaGarciaMarquez/pypozo")
            print("🌐 Abriendo GitHub...")
        except Exception as e:
            print(f"❌ Error abriendo GitHub: {e}")
            
    def open_docs(self):
        """Abrir documentación."""
        try:
            # Intentar abrir documentación local o web
            docs_path = Path(__file__).parent / "docs" / "README.md"
            if docs_path.exists():
                webbrowser.open(f"file:///{docs_path}")
            else:
                # Fallback a GitHub docs
                webbrowser.open("https://github.com/JoseMariaGarciaMarquez/pypozo/blob/main/docs/README.md")
            print("🌐 Abriendo documentación...")
        except Exception as e:
            print(f"❌ Error abriendo documentación: {e}")

def show_welcome_dialog(parent=None):
    """Mostrar el diálogo de bienvenida."""
    if not PYQT5_AVAILABLE:
        print("⚠️ PyQt5 no disponible para mostrar diálogo de bienvenida")
        return True
        
    dialog = WelcomeDialog(parent)
    result = dialog.exec_()
    return result == QDialog.Accepted

if __name__ == "__main__":
    # Test del diálogo
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    show_welcome_dialog()
    sys.exit(app.exec_())
