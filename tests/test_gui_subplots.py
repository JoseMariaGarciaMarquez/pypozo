#!/usr/bin/env python3
"""
Test rápido de la GUI con la corrección de subplots implementada.
Carga un pozo y prueba la visualización con subplots compartidos.
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# Agregar el directorio raíz al path para pypozo_app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication
import tempfile
import shutil

def test_gui_subplots():
    """Test rápido de la GUI con subplots."""
    print("🧪 Test rápido de GUI con corrección de subplots")
    print("=" * 60)
    
    try:
        # Importar y crear la aplicación GUI
        from pypozo_app import PyPozoApp
        
        app = QApplication(sys.argv)
        window = PyPozoApp()
        
        # Buscar archivo de test
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        test_files = []
        
        for file in os.listdir(data_dir):
            if file.endswith('.las'):
                test_files.append(os.path.join(data_dir, file))
        
        if not test_files:
            print("❌ No se encontraron archivos LAS para prueba")
            return False
        
        test_file = test_files[0]
        print(f"📁 Usando archivo: {os.path.basename(test_file)}")
        
        # Cargar pozo
        window.load_well_from_path(test_file)
        
        if window.current_well:
            print(f"✅ Pozo cargado: {window.current_well.name}")
            print(f"📊 Curvas disponibles: {len(window.current_well.curves)}")
            
            # Probar visualización de todas las curvas (que usa subplots)
            window.plot_all_curves()
            print("✅ Visualización con subplots ejecutada correctamente")
            
            # Verificar que la figura fue creada
            if window.figure.get_axes():
                axes = window.figure.get_axes()
                print(f"📊 Subplots creados: {len(axes)}")
                
                # Verificar que todos tienen el mismo rango Y
                if len(axes) > 1:
                    first_ylim = axes[0].get_ylim()
                    all_same = all(
                        abs(ax.get_ylim()[0] - first_ylim[0]) < 0.1 and 
                        abs(ax.get_ylim()[1] - first_ylim[1]) < 0.1 
                        for ax in axes
                    )
                    
                    if all_same:
                        print(f"✅ Todos los subplots comparten el rango Y: {first_ylim}")
                        result = True
                    else:
                        print("❌ Los subplots tienen rangos Y diferentes")
                        for i, ax in enumerate(axes):
                            print(f"  Subplot {i}: {ax.get_ylim()}")
                        result = False
                else:
                    print("✅ Un solo subplot creado correctamente")
                    result = True
                    
                # Guardar la figura para inspección visual
                output_file = os.path.join(os.path.dirname(__file__), '..', 'test_gui_subplots.png')
                window.figure.savefig(output_file, dpi=300, bbox_inches='tight')
                print(f"💾 Figura guardada en: {output_file}")
                
            else:
                print("❌ No se crearon subplots")
                result = False
            
        else:
            print("❌ No se pudo cargar el pozo")
            result = False
        
        # No mostrar la ventana, solo probar programáticamente
        app.quit()
        
        return result
        
    except Exception as e:
        print(f"❌ Error en test GUI: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar test de GUI."""
    success = test_gui_subplots()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST GUI EXITOSO: Subplots funcionan correctamente en la GUI")
    else:
        print("❌ TEST GUI FALLIDO: Problemas con subplots en la GUI")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
