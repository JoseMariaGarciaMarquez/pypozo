#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico para validar que los subplots funcionan en GUI
"""

import sys
from pathlib import Path
import numpy as np

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    from PyQt5.QtCore import Qt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    
    from pypozo import WellManager

    class TestSubplotsGUI(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Test Subplots GUI")
            self.setGeometry(100, 100, 800, 600)
            
            # Widget central
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Canvas de matplotlib
            self.figure = Figure(figsize=(10, 8))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
            
            # Cargar datos y probar
            self.load_and_plot()
        
        def load_and_plot(self):
            try:
                print("🔧 Cargando pozo...")
                well = WellManager.from_las("data/PALO BLANCO 791_PROCESADO.las")
                
                print(f"✅ Pozo cargado: {well.name}")
                print(f"📊 Curvas disponibles: {well.curves[:5]}")
                
                # Seleccionar algunas curvas para probar
                test_curves = ["GR", "SP", "CAL"]
                available_curves = [c for c in test_curves if c in well.curves]
                
                print(f"🎨 Probando con curvas: {available_curves}")
                
                if available_curves:
                    self.plot_curves_safe(well, available_curves)
                else:
                    print("❌ No hay curvas de prueba disponibles")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        def plot_curves_safe(self, well, curves):
            """Método seguro para graficar curvas con subplots."""
            try:
                # Limpiar figura
                self.figure.clf()
                
                # Obtener datos
                df = well._well.df()
                n_curves = len(curves)
                
                print(f"📊 Creando {n_curves} subplots...")
                
                # Colores
                colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00']
                
                # Crear subplots uno por uno
                for i, curve_name in enumerate(curves):
                    print(f"  📈 Procesando curva {i+1}/{n_curves}: {curve_name}")
                    
                    ax = self.figure.add_subplot(1, n_curves, i + 1)
                    
                    if curve_name in df.columns:
                        curve_data = df[curve_name].dropna()
                        
                        if len(curve_data) > 0:
                            depth = curve_data.index
                            values = curve_data.values
                            
                            # Verificar valores finitos
                            valid_mask = np.isfinite(values) & np.isfinite(depth)
                            
                            if np.any(valid_mask):
                                values = values[valid_mask]
                                depth = depth[valid_mask]
                                
                                # Graficar
                                color = colors[i % len(colors)]
                                ax.plot(values, depth, linewidth=1.5, color=color)
                                ax.fill_betweenx(depth, values, alpha=0.3, color=color)
                                
                                # Obtener unidades
                                units = well.get_curve_units(curve_name)
                                xlabel = f'{curve_name} ({units})' if units else curve_name
                                
                                # Configurar ejes
                                ax.set_xlabel(xlabel, fontsize=10, fontweight='bold')
                                ax.set_title(curve_name, fontsize=11, fontweight='bold')
                                ax.invert_yaxis()
                                ax.grid(True, alpha=0.3)
                                
                                # Solo el primer subplot tiene etiqueta Y
                                if i == 0:
                                    ax.set_ylabel('Profundidad (m)', fontsize=10, fontweight='bold')
                                
                                print(f"    ✅ {curve_name}: {len(values)} puntos válidos")
                            else:
                                print(f"    ⚠️ {curve_name}: sin valores finitos")
                        else:
                            print(f"    ⚠️ {curve_name}: sin datos después de dropna()")
                    else:
                        print(f"    ❌ {curve_name}: no encontrada en DataFrame")
                
                # Título
                self.figure.suptitle(f'Test Subplots GUI - {well.name}', fontsize=12, fontweight='bold')
                
                # Layout
                try:
                    self.figure.tight_layout()
                    self.figure.subplots_adjust(top=0.9)
                except Exception as e:
                    print(f"⚠️ Warning en layout: {str(e)}")
                
                # Actualizar
                self.canvas.draw()
                print("✅ Gráfico creado exitosamente en GUI")
                
            except Exception as e:
                print(f"❌ Error en plot_curves_safe: {str(e)}")
                import traceback
                traceback.print_exc()

    def main():
        print("🚀 Test de Subplots en GUI")
        print("=" * 40)
        
        app = QApplication(sys.argv)
        window = TestSubplotsGUI()
        window.show()
        
        print("👁️ Ventana mostrada. Presione Ctrl+C para salir.")
        
        try:
            sys.exit(app.exec_())
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Error de importación: {str(e)}")
    print("💡 Asegúrese de tener instalado PyQt5 y matplotlib")
    print("   pip install PyQt5 matplotlib")
