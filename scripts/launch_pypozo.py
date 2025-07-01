#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPozo 2.0 - Script de Lanzamiento
==================================

Script principal para lanzar la aplicación PyPozo.
Maneja automáticamente la configuración del path y las dependencias.

Uso:
    python launch_pypozo.py

Autor: José María García Márquez
Fecha: Junio 2025
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Configurar el entorno de ejecución."""
    # Obtener directorio del proyecto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Agregar src al path
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Configurar variables de entorno para mejor compatibilidad
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    return project_root

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import QTimer
    
    # Importar la aplicación principal
    from pypozo_app import PyPozoApp
    
    def main():
        """Función principal mejorada."""
        print("🚀 Iniciando PyPozo App...")
        
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        app.setApplicationName("PyPozo Professional")
        app.setOrganizationName("PyPozo")
        
        # Crear ventana principal
        window = PyPozoApp()
        window.show()
        
        # Log inicial
        window.log_activity("🚀 PyPozo App iniciada")
        window.log_activity("📂 Archivos de ejemplo disponibles en carpeta 'data/'")
        
        # Función para cargar datos de ejemplo después de que la GUI esté lista
        def load_example_data():
            """Cargar datos de ejemplo automáticamente."""
            example_files = [
                "data/70449_abedul1_gn_1850_800_05mz79p.las",
                "data/ABEDUL1_REPROCESADO.las",
                "data/PALO BLANCO 791_PROCESADO.las"
            ]
            
            available_files = [f for f in example_files if Path(f).exists()]
            
            if available_files:
                window.log_activity(f"📊 Encontrados {len(available_files)} archivos de ejemplo")
                
                # Preguntar si cargar automáticamente
                reply = QMessageBox.question(
                    window,
                    "Datos de Ejemplo",
                    f"¿Desea cargar automáticamente {len(available_files)} pozos de ejemplo?\\n\\n" +
                    "\\n".join([Path(f).name for f in available_files]),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    for file_path in available_files:
                        window.load_well_from_path(file_path)
                        window.log_activity(f"📥 Cargando: {Path(file_path).name}")
                    
                    window.log_activity("✅ Pozos de ejemplo cargados - ¡Explore las funcionalidades!")
                    window.status_bar.showMessage("Pozos de ejemplo cargados", 5000)
            else:
                window.log_activity("⚠️ No se encontraron archivos de ejemplo en 'data/'")
        
        # Cargar datos después de 2 segundos
        QTimer.singleShot(2000, load_example_data)
        
        print("✅ GUI iniciada. La ventana debería aparecer ahora.")
        print("📋 Funcionalidades disponibles:")
        print("   • Cargar pozos (archivos LAS)")
        print("   • Visualizar curvas seleccionadas")
        print("   • Comparar múltiples pozos")
        print("   • Exportar gráficos y datos")
        print("   • Análisis rápido automatizado")
        
        # Ejecutar aplicación
        sys.exit(app.exec_())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("\\n💡 Instale las dependencias faltantes:")
    print("   pip install PyQt5 matplotlib numpy pandas welly")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
