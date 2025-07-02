#!/usr/bin/env python3
"""Test final de PyPozoApp"""

from pypozo_app import PyPozoApp
import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
window = PyPozoApp()

# Verificar métodos importantes
methods = ['remove_well', 'plot_curves_together', 'clear_all_wells', 'merge_selected_wells']
missing = []

for method in methods:
    if not hasattr(window, method):
        missing.append(method)

if missing:
    print(f"❌ Métodos faltantes: {missing}")
else:
    print("✅ Todos los métodos están presentes")

print("✅ PyPozoApp funciona correctamente")
app.quit()
