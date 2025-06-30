# PyPozo 2.0 🛢️

**PyPozo 2.0** es un sistema moderno y profesional de análisis de pozos con interfaz gráfica avanzada, diseñado como alternativa Open Source a WellCAD. Ofrece capacidades completas de procesamiento, visualización e interpretación de registros geofísicos.

## 🎯 Características Principales

✅ **Interfaz Gráfica Profesional** - GUI moderna con PyQt5 y matplotlib integrado  
✅ **Análisis Multi-Curva Avanzado** - Visualización individual y combinada de registros  
✅ **Detección Automática de Curvas Eléctricas** - Identificación inteligente por unidades (OHMM) y nombres  
✅ **Escala Logarítmica Automática** - Aplicación automática para curvas de resistividad  
✅ **Visualización de Unidades** - Etiquetas automáticas con unidades en gráficos  
✅ **Comparación de Pozos** - Análisis comparativo de múltiples pozos  
✅ **Procesamiento Automatizado** - Flujos de trabajo estandarizados y profesionales  

## � Nuevas Funcionalidades v2.0

### 🔗 **Graficado de Curvas Combinadas**
- **Curvas Superpuestas**: Graficar múltiples registros en la misma figura
- **Normalización Opcional**: Escalado 0-1 para comparación visual
- **Detección Inteligente**: Aplicación automática de escala logarítmica

### ⚡ **Análisis de Curvas Eléctricas**
- **Detección por Unidades**: Identifica automáticamente curvas con unidades OHMM, OHM
- **Patrones de Nombres**: Reconoce RT, RES, ILM, LLD, M1R, etc.
- **Escala Log Automática**: Aplicación inteligente para registros de resistividad

### 🏷️ **Visualización Mejorada**
- **Unidades en Etiquetas**: Muestra automáticamente las unidades en ejes
- **Estadísticas Integradas**: N, Min, Max, Media en cada gráfico
- **Colores Profesionales**: Paleta optimizada para análisis técnico

## 🏗️ Arquitectura Modular

### 🔧 **Core (Núcleo)**
- **`WellManager`**: Clase principal con validación automática y acceso a curvas/metadata
- **`ProjectManager`**: Manejo de múltiples pozos con workflows coordinados
- **`get_curve_units()`**: Extracción automática de unidades desde archivos LAS

### ⚙️ **Processors (Procesadores)**
- **`StandardizeProcessor`**: Estandarización automática de mnemonics y unidades
- **`GeophysicsCalculator`**: Cálculos geofísicos (VSH, porosidad, zonas clave)

### 📊 **Visualization (Visualización)**
- **`WellPlotter`**: Sistema avanzado de visualización interpretativa
- **`plot_curves_together()`**: Graficado de curvas superpuestas con normalización
- **`plot_well_logs_enhanced()`**: Visualización con escala logarítmica automática
- **`_is_electrical_curve()`**: Detección inteligente de curvas eléctricas

### 📱 **GUI (Interfaz Gráfica)**
- **`PyPozoApp`**: Aplicación principal con interfaz moderna
- **Selección Automática**: Botones para curvas básicas, petrofísicas, acústicas y eléctricas
- **Exportación Integrada**: Guardado directo de gráficos y datos
- **Log de Actividades**: Seguimiento completo de operaciones

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/JoseMariaGarciaMarquez/pypozo.git
cd pypozo

# Instalar dependencias
pip install -e .
pip install PyQt5  # Para la interfaz gráfica

# Opcional: crear ambiente conda
conda env create -f pozoambiente.yaml
conda activate pozoambiente
```

## 📖 Uso Rápido - PyPozo 2.0

### �️ **Uso con Interfaz Gráfica (GUI) - Recomendado**

```bash
# Lanzar la aplicación gráfica
python pypozo_app.py
```

**Funcionalidades de la GUI:**
- 📂 **Cargar Pozos**: Arrastrar y soltar archivos LAS o usar el explorador
- 🎨 **Visualización Avanzada**: 
  - Gráficos individuales por curva
  - **🔗 Graficar Juntas**: Superponer múltiples curvas en la misma figura
  - Normalización automática para comparación visual
- ⚡ **Selección Inteligente**: 
  - Botón "⚡ Eléctricas" detecta automáticamente curvas de resistividad
  - Presets para curvas básicas, petrofísicas y acústicas
- 📊 **Análisis Automático**: Escala logarítmica para curvas eléctricas
- 💾 **Exportación**: Guardar gráficos en PNG, PDF, SVG
- ⚖️ **Comparación**: Analizar múltiples pozos simultáneamente

### 🐍 **Uso Programático - Nuevas Funciones**

```python
from pypozo import WellManager, WellPlotter

