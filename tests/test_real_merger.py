#!/usr/bin/env python3
"""
Test Real Well Merger - PyPozo 2.0
===================================

Script para probar la funcionalidad real de fusión de pozos
en la aplicación PyPozo 2.0 GUI.

Este script:
1. Crea pozos sintéticos con traslapes
2. Carga la aplicación GUI
3. Prueba la funcionalidad de fusión
4. Verifica que los datos se combinen correctamente

Autor: José María García Márquez
Fecha: Enero 2025
"""

import sys
import logging
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd

# PyQt5 para GUI
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

# Importar la aplicación principal
sys.path.append(str(Path(__file__).parent))
from pypozo_app import PyPozoApp

# Importar módulos de PyPozo
from src.pypozo.core.well import WellManager, WellDataFrame

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_wells():
    """Crear pozos de prueba con traslapes."""
    
    print("🏗️ Creando pozos de prueba con traslapes...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Importar lasio para crear archivos LAS
        import lasio
        
        # Pozo 1: Rango 1000-1200m con GR, SP, CAL
        print("   📝 Creando Pozo 1 (1000-1200m)")
        depth1 = np.arange(1000, 1200.5, 0.5)
        gr1 = 60 + 40 * np.sin(depth1 / 50) + np.random.normal(0, 5, len(depth1))
        sp1 = -30 + 20 * np.cos(depth1 / 60) + np.random.normal(0, 3, len(depth1))
        cal1 = 8.5 + 1.0 * np.sin(depth1 / 80) + np.random.normal(0, 0.3, len(depth1))
        
        las1 = lasio.LASFile()
        las1.well.WELL = "TEST_WELL_1"
        las1.well.COMP = "PyPozo Test"
        las1.well.LOC = "Test Location"
        
        las1.append_curve('DEPT', depth1, unit='M', descr='Depth')
        las1.append_curve('GR', gr1, unit='GAPI', descr='Gamma Ray')
        las1.append_curve('SP', sp1, unit='MV', descr='Spontaneous Potential')
        las1.append_curve('CAL', cal1, unit='IN', descr='Caliper')
        
        file1 = temp_path / "test_well_1.las"
        las1.write(str(file1), version=2.0)
        
        # Pozo 2: Rango 1150-1350m con GR (traslape), RT, RES
        print("   📝 Creando Pozo 2 (1150-1350m) - Traslape en GR")
        depth2 = np.arange(1150, 1350.5, 0.5)
        # GR con continuidad pero algo de variación
        gr2 = 60 + 40 * np.sin(depth2 / 50) + np.random.normal(0, 8, len(depth2))
        rt2 = np.exp(1.5 + 0.8 * np.sin(depth2 / 70)) + np.random.normal(0, 0.2, len(depth2))
        res2 = np.exp(1.2 + 0.6 * np.cos(depth2 / 90)) + np.random.normal(0, 0.15, len(depth2))
        
        las2 = lasio.LASFile()
        las2.well.WELL = "TEST_WELL_2"
        las2.well.COMP = "PyPozo Test"
        las2.well.LOC = "Test Location"
        
        las2.append_curve('DEPT', depth2, unit='M', descr='Depth')
        las2.append_curve('GR', gr2, unit='GAPI', descr='Gamma Ray')
        las2.append_curve('RT', rt2, unit='OHMM', descr='Resistivity True')
        las2.append_curve('RES', res2, unit='OHMM', descr='Resistivity')
        
        file2 = temp_path / "test_well_2.las"
        las2.write(str(file2), version=2.0)
        
        # Pozo 3: Rango 1300-1500m con NPHI, DENS
        print("   📝 Creando Pozo 3 (1300-1500m)")
        depth3 = np.arange(1300, 1500.5, 0.5)
        nphi3 = 0.20 + 0.15 * np.sin(depth3 / 100) + np.random.normal(0, 0.03, len(depth3))
        dens3 = 2.4 + 0.3 * np.cos(depth3 / 120) + np.random.normal(0, 0.05, len(depth3))
        
        las3 = lasio.LASFile()
        las3.well.WELL = "TEST_WELL_3"
        las3.well.COMP = "PyPozo Test"
        las3.well.LOC = "Test Location"
        
        las3.append_curve('DEPT', depth3, unit='M', descr='Depth')
        las3.append_curve('NPHI', nphi3, unit='V/V', descr='Neutron Porosity')
        las3.append_curve('DENS', dens3, unit='G/C3', descr='Bulk Density')
        
        file3 = temp_path / "test_well_3.las"
        las3.write(str(file3), version=2.0)
        
        # Copiar archivos al directorio actual para uso persistente
        output_dir = Path("test_merger_output")
        output_dir.mkdir(exist_ok=True)
        
        files_created = []
        for file in [file1, file2, file3]:
            dest = output_dir / file.name
            dest.write_bytes(file.read_bytes())
            files_created.append(dest)
            print(f"      ✅ Creado: {dest}")
        
        print(f"📁 Archivos de prueba creados en: {output_dir}")
        return files_created

def test_well_merger_programmatically():
    """Probar la fusión de pozos programáticamente."""
    
    print("\n🧪 Probando fusión de pozos programáticamente...")
    
    try:
        # Crear archivos de prueba
        test_files = create_test_wells()
        
        # Cargar pozos
        wells = []
        for file in test_files:
            print(f"   📂 Cargando: {file.name}")
            well = WellManager.from_las(file)
            wells.append(well)
            print(f"      ✅ {well.name}: {len(well.curves)} curvas, rango {well.depth_range}")
        
        # Fusionar pozos
        print(f"\n🔗 Fusionando {len(wells)} pozos...")
        merged_well = WellDataFrame.merge_wells(wells, "TEST_MERGED_WELL")
        
        if merged_well is None:
            print("❌ Error en la fusión")
            return False
        
        # Verificar resultado
        print(f"\n✅ Fusión completada:")
        print(f"   📋 Nombre: {merged_well.name}")
        print(f"   📊 Curvas: {len(merged_well.curves)}")
        print(f"   🎯 Rango: {merged_well.depth_range[0]:.1f}-{merged_well.depth_range[1]:.1f}m")
        
        # Listar curvas disponibles
        print(f"   📈 Curvas disponibles: {merged_well.curves}")
        
        # Verificar que efectivamente hay datos combinados
        df = merged_well._well.df()
        print(f"   📊 Puntos de datos: {len(df)}")
        
        # Verificar traslapes en GR (debe aparecer en pozos 1 y 2)
        if 'GR' in merged_well.curves:
            gr_data = merged_well.get_curve_data('GR')
            overlap_range = (1150, 1200)  # Rango de traslape esperado
            overlap_data = gr_data[(gr_data.index >= overlap_range[0]) & 
                                  (gr_data.index <= overlap_range[1])]
            print(f"   🔄 Datos en zona de traslape GR: {len(overlap_data)} puntos")
        
        # Guardar pozo fusionado
        output_file = Path("test_merger_output") / f"{merged_well.name}.las"
        success = merged_well.export_to_las(output_file)
        
        if success:
            print(f"   💾 Pozo fusionado guardado: {output_file}")
        else:
            print(f"   ⚠️ Advertencia: Error guardando archivo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba programática: {str(e)}")
        return False

def test_gui_merger():
    """Probar la fusión desde la GUI."""
    
    print("\n🖥️ Probando fusión desde la GUI...")
    
    try:
        # Crear aplicación
        app = QApplication(sys.argv)
        
        # Crear ventana principal
        window = PyPozoApp()
        window.show()
        
        # Cargar pozos de prueba
        test_files = Path("test_merger_output").glob("test_well_*.las")
        
        for file in test_files:
            print(f"   📂 Cargando en GUI: {file.name}")
            # Aquí se cargaría el archivo en la GUI
            # window.load_las_file(str(file))
        
        print("   ℹ️ GUI iniciada. Cargue los archivos de test_merger_output/ manualmente")
        print("   ℹ️ Luego seleccione múltiples pozos y use 'Fusionar Pozos'")
        
        # Ejecutar aplicación
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error en prueba GUI: {str(e)}")
        return False

def main():
    """Función principal."""
    
    print("=" * 60)
    print("🧪 TEST DE FUSIÓN REAL DE POZOS - PyPozo 2.0")
    print("=" * 60)
    
    try:
        # Prueba programática
        success_prog = test_well_merger_programmatically()
        
        if success_prog:
            print("\n✅ Prueba programática exitosa")
            
            # Preguntar si se quiere probar la GUI
            print("\n🖥️ ¿Desea probar la fusión desde la GUI? (y/n)")
            response = input().lower().strip()
            
            if response == 'y':
                test_gui_merger()
            else:
                print("ℹ️ Para probar la GUI manualmente:")
                print("   1. Ejecute: python pypozo_app.py")
                print("   2. Cargue los archivos de test_merger_output/")
                print("   3. Seleccione múltiples pozos")
                print("   4. Use el botón 'Fusionar Pozos'")
        else:
            print("\n❌ Prueba programática falló")
            return False
        
        print("\n🎉 Todas las pruebas completadas")
        return True
        
    except Exception as e:
        print(f"❌ Error en función principal: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
