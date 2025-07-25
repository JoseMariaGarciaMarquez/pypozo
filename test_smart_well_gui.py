"""
Test rápido del sistema 'Pozo Inteligente' con datos reales de PyPozo.
"""

import sys
sys.path.append(r'c:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\pypozo')

from PyQt5.QtWidgets import QApplication
import welly
import pandas as pd

def test_smart_well_with_real_data():
    """Probar el sistema con datos reales de PyPozo."""
    print("🧠 Probando sistema 'Pozo Inteligente' con datos reales...")
    
    try:
        # Cargar un archivo LAS real
        las_file = r"c:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\pypozo\data\ABEDUL-1_MERGED_COMPLETE.las"
        
        print(f"📁 Cargando archivo: {las_file}")
        well = welly.Well.from_las(las_file)
        print(f"✅ Pozo cargado: {well.header.name if hasattr(well.header, 'name') else 'Sin nombre'}")
        
        # Obtener DataFrame
        df = well.df()
        print(f"✅ DataFrame obtenido: {len(df)} filas, {len(df.columns)} columnas")
        print(f"📊 Curvas disponibles: {list(df.columns)}")
        
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        
        # Probar el sistema 'Pozo Inteligente'
        from patreon_dlc.completion.smart_well_gui import SmartWellDialog
        
        # Crear diálogo con el pozo real
        dialog = SmartWellDialog([well])
        print("✅ SmartWellDialog creado con datos reales")
        
        # Mostrar el diálogo
        dialog.show()
        print("✅ GUI 'Pozo Inteligente' desplegada con datos reales")
        
        print("\n🎉 ¡Prueba exitosa con datos reales!")
        print("🔍 Puedes probar todas las funcionalidades:")
        print("   • Selección de curvas")
        print("   • Análisis IA de correlaciones")
        print("   • Completado neuronal")
        
        # Ejecutar aplicación
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = test_smart_well_with_real_data()
    sys.exit(exit_code)