# Cargar pozo
well = WellManager.from_las("data/mi_pozo.las")
plotter = WellPlotter()

# 🔗 Graficar curvas eléctricas juntas con escala logarítmica automática
electrical_curves = ['M1R6', 'M1R9', 'RT']
plotter.plot_curves_together(
    well,
    curves=electrical_curves,
    title="Registros de Resistividad",
    normalize=False,  # Mantener valores originales
    save_path="resistividad_log.png"
)

# 📊 Visualización mejorada con detección automática
plotter.plot_well_logs_enhanced(
    well,
    curves=['RT', 'GR', 'RHOB', 'NPHI'],
    title="Registros con Escala Log Automática",
    save_path="registros_mejorados.png"
)

# 🏷️ Obtener unidades de las curvas
for curve in well.curves:
    units = well.get_curve_units(curve)
    is_electrical = plotter._is_electrical_curve(curve, well)
    print(f"{curve}: {units} {'⚡ ELÉCTRICA' if is_electrical else ''}")
```

### 🔄 **Workflow Automatizado Tradicional**

```python
from pypozo import StandardWorkflow
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Crear workflow
workflow = StandardWorkflow(output_dir="resultados")

# Procesar pozo individual - TODO AUTOMÁTICO
resultado = workflow.process_single_well(
    well_source="data/mi_pozo.las",
    generate_plots=True,      # ✅ Plots automáticos
    export_gis=True,          # ✅ Exportación GIS
    export_formats=['csv', 'excel', 'geojson']  # ✅ Múltiples formatos
)

print(f"✅ Pozo procesado: {resultado['well_name']}")
print(f"📁 Resultados en: {resultado['output_directory']}")
```

### 🏗️ Uso Modular (Avanzado)

```python
from pypozo import Well, StandardizeProcessor, GeophysicsCalculator, WellPlotter

# 1. Cargar pozo con validación automática
well = Well.from_las("data/mi_pozo.las")

# 2. Estandarizar mnemonics y unidades
standardizer = StandardizeProcessor()
standardizer.standardize_well(well)

# 3. Calcular propiedades geofísicas
calculator = GeophysicsCalculator()
vsh = calculator.calculate_vsh(well, method='larionov')
porosity = calculator.calculate_porosity(well, method='density')

# 4. Visualización profesional
plotter = WellPlotter()
plotter.plot_standard_logs(well, save_path="logs.png")
plotter.plot_petrophysics(well, save_path="petro.png")
```

### 🔄 Procesamiento de Proyectos Multi-Pozo

```python
from pypozo import Project, StandardWorkflow

# Crear proyecto con múltiples pozos
proyecto = Project("Campo_Norte")
proyecto.add_wells([
    "data/pozo_A.las",
    "data/pozo_B.las", 
    "data/pozo_C.las"
])

# Workflow automático para todo el proyecto
workflow = StandardWorkflow(output_dir="proyecto_completo")
resultado = workflow.process_project(
    project=proyecto,
    generate_summary=True,        # ✅ Resumen del proyecto
    cross_plot_wells=True,        # ✅ Gráficos cruzados
    export_gis=True               # ✅ Integración GIS
)

