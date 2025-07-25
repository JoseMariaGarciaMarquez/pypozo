"""
PozoChat GUI - Ventana de asistente conversacional con logo y chat
"""

import sys
import os
import threading
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QScrollArea
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

LOGO_PATH = os.path.join(os.path.dirname(__file__), '../images/logo_completo.png')

class PozoChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PozoChat - Asistente de Procesamiento de Pozos")
        self.setGeometry(300, 200, 600, 700)
        self.init_ui()
        self.chat_history = []
        self.hf_token = os.environ.get("HF_TOKEN", None)
        self.hf_model = "mistralai/Mistral-7B-Instruct-v0.2"
        self.show_welcome()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        if os.path.exists(LOGO_PATH):
            pixmap = QPixmap(LOGO_PATH)
            logo_label.setPixmap(pixmap.scaledToWidth(320, Qt.SmoothTransformation))
        else:
            logo_label.setText("PozoChat")
            logo_label.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(logo_label)

        # Chat area (scrollable)
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("Consolas", 11))
        self.chat_area.setMinimumHeight(400)
        self.chat_area.setStyleSheet("background-color: #f8f9fa; font-family: 'Courier New'; font-size: 11px; border: 1px solid #dee2e6; border-radius: 6px; color: #495057;")
        layout.addWidget(self.chat_area)

        # Input area
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Escribe tu pregunta o comando...")
        self.input_box.returnPressed.connect(self.handle_user_input)
        input_layout.addWidget(self.input_box)
        self.send_btn = QPushButton("Enviar")
        self.send_btn.clicked.connect(self.handle_user_input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def show_welcome(self):
        welcome = "<b>Bienvenido a PozoChat!</b><br>" \
                  "Soy tu asistente para procesar datos de pozos.<br>" \
                  "Puedes preguntarme sobre análisis, intervalos, gráficos y cálculos petrofísicos." \
                  "<br><i>¿Qué deseas analizar hoy?</i>"
        self.append_chat("PozoChat", welcome)

    def append_chat(self, sender, message):
        self.chat_area.append(f"<b>{sender}:</b> {message}")

    def handle_user_input(self):
        user_text = self.input_box.text().strip()
        if not user_text:
            return
        self.append_chat("Tú", user_text)
        self.input_box.clear()
        if self.hf_token:
            self.append_chat("PozoChat", "<i>Consultando modelo IA en Hugging Face...</i>")
            threading.Thread(target=self.query_huggingface, args=(user_text,)).start()
        else:
            response = self.generate_response(user_text)
            self.append_chat("PozoChat", response)

    def query_huggingface(self, user_text):
        api_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        prompt = f"Eres un asistente experto en petrofísica y análisis de pozos. Responde en español de forma clara y profesional.\nUsuario: {user_text}\nAsistente:"
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 256, "temperature": 0.7}}
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Hugging Face puede devolver una lista de dicts con 'generated_text'
                if isinstance(data, list) and 'generated_text' in data[0]:
                    answer = data[0]['generated_text'].split("Asistente:")[-1].strip()
                elif isinstance(data, dict) and 'error' in data:
                    answer = f"[Error Hugging Face] {data['error']}"
                else:
                    answer = str(data)
            else:
                answer = f"[Error {response.status_code}] {response.text}"
        except Exception as e:
            answer = f"[Error de conexión a Hugging Face: {e}]"
        # Mostrar respuesta en el hilo principal
        from PyQt5.QtWidgets import QApplication
        def show():
            self.append_chat("PozoChat", answer)
        QApplication.instance().postEvent(self, type('Event', (), {'accept': show})())

    def generate_response(self, user_text):
        # Respuestas simuladas si no hay token
        # Restaurar lógica de IA: si hay token/configuración, usar modelo Hugging Face
        try:
            return self.query_huggingface(user_text)
        except Exception:
            # Si falla, mostrar mensaje local
            return "Procesando tu solicitud... (Funcionalidad avanzada próximamente)"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PozoChatWindow()
    window.show()
    sys.exit(app.exec_())
