import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pypozo import WellManager, WellPlotter
from pathlib import Path

print("🔧 PyPozo 2.0 - Análisis Completo de Pozos")
print("=" * 60)

# Lista de pozos a analizar
pozos_files = [
    "data/70449_abedul1_gn_1850_800_05mz79p.las",
    "data/PALO BLANCO 791_PROCESADO.las"
]

wells = []
output_dir = Path("output_workflow_simple")
output_dir.mkdir(exist_ok=True)

# Cargar y analizar cada pozo
for i, pozo_file in enumerate(pozos_files, 1):
    print(f"\n📁 {i}. Analizando: {Path(pozo_file).name}")
    print("-" * 50)
    
    try:
        # Cargar pozo
        well = WellManager.from_las(pozo_file)
        wells.append(well)
        
        # Información básica
        print(f"✅ Pozo: {well.name}")
        print(f"📊 Curvas: {well.curves}")
        print(f"📏 Profundidad: {well.depth_range[0]:.1f} - {well.depth_range[1]:.1f} m")
        
        # Analizar cada curva disponible
        for curve in well.curves:
            curve_data = well.get_curve_data(curve)
            if curve_data is not None:
                print(f"  📈 {curve}: {len(curve_data)} puntos | "
                      f"Rango: {curve_data.min():.1f}-{curve_data.max():.1f} | "
                      f"Promedio: {curve_data.mean():.1f}")
        
        # Crear visualización individual
        print(f"🎨 Creando visualizaciones...")
        plotter = WellPlotter()
        
        # Visualizar todas las curvas del pozo
        safe_name = well.name.replace("-", "_").replace(" ", "_")
        result = plotter.plot_multiple_curves(
            well,
            title=f"Análisis Completo - {well.name}",
            save_path=output_dir / f"{safe_name}_completo.png"
        )
        
        if result:
            print(f"✅ Visualización completa guardada: {result.name}")
        
    except Exception as e:
        print(f"❌ Error procesando {Path(pozo_file).name}: {str(e)}")

# Comparar pozos si tenemos más de uno
if len(wells) > 1:
    print(f"\n🔄 Comparando Pozos")
    print("=" * 30)
    
    plotter = WellPlotter()
    
    # Encontrar curvas comunes
    common_curves = set(wells[0].curves)
    for well in wells[1:]:
        common_curves = common_curves.intersection(set(well.curves))
    
    print(f"📋 Curvas comunes: {list(common_curves)}")
    
    # Crear comparaciones para cada curva común
    for curve in common_curves:
        print(f"📊 Comparando curva: {curve}")
        result = plotter.plot_well_comparison(
            wells,
            curve=curve,
            title=f"Comparación de Curva {curve}",
            save_path=output_dir / f"comparacion_{curve}.png"
        )
        
        if result:
            print(f"✅ Comparación {curve} guardada: {result.name}")

print(f"\n🎯 Análisis Completado")
print(f"📁 Archivos guardados en: {output_dir}")

# Demostración de selección de curvas específicas
print(f"\n🎨 Ejemplo de Selección de Curvas Específicas")
print("=" * 60)

if wells:
    # Tomar el pozo Palo Blanco (tiene más curvas)
    palo_blanco = None
    for well in wells:
        if "PALO BLANCO" in well.name.upper():
            palo_blanco = well
            break
    
    if palo_blanco:
        print(f"🔧 Análisis selectivo del pozo: {palo_blanco.name}")
        
        # Ejemplo 1: Curvas básicas de geofísica
        basic_curves = ["GR", "SP", "CAL"]
        available_basic = [c for c in basic_curves if c in palo_blanco.curves]
        
        if available_basic:
            print(f"📊 Graficando curvas básicas: {available_basic}")
            result = plotter.plot_selected_curves(
                palo_blanco,
                curves=available_basic,
                title=f"Registros Básicos - {palo_blanco.name}",
                save_path=output_dir / f"palo_blanco_basicos.png"
            )
            if result:
                print(f"✅ Curvas básicas guardadas: {result.name}")
        
        # Ejemplo 2: Curvas petrofísicas
        petro_curves = ["VCL", "PHIE", "SW", "ZDEN"]
        available_petro = [c for c in petro_curves if c in palo_blanco.curves]
        
        if available_petro:
            print(f"🔬 Graficando curvas petrofísicas: {available_petro}")
            result = plotter.plot_selected_curves(
                palo_blanco,
                curves=available_petro,
                title=f"Análisis Petrofísico - {palo_blanco.name}",
                save_path=output_dir / f"palo_blanco_petrofisico.png"
            )
            if result:
                print(f"✅ Curvas petrofísicas guardadas: {result.name}")
        
        # Ejemplo 3: Curvas acústicas
        acoustic_curves = ["DTC", "DTS", "VPVS", "POISDIN"]
        available_acoustic = [c for c in acoustic_curves if c in palo_blanco.curves]
        
        if available_acoustic:
            print(f"🔊 Graficando curvas acústicas: {available_acoustic}")
            result = plotter.plot_selected_curves(
                palo_blanco,
                curves=available_acoustic,
                title=f"Análisis Acústico - {palo_blanco.name}",
                save_path=output_dir / f"palo_blanco_acustico.png"
            )
            if result:
                print(f"✅ Curvas acústicas guardadas: {result.name}")
        
        # Ejemplo 4: NUEVA FUNCIONALIDAD - Registros juntos en la misma figura
        if len(available_basic) >= 2:
            print(f"🔗 Graficando curvas básicas juntas: {available_basic}")
            result = plotter.plot_curves_together(
                palo_blanco,
                curves=available_basic,
                title=f"Registros Combinados - {palo_blanco.name}",
                save_path=output_dir / f"palo_blanco_combinados.png"
            )
            if result:
                print(f"✅ Curvas combinadas guardadas: {result.name}")
        
        # Ejemplo 5: NUEVA FUNCIONALIDAD - Registros eléctricos con escala logarítmica
        electric_curves = ["M1R6", "M1R9"]  # Resistividades del Palo Blanco
        available_electric = [c for c in electric_curves if c in palo_blanco.curves]
        
        if available_electric:
            print(f"🔌 Graficando curvas eléctricas con escala log: {available_electric}")
            result = plotter.plot_well_logs_enhanced(
                palo_blanco,
                curves=available_electric,
                title=f"Registros Eléctricos (Log) - {palo_blanco.name}",
                save_path=output_dir / f"palo_blanco_electricos_log.png"
            )
            if result:
                print(f"✅ Curvas eléctricas (log) guardadas: {result.name}")

print(f"\n🎯 Funcionalidades Disponibles:")
print("• plot_well_logs(well, curves=['GR', 'SP']) - Curvas específicas")
print("• plot_multiple_curves(well) - Todas las curvas")
print("• plot_selected_curves(well, curves) - Con validación")
print("• plot_well_comparison(wells, curve) - Comparar pozos")
print("• plot_curves_together(well, curves) - 🆕 Curvas en misma figura")
print("• plot_well_logs_enhanced(well, curves) - 🆕 Con escala log automática")
print("  └─ Detecta automáticamente curvas eléctricas y aplica escala logarítmica")
print("• plot_curves_together(well, curves) - Registros juntos")
print("• plot_well_logs_enhanced(well, curves) - Registros eléctricos (log)")

print("=" * 60)