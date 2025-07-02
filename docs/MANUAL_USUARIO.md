# Manual de Usuario - PyPozo 2.0

![PyPozo Logo](../examples/pypozo_logo.png)

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Guía Rápida](#guía-rápida)
4. [Manual de la Aplicación GUI](#manual-de-la-aplicación-gui)
5. [Manual de la Librería](#manual-de-la-librería)
6. [Ejemplos Prácticos](#ejemplos-prácticos)
7. [Solución de Problemas](#solución-de-problemas)
8. [Referencias](#referencias)

---

## 🎯 Introducción

**PyPozo** es una suite completa de herramientas para el análisis de pozos petroleros, diseñada como una alternativa Open Source profesional a software comercial como WellCAD. Incluye:

- **Aplicación GUI**: Interfaz gráfica completa para análisis interactivo
- **Librería Python**: API programática para automatización y scripts
- **Cálculos Petrofísicos**: Módulos especializados para VCL, porosidad, saturación
- **Visualización Avanzada**: Gráficos profesionales de registros de pozos

### ✨ Características Principales

- ✅ **Carga de archivos LAS** (Log ASCII Standard)
- ✅ **Visualización interactiva** de curvas de registros
- ✅ **Cálculos petrofísicos** (VCL, PHIE, análisis litológico)
- ✅ **Comparación de pozos** múltiples
- ✅ **Fusión automática** de registros
- ✅ **Exportación** a múltiples formatos
- ✅ **Workflows automatizados**
- ✅ **Interfaz profesional** moderna

---

## 🔧 Instalación

### Requisitos del Sistema

- **Python**: 3.8 o superior
- **Sistema Operativo**: Windows, macOS, Linux
- **RAM**: Mínimo 4GB (recomendado 8GB)
- **Espacio en disco**: 500MB

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/usuario/pypozo.git
cd pypozo

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar PyPozo
pip install -e .
```

### Verificar Instalación

```bash
# Probar la librería
python -c "from pypozo import WellManager; print('✅ PyPozo instalado correctamente')"

# Probar la aplicación GUI
python pypozo_app.py
```

---

## 🚀 Guía Rápida

### Inicio Rápido - Aplicación GUI

1. **Ejecutar la aplicación**:
   ```bash
   python pypozo_app.py
   ```

2. **Cargar un pozo**:
   - Botón "📂 Cargar Pozo" → Seleccionar archivo `.las`
   - El pozo aparecerá en el explorador izquierdo

3. **Visualizar curvas**:
   - Seleccionar curvas en la pestaña "📊 Curvas"
   - Hacer clic en "🎨 Graficar Seleccionadas"

4. **Análisis petrofísico**:
   - Ir a pestaña "🧪 Petrofísica"
   - Configurar parámetros y calcular VCL/PHIE

### Inicio Rápido - Librería

```python
from pypozo import WellManager

# Cargar pozo
well = WellManager.from_las("mi_pozo.las")

# Ver información básica
print(f"Pozo: {well.name}")
print(f"Profundidad: {well.depth_range}")
print(f"Curvas: {well.curves}")

# Obtener datos de una curva
gr_data = well.get_curve_data("GR")
print(gr_data.describe())

# Calcular VCL
from pypozo.petrophysics import VclCalculator
calc = VclCalculator()
result = calc.calculate(
    gamma_ray=well.data["GR"],
    gr_clean=15,
    gr_clay=150,
    method="larionov_tertiary"
)

# Agregar resultado al pozo
well.add_curve("VCL", result['vcl'], units="fraction")
```

---

## 🖥️ Manual de la Aplicación GUI

### Interfaz Principal

La aplicación está dividida en tres paneles principales:

#### Panel Izquierdo - Explorador de Pozos
- **Árbol de pozos**: Lista de pozos cargados
- **Botones de carga**: Cargar uno o múltiples pozos
- **Propiedades**: Información detallada del pozo seleccionado

#### Panel Central - Visualización
- **Canvas de gráficos**: Área principal para mostrar curvas
- **Controles de graficado**: Botones para diferentes tipos de visualización
- **Toolbar**: Accesos rápidos a funciones principales

#### Panel Derecho - Herramientas
Contiene cuatro pestañas principales:

### 📊 Pestaña Curvas

**Función**: Selección y configuración de curvas para graficar.

**Controles principales**:
- **Lista de curvas**: Selección múltiple de curvas disponibles
- **Botones de selección rápida**:
  - ✅ **Todo**: Selecciona todas las curvas
  - ❌ **Nada**: Deselecciona todas
  - 📊 **Básicas**: GR, SP, CAL, RT, RHOB, NPHI
  - 🔬 **Petrofísicas**: VCL, PHIE, SW, etc.
  - 🔊 **Acústicas**: DTC, DTS, VPVS, etc.
  - ⚡ **Eléctricas**: Detecta automáticamente curvas de resistividad

**Tipos de gráficos**:
- **🎨 Graficar Seleccionadas**: Subplots individuales para cada curva
- **🔗 Graficar Juntas**: Todas las curvas en un solo gráfico (con opción de normalización)
- **📊 Graficar Todo**: Todas las curvas disponibles (máximo 8)

### ⚖️ Pestaña Comparar

**Función**: Comparación visual entre múltiples pozos.

**Pasos para comparar**:
1. Seleccionar 2 o más pozos de la lista
2. Elegir la curva a comparar
3. Hacer clic en "⚖️ Comparar Seleccionados"

**Fusión de pozos**:
- Botón "🔗 Fusionar Seleccionados"
- Combina registros de pozos duplicados automáticamente
- Promedia valores en zonas de traslape

### 🔬 Pestaña Análisis

**Función**: Herramientas de análisis automático.

**Análisis rápido**:
- **📈 Análisis Completo**: Genera reporte estadístico del pozo
- **📤 Exportar Datos**: Exporta a LAS o CSV

**Log de actividades**:
- Registro en tiempo real de todas las operaciones
- Útil para debugging y seguimiento de procesos

### 🧪 Pestaña Petrofísica

**Función**: Cálculos petrofísicos especializados.

#### Volumen de Arcilla (VCL)

**Métodos disponibles**:
- **Linear**: VCL = IGR (método más simple)
- **Larionov Older**: Para rocas Pre-Terciarias
- **Larionov Tertiary**: Para rocas Terciarias (recomendado)
- **Clavier**: Uso general, buen balance
- **Steiber**: Para formaciones con alta radioactividad

**Parámetros**:
- **Curva GR**: Seleccionar curva de Gamma Ray
- **GR min**: Valor de arena limpia (típico: 15 API)
- **GR max**: Valor de arcilla pura (típico: 150 API)

**Proceso**:
1. Seleccionar método y curva GR
2. Ajustar valores mínimo y máximo
3. Hacer clic en "🧮 Calcular VCL"
4. Revisar estadísticas en panel de resultados

#### Porosidad Efectiva (PHIE)

**Métodos disponibles**:
- **Density**: Solo desde RHOB
- **Neutron**: Solo desde NPHI
- **Combined**: Combinación densidad-neutrón

**Parámetros**:
- **ρma** (Densidad de matriz): 2.65 g/cc (cuarzo), 2.71 (caliza), 2.87 (dolomita)
- **ρfl** (Densidad de fluido): 1.00 g/cc (agua dulce), 1.10 (salmuera)

**Correcciones**:
- ☐ **Corrección de Arcilla**: Compensa efectos de arcilla (requiere VCL)
- ☐ **Corrección de Gas**: Compensa efectos de gas en formación

#### Análisis Litológico

**Función**: Identifica litología dominante y recomienda parámetros.

**Proceso**:
1. Requiere curvas RHOB y NPHI
2. Analiza correlación densidad-neutrón
3. Recomienda valores de ρma apropiados
4. Actualiza automáticamente parámetros en UI

### 🎨 Funciones de Visualización

#### Normalización de Curvas
Cuando se grafican curvas juntas, la aplicación pregunta:
- **Sí**: Normaliza todas las curvas entre 0-1 (recomendado para rangos diferentes)
- **No**: Mantiene valores originales

#### Personalización de Gráficos
- **Colores automáticos**: Paleta profesional de 8 colores
- **Estadísticas integradas**: N, Min, Max, Media en cada subplot
- **Rangos de profundidad comunes**: Alineación automática
- **Etiquetas con unidades**: Detecta automáticamente las unidades

#### Exportación de Gráficos
- **Formatos**: PNG (alta resolución), PDF (vectorial), SVG
- **Resolución**: 300 DPI automático
- **Nombre automático**: Basado en nombre del pozo y fecha

---

## 📚 Manual de la Librería

### Clase WellManager

La clase principal para manejar datos de pozos.

#### Carga de Datos

```python
from pypozo import WellManager

# Desde archivo LAS
well = WellManager.from_las("path/to/well.las")

# Desde DataFrame de pandas
import pandas as pd
df = pd.read_csv("well_data.csv", index_col=0)
well = WellManager.from_dataframe(df, name="MyWell")
```

#### Propiedades Principales

```python
# Información básica
print(well.name)                    # Nombre del pozo
print(well.depth_range)             # (min_depth, max_depth)
print(well.curves)                  # Lista de curvas disponibles
print(well.metadata)                # Metadatos del archivo LAS

# Acceso a datos
data = well.data                     # DataFrame con todas las curvas
curve = well.get_curve_data("GR")   # Serie de pandas para una curva
units = well.get_curve_units("GR")  # Unidades de la curva
```

#### Manipulación de Curvas

```python
# Agregar nueva curva
well.add_curve(
    curve_name="VCL",
    data=vcl_values,
    units="fraction",
    description="Volume of clay"
)

# Eliminar curva
well.remove_curve("OBSOLETE_CURVE")

# Renombrar curva
well.rename_curve("OLD_NAME", "NEW_NAME")

# Aplicar filtros
filtered_well = well.filter_depth(1500, 2000)  # Filtrar por profundidad
```

#### Exportación

```python
# Exportar a LAS
well.export_to_las("output.las")

# Exportar curvas específicas
well.export_to_las("output.las", curves=["GR", "RHOB", "NPHI", "VCL"])

# Exportar a CSV
well.data.to_csv("output.csv")
```

### Módulo de Petrofísica

#### VclCalculator

```python
from pypozo.petrophysics import VclCalculator

calc = VclCalculator()

# Cálculo básico
result = calc.calculate(
    gamma_ray=well.data["GR"],
    gr_clean=15,
    gr_clay=150,
    method="larionov_tertiary"
)

# Acceder a resultados
vcl = result['vcl']                  # Array de VCL
igr = result['igr']                  # Índice de Gamma Ray
params = result['parameters']        # Parámetros utilizados
qc_stats = result['qc_stats']       # Estadísticas de control de calidad
warnings = result['warnings']        # Advertencias del cálculo

# Métodos disponibles
methods = calc.get_method_info()
print(methods['available_methods'])  # ['linear', 'larionov_tertiary', ...]
```

#### PorosityCalculator

```python
from pypozo.petrophysics import PorosityCalculator

calc = PorosityCalculator()

# Porosidad desde densidad
result = calc.calculate_density_porosity(
    bulk_density=well.data["RHOB"],
    matrix_density=2.65,
    fluid_density=1.00
)
phid = result['phid']

# Porosidad desde neutrón
result = calc.calculate_neutron_porosity(
    neutron_porosity=well.data["NPHI"],
    lithology="sandstone"
)
phin = result['phin']

# Porosidad combinada
result = calc.calculate_density_neutron_porosity(
    bulk_density=well.data["RHOB"],
    neutron_porosity=well.data["NPHI"],
    matrix_density=2.65,
    fluid_density=1.00,
    combination_method="arithmetic"
)
phie = result['phie']
```

### Visualización con WellPlotter

```python
from pypozo import WellPlotter
import matplotlib.pyplot as plt

plotter = WellPlotter()

# Gráfico básico de curvas
fig, axes = plotter.plot_curves(
    well, 
    curves=["GR", "RHOB", "NPHI"],
    figsize=(12, 8)
)

# Gráfico de comparación entre pozos
fig, ax = plotter.compare_wells(
    wells=[well1, well2, well3],
    curve="GR",
    names=["Pozo A", "Pozo B", "Pozo C"]
)

# Crossplot densidad-neutrón
fig, ax = plotter.crossplot(
    well,
    x_curve="RHOB",
    y_curve="NPHI",
    color_curve="GR"
)

plt.show()
```

### Gestión de Proyectos

```python
from pypozo import ProjectManager

# Crear proyecto
project = ProjectManager("Mi_Proyecto_Petroleo")

# Agregar pozos
project.add_well(well1)
project.add_well(well2)

# Workflow automatizado
project.run_workflow([
    "load_wells",
    "calculate_vcl",
    "calculate_porosity",
    "generate_report"
])

# Guardar proyecto
project.save("proyecto.pypz")

# Cargar proyecto existente
project = ProjectManager.load("proyecto.pypz")
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Análisis Completo de Pozo

```python
from pypozo import WellManager
from pypozo.petrophysics import VclCalculator, PorosityCalculator

# 1. Cargar pozo
well = WellManager.from_las("ABEDUL-1.las")
print(f"Pozo cargado: {well.name}")
print(f"Curvas disponibles: {well.curves}")

# 2. Calcular VCL
vcl_calc = VclCalculator()
vcl_result = vcl_calc.calculate(
    gamma_ray=well.data["GR"],
    gr_clean=20,
    gr_clay=140,
    method="larionov_tertiary"
)

# Agregar VCL al pozo
well.add_curve("VCL", vcl_result['vcl'], units="fraction")

# 3. Calcular Porosidad
por_calc = PorosityCalculator()
por_result = por_calc.calculate_density_neutron_porosity(
    bulk_density=well.data["RHOB"],
    neutron_porosity=well.data["NPHI"],
    matrix_density=2.65,  # Arenisca
    fluid_density=1.00
)

# Agregar PHIE al pozo
well.add_curve("PHIE", por_result['phie'], units="fraction")

# 4. Generar reporte
print("\n=== REPORTE PETROFÍSICO ===")
print(f"VCL promedio: {vcl_result['vcl'].mean():.3f}")
print(f"VCL rango: {vcl_result['vcl'].min():.3f} - {vcl_result['vcl'].max():.3f}")
print(f"PHIE promedio: {por_result['phie'].mean():.3f}")
print(f"PHIE rango: {por_result['phie'].min():.3f} - {por_result['phie'].max():.3f}")

# 5. Exportar resultados
well.export_to_las("ABEDUL-1_processed.las")
```

### Ejemplo 2: Comparación de Pozos

```python
from pypozo import WellManager, WellPlotter
import matplotlib.pyplot as plt

# Cargar múltiples pozos
pozos = {}
archivos = ["ABEDUL-1.las", "ARIEL-1.las", "PALOBLANCO-791.las"]

for archivo in archivos:
    pozo = WellManager.from_las(archivo)
    pozos[pozo.name] = pozo

# Comparar curva GR
plotter = WellPlotter()
fig, ax = plotter.compare_wells(
    wells=list(pozos.values()),
    curve="GR",
    names=list(pozos.keys())
)

plt.title("Comparación de Gamma Ray")
plt.xlabel("GR (API)")
plt.ylabel("Profundidad (m)")
plt.legend()
plt.show()

# Estadísticas comparativas
print("=== ESTADÍSTICAS COMPARATIVAS ===")
for nombre, pozo in pozos.items():
    gr_data = pozo.get_curve_data("GR")
    print(f"{nombre}:")
    print(f"  GR promedio: {gr_data.mean():.1f} API")
    print(f"  GR rango: {gr_data.min():.1f} - {gr_data.max():.1f} API")
```

### Ejemplo 3: Workflow Automatizado

```python
from pypozo import WellManager, ProjectManager
from pypozo.petrophysics import VclCalculator, PorosityCalculator
import glob

def procesar_pozo_automatico(archivo_las):
    """Workflow automatizado para procesar un pozo."""
    
    # 1. Cargar
    well = WellManager.from_las(archivo_las)
    print(f"📁 Procesando: {well.name}")
    
    # 2. Validar curvas necesarias
    required_curves = ["GR", "RHOB", "NPHI"]
    missing = [c for c in required_curves if c not in well.curves]
    if missing:
        print(f"⚠️  Curvas faltantes: {missing}")
        return None
    
    # 3. Calcular VCL
    if "GR" in well.curves:
        vcl_calc = VclCalculator()
        vcl_result = vcl_calc.calculate(
            gamma_ray=well.data["GR"],
            gr_clean=15,
            gr_clay=150,
            method="larionov_tertiary"
        )
        well.add_curve("VCL", vcl_result['vcl'], units="fraction")
        print(f"✅ VCL calculado (promedio: {vcl_result['vcl'].mean():.3f})")
    
    # 4. Calcular Porosidad
    if all(c in well.curves for c in ["RHOB", "NPHI"]):
        por_calc = PorosityCalculator()
        por_result = por_calc.calculate_density_neutron_porosity(
            bulk_density=well.data["RHOB"],
            neutron_porosity=well.data["NPHI"],
            matrix_density=2.65,
            fluid_density=1.00
        )
        well.add_curve("PHIE", por_result['phie'], units="fraction")
        print(f"✅ PHIE calculado (promedio: {por_result['phie'].mean():.3f})")
    
    # 5. Exportar
    output_file = archivo_las.replace(".las", "_processed.las")
    well.export_to_las(output_file)
    print(f"💾 Exportado: {output_file}")
    
    return well

# Procesar todos los archivos LAS en un directorio
archivos_las = glob.glob("data/*.las")
pozos_procesados = []

for archivo in archivos_las:
    pozo = procesar_pozo_automatico(archivo)
    if pozo:
        pozos_procesados.append(pozo)

print(f"\n🎉 Procesamiento completado: {len(pozos_procesados)} pozos")
```

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### Error: "PyQt5 not found"
```bash
# Solución: Instalar PyQt5
pip install PyQt5
```

#### Error: "ModuleNotFoundError: No module named 'pypozo'"
```bash
# Solución: Instalar en modo desarrollo
pip install -e .
```

#### Error: "Cannot read LAS file"
- **Verificar formato**: El archivo debe ser LAS válido (versión 2.0 o superior)
- **Verificar encoding**: Probar con diferentes codificaciones (UTF-8, latin-1)
- **Verificar path**: Usar rutas absolutas si hay problemas con relativas

#### La aplicación GUI no inicia
1. Verificar instalación de PyQt5
2. Verificar permisos de ejecución
3. Revisar log de errores en consola

#### Cálculos petrofísicos dan valores extraños
- **Verificar parámetros**: GR_clean < GR_clay
- **Verificar unidades**: Densidad en g/cc, porosidad en fracción
- **Verificar datos de entrada**: Sin valores NaN o infinitos

### Logging y Debug

```python
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Activar logging en PyPozo
from pypozo import WellManager
well = WellManager.from_las("test.las", verbose=True)
```

### Optimización de Rendimiento

```python
# Para archivos grandes, usar chunking
well = WellManager.from_las("huge_file.las", chunk_size=10000)

# Filtrar datos innecesarios
well = well.filter_depth(1500, 2500)  # Solo intervalo de interés

# Usar solo curvas necesarias
essential_curves = ["GR", "RHOB", "NPHI", "RT"]
well = well.select_curves(essential_curves)
```

---

## 📖 Referencias

### Estándares de la Industria

- **LAS 2.0**: Log ASCII Standard Version 2.0 (CWLS)
- **API**: American Petroleum Institute standards
- **SPE**: Society of Petroleum Engineers publications

### Métodos Petrofísicos

- **Larionov (1969)**: "Borehole radiometry"
- **Clavier et al. (1971)**: "Theoretical and experimental bases for the dual-water model"
- **Steiber (1973)**: "Optimization of shale volumes in sand-shale sequences"

### Documentación Técnica

- **Cased & Serra**: "Cased Hole Log Interpretation Principles/Applications"
- **Schlumberger**: "Cased Hole Interpretation Charts"
- **Halliburton**: "Basic Well Log Analysis"

### Enlaces Útiles

- 📚 [Documentación completa](docs/)
- 🐛 [Reportar bugs](issues/)
- 💬 [Foro de usuarios](discussions/)
- 📧 [Contacto](mailto:support@pypozo.com)

---

## 🎓 Soporte y Comunidad

### Obtener Ayuda

1. **Documentación**: Revisar este manual y ejemplos
2. **Issues**: Reportar problemas en GitHub
3. **Discusiones**: Preguntas generales en el foro
4. **Email**: Soporte técnico directo

### Contribuir

- **Código**: Pull requests bienvenidos
- **Documentación**: Mejorar manuales y ejemplos
- **Testing**: Reportar bugs y casos de uso
- **Traducción**: Ayudar con internacionalización

### Roadmap

- 🔄 **v2.1**: Saturación de agua (SW) y permeabilidad
- 🔄 **v2.2**: Módulo de interpretación sísmica
- 🔄 **v2.3**: Machine Learning para predicción litológica
- 🔄 **v3.0**: Interfaz web y colaboración en la nube

---

**© 2025 PyPozo Project - Licencia MIT**

*Alternativa Open Source profesional para análisis de pozos petroleros*