print(f"✅ Proyecto procesado: {resultado['project_summary']['total_wells']} pozos")
```

## 📁 Nueva Estructura del Proyecto

```
pypozo/
├── src/pypozo/              # Código fuente principal
│   ├── core/                # 🔧 Núcleo
│   │   ├── well.py         # Clase Well moderna
│   │   └── project.py      # Clase Project
│   ├── processors/          # ⚙️ Procesadores
│   │   ├── standardizer.py # Estandarización automática
│   │   └── calculator.py   # Cálculos geofísicos
│   ├── visualization/       # 📊 Visualización
│   │   └── plotter.py      # Sistema de plots profesional
│   ├── integration/         # 🌍 Integración
│   │   └── gis.py          # Exportación GIS/SIG
│   └── workflows/           # 🔄 Workflows
│       └── standard.py     # Workflow estándar
├── examples/               # Ejemplos de uso PyPozo 2.0
├── notebooks/             # Jupyter notebooks actualizados
├── tests/                # Tests para PyPozo 2.0
└── data/                # Datos de ejemplo
```

## 🔧 Dependencias Modernas

```toml
# Análisis y procesamiento
numpy = ">=1.21.0"
pandas = ">=1.5.0"
scipy = ">=1.9.0"

# Archivos LAS y geofísica
lasio = ">=0.30"
welly = ">=0.5.2"

# Visualización profesional
matplotlib = ">=3.6.0"
seaborn = ">=0.12.0"

# Integración GIS
geopandas = ">=0.12.0"
pyproj = ">=3.4.0"

# Exportación y formatos
openpyxl = ">=3.1.0"
xlsxwriter = ">=3.0.0"
```

## 🧪 Pruebas y Validación

```bash
# Ejecutar tests de PyPozo 2.0
python -m pytest tests/ -v

# Test específicos por módulo
python -m pytest tests/test_core.py       # Core (Well, Project)
python -m pytest tests/test_processors.py # Procesadores
python -m pytest tests/test_workflows.py  # Workflows

# Con coverage
python -m pytest tests/ --cov=pypozo --cov-report=html
```

## 📊 Ejemplos Actualizados

### 📁 Archivos de Ejemplo PyPozo 2.0

- **`examples/workflow_simple.py`**: Workflow básico con un pozo
- **`examples/proyecto_multipozo.py`**: Proyecto con múltiples pozos  
- **`examples/integracion_gis.py`**: Exportación a SIG y MODFLOW
- **`notebooks/get_started.ipynb`**: Tutorial interactivo actualizado

### 🔄 Migración desde PyPozo 1.x

```python
# PyPozo 1.x (OBSOLETO)
from pypozo import WellAnalyzer
well = WellAnalyzer("pozo.las")
vsh = well.calculate_vsh_larionov()

# PyPozo 2.0 (NUEVO)
from pypozo import StandardWorkflow
workflow = StandardWorkflow()
resultado = workflow.process_single_well("pozo.las")
# ✅ TODO automático: estandarización, cálculos, plots, exportación
```

## 🆕 Nuevas Funcionalidades Destacadas v2.0

### 🔗 **Graficado de Curvas Combinadas**
```python
# Graficar múltiples curvas eléctricas juntas
plotter.plot_curves_together(
    well, 
    curves=['M1R6', 'M1R9', 'RT'],
    normalize=False,  # Valores originales con escala log automática
    title="Resistividad - Escala Logarítmica"
)

# Comparación visual con normalización
plotter.plot_curves_together(
    well,
    curves=['GR', 'SP', 'CAL'],
    normalize=True,  # Escalado 0-1 para comparación
    title="Curvas Básicas Normalizadas"
)
```

### ⚡ **Detección Automática de Curvas Eléctricas**
```python
# Detecta automáticamente por unidades (OHMM, OHM) y nombres
electrical_curves = []
for curve in well.curves:
    if plotter._is_electrical_curve(curve, well):
        units = well.get_curve_units(curve)
        electrical_curves.append(curve)
        print(f"⚡ {curve} ({units}) - ELÉCTRICA")

# En la GUI: Botón "⚡ Eléctricas" hace esto automáticamente
```

### 🏷️ **Visualización de Unidades**
```python
# Las unidades aparecen automáticamente en las etiquetas
# Ejemplo: "M1R6 (OHMM)", "GR (GAPI)", "DTC (us/ft)"

