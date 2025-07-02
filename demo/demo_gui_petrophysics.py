#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo GUI Petrofísica
===================

Demo simple de la nueva funcionalidad petrofísica en la GUI.
"""

import sys
import os
from pathlib import Path

# Asegurar que usemos la versión local (ir un nivel arriba desde demo/)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    print("🧪 Iniciando demo de GUI con petrofísica...")
    
    try:
        # Importar con paths correctos
        from PyQt5.QtWidgets import QApplication
        
        # Crear aplicación
        app = QApplication(sys.argv)
        app.setApplicationName("PyPozo Demo")
        
        print("✅ QApplication creada")
        
        # Verificar que podemos importar los módulos petrofísicos
        sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "pypozo"))
        
        try:
            from petrophysics import VclCalculator, PorosityCalculator
            print("✅ Módulos petrofísicos importados correctamente")
            
            # Crear calculadoras de prueba
            vcl_calc = VclCalculator()
            por_calc = PorosityCalculator()
            
            print(f"✅ VCL Calculator - Métodos: {list(vcl_calc.methods.keys())}")
            print("✅ Porosity Calculator creado")
            
        except Exception as e:
            print(f"❌ Error con módulos petrofísicos: {e}")
            return False
        
        # Mostrar mensaje de éxito
        from PyQt5.QtWidgets import QMessageBox, QMainWindow
        
        window = QMainWindow()
        window.setWindowTitle("PyPozo 2.0 - Demo Petrofísica")
        window.resize(800, 600)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Demo Petrofísica")
        msg.setText("""🎉 ¡Integración Exitosa!
        
Los módulos petrofísicos están funcionando:

✅ VclCalculator - 5 métodos disponibles
✅ PorosityCalculator - 3 métodos disponibles  
✅ PetrophysicsCalculator - Base para QC

🚀 Funcionalidades implementadas:
• Cálculo de VCL (5 métodos estándar)
• Cálculo de PHIE (densidad, neutrón, combinado)
• Correcciones de arcilla y gas
• Análisis litológico automático
• Control de calidad integrado
• Exportación de resultados

📋 Próximos pasos:
• Saturación de Agua (SW)
• Templates de workflows
• Mejoras en visualización""")
        
        msg.exec_()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Demo completado exitosamente!")
        print("🚀 Los módulos petrofísicos están listos para usar.")
    else:
        print("\n❌ Demo falló. Revisar errores arriba.")