# Obtener unidades programáticamente
units = well.get_curve_units('M1R6')  # Returns: "OHMM"
```

## 📊 Ejemplos Actualizados

### � **Archivos de Ejemplo PyPozo 2.0**

- **`pypozo_app.py`**: 🆕 Aplicación GUI completa
- **`test_nuevas_funciones.py`**: 🆕 Demo de nuevas características
- **`examples/workflow_simple.py`**: Workflow básico con un pozo
- **`examples/proyecto_multipozo.py`**: Proyecto con múltiples pozos  
- **`examples/integracion_gis.py`**: Exportación a SIG y MODFLOW
- **`notebooks/get_started.ipynb`**: Tutorial interactivo actualizado

### 🖥️ **Prueba Rápida de la GUI**

```bash
# Lanzar la aplicación
python pypozo_app.py

# O ejecutar tests de las nuevas funciones
python test_nuevas_funciones.py
python tests/pruebas.py
```

### 🔄 **Migración desde PyPozo 1.x**

```python
# PyPozo 1.x (OBSOLETO)
from pypozo import WellAnalyzer
well = WellAnalyzer("pozo.las")
vsh = well.calculate_vsh_larionov()

# PyPozo 2.0 (NUEVO - Programático)
from pypozo import WellManager, WellPlotter
well = WellManager.from_las("pozo.las")
plotter = WellPlotter()
plotter.plot_well_logs_enhanced(well, well.curves[:5])

# PyPozo 2.0 (NUEVO - GUI)
# python pypozo_app.py
# ✅ TODO visual: cargar, seleccionar, graficar, exportar
```

## 🚀 **Beneficios de PyPozo 2.0**

### ✅ **Interfaz Gráfica Profesional**
- **Alternativa a WellCAD**: Funcionalidades comparables sin costo de licencia
- **Workflow Visual**: Desde carga hasta exportación sin programar
- **Análisis Interactivo**: Selección de curvas, comparación de pozos

### ✅ **Detección Inteligente**
- **Automática por Unidades**: Identifica curvas eléctricas por OHMM, OHM
- **Escala Logarítmica**: Aplicación automática para resistividad
- **Selección por Tipo**: Botones para básicas, petrofísicas, acústicas, eléctricas

### ✅ **Visualización Avanzada**
- **Curvas Superpuestas**: Comparación directa en la misma figura
- **Normalización**: Escalado 0-1 para curvas con diferentes rangos
- **Unidades en Etiquetas**: Información completa automática
- **Exportación Multi-formato**: PNG, PDF, SVG con alta resolución

| Característica | PyPozo 1.x | PyPozo 2.0 |
|---|---|---|
| **Arquitectura** | Monolítica | Modular y extensible |
| **Estandarización** | Manual | Automática |
| **Workflows** | Ad-hoc | Estandarizados |
| **Integración GIS** | No | Completa |
| **Visualización** | Básica | Profesional |
| **Logging** | No | Completo |
| **Validación** | Mínima | Automática |

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📋 Roadmap PyPozo 2.0

- [x] **v2.0.0**: Arquitectura modular completa
- [x] **v2.0.0**: Workflow estándar automatizado
- [x] **v2.0.0**: Integración GIS completa
- [ ] **v2.1.0**: Tests unitarios al 100%
- [ ] **v2.2.0**: Documentación API completa
- [ ] **v2.3.0**: Interfaz web opcional
- [ ] **v2.4.0**: Integración con bases de datos
- [ ] **v3.0.0**: Módulos de inteligencia artificial

## ⚠️ Estado del Desarrollo

**PyPozo 2.0 está funcional y listo para uso profesional.** 

La nueva arquitectura es estable y todas las funcionalidades principales están operativas. Se recomienda migrar de PyPozo 1.x a PyPozo 2.0 para obtener los beneficios de automatización y estandarización.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- Comunidad de geofísica por feedback y casos de uso reales
- Contribuidores de Welly, Lasio y GeoPandas
- Usuarios que han ayudado a definir los requisitos profesionales

---

## Desarrollado con ❤️ para la comunidad de geofísica e ingeniería

**PyPozo 2.0** - Procesamiento profesional de registros geofísicos 
