# PyPozo 2.0 - Sistema Profesional de Análisis de Pozos

![PyPozo Logo](https://img.shields.io/badge/PyPozo-2.0-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![GUI](https://img.shields.io/badge/GUI-PyQt5-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Alternativa Open Source profesional a WellCAD** para el análisis, visualización y procesamiento de registros geofísicos de pozos.

## 🚀 Características Principales

### 🖥️ **Interfaz Gráfica Profesional**
- **GUI moderna con PyQt5** - Interfaz intuitiva y profesional
- **Visualización interactiva** - Gráficos de alta calidad con matplotlib
- **Manejo multi-pozo** - Carga y comparación de múltiples pozos
- **Selección flexible de curvas** - Presets inteligentes (básicas, petrofísicas, acústicas)
- **Exportación avanzada** - PNG, PDF, SVG, CSV, Excel

### 📊 **Análisis Avanzado**
- **Procesamiento con Welly** - Backend robusto y confiable
- **Estandarización automática** - Normalización de curvas
- **Calculadora geofísica** - Cálculos petrofísicos automatizados  
- **Workflows personalizables** - Procesamiento por lotes
- **Validación inteligente** - Control de calidad automático

### 🔧 **Capacidades Técnicas**
- **Carga de archivos LAS** - Soporte completo para estándares LAS
- **Visualización profesional** - Gráficos estilo WellCAD
- **Comparación multi-pozo** - Análisis comparativo avanzado
- **Integración GIS** - Exportación para sistemas GIS
- **API extensible** - Fácil integración con otros sistemas

## 📋 Instalación Rápida

### Opción 1: Con GUI (Recomendado)
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/pypozo.git
cd pypozo

# Instalar dependencias
pip install PyQt5 matplotlib numpy pandas welly lasio openpyxl

# Ejecutar aplicación GUI
python pypozo_app.py
```

### Opción 2: Solo backend
```bash
# Instalar dependencias mínimas
pip install numpy pandas matplotlib welly lasio

# Usar desde Python
python -c "from src.pypozo import WellManager; print('PyPozo listo!')"
```

## 🎯 Uso de la GUI

### Inicio Rápido
1. **Ejecutar**: `python pypozo_app.py`
2. **Cargar pozo**: Archivo → Abrir Pozo (o Ctrl+O)
3. **Seleccionar curvas**: Panel derecho → Tab "Curvas"
4. **Visualizar**: Click en "Graficar Seleccionadas"
5. **Exportar**: Archivo → Guardar Gráfico

### Lanzador con Ejemplos
```bash
# Lanzar con carga automática de pozos de ejemplo
python launch_pypozo.py
```

### Funcionalidades Principales

#### 📂 **Explorador de Pozos**
- Cargar pozos individuales o múltiples
- Vista en árbol de pozos cargados
- Propiedades detalladas de cada pozo
- Remoción selectiva de pozos

#### 📈 **Visualización Avanzada**
- Gráficos profesionales estilo WellCAD
- Selección inteligente de curvas:
  - ✅ **Básicas**: GR, SP, CAL, RT, RHOB, NPHI
  - 🔬 **Petrofísicas**: VCL, PHIE, SW, ZDEN, VSH
  - 🔊 **Acústicas**: DTC, DTS, VPVS, POISDIN
- Estadísticas automáticas en gráficos
- Eje Y invertido (profundidad hacia abajo)

#### ⚖️ **Comparación Multi-Pozo**
- Comparar hasta 7 pozos simultáneamente
- Selección de curva específica para comparación
- Colores diferenciados automáticamente
- Leyenda profesional

#### 🔬 **Análisis Rápido**
- Identificación automática de curvas principales
- Estadísticas básicas del pozo
- Detección de intervalos de interés
- Generación de reportes

## 💻 Uso Programático

### Ejemplo Básico
```python
from pypozo import WellManager, WellPlotter

# Cargar pozo
well = WellManager.from_las("mi_pozo.las")

# Información básica
print(f"Pozo: {well.name}")
print(f"Curvas: {well.curves}")
print(f"Profundidad: {well.depth_range}")

# Visualizar
plotter = WellPlotter()
plotter.plot_selected_curves(well, ["GR", "RT", "RHOB"])
```

### Ejemplo Avanzado
```python
from pypozo import ProjectManager, StandardWorkflow

# Crear proyecto multi-pozo
project = ProjectManager()
project.add_well("pozo1.las")
project.add_well("pozo2.las")

# Ejecutar workflow
workflow = StandardWorkflow()
results = workflow.process_project(project)

# Comparar pozos
project.compare_wells(["Pozo1", "Pozo2"], curve="GR")
```

## 🏗️ Arquitectura

```
pypozo/
├── src/pypozo/
│   ├── core/           # Clases principales
│   │   ├── well.py     # WellManager
│   │   └── project.py  # ProjectManager
│   ├── processors/     # Procesamiento
│   │   ├── standardizer.py
│   │   └── calculator.py
│   ├── visualization/  # Visualización
│   │   └── plotter.py  # WellPlotter
│   ├── workflows/      # Workflows
│   │   └── standard.py
│   ├── gui/           # Interfaz gráfica
│   │   └── main_window.py
│   └── utils/         # Utilidades
├── data/              # Datos de ejemplo
├── tests/             # Pruebas
├── pypozo_app.py      # Aplicación GUI principal
└── launch_pypozo.py   # Lanzador con ejemplos
```

## 🔧 Desarrollo

### Configurar Entorno
```bash
git clone https://github.com/tu-usuario/pypozo.git
cd pypozo

# Entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar en modo desarrollo
pip install -e .
```

### Ejecutar Pruebas
```bash
# Pruebas del backend
python tests/pruebas.py

# Pruebas de visualización
python test_visualizacion.py

# Pruebas de GUI
python test_gui.py
```

## 📊 Formatos Soportados

- **Entrada**: LAS 2.0/3.0, ASCII personalizado
- **Salida**: PNG, PDF, SVG, CSV, Excel, LAS
- **Integración**: GIS (Shapefile, GeoJSON), JSON, XML

## 🆚 Comparación con WellCAD

| Característica | PyPozo 2.0 | WellCAD |
|---|---|---|
| **Precio** | ✅ Gratis/Open Source | ❌ Licencia comercial |
| **Visualización** | ✅ Profesional | ✅ Profesional |
| **Multi-pozo** | ✅ Ilimitado | ❌ Limitado |
| **Personalización** | ✅ Código abierto | ❌ Cerrado |
| **Análisis** | ✅ Avanzado | ✅ Avanzado |
| **Integración** | ✅ API Python | ❌ Limitada |
| **Workflows** | ✅ Programables | ❌ GUI únicamente |

## 🛠️ Dependencias

### Principales
- **welly**: Backend de pozos
- **matplotlib**: Visualización
- **pandas**: Manipulación de datos
- **numpy**: Cómputo numérico

### GUI
- **PyQt5**: Interfaz gráfica
- **matplotlib**: Integración con Qt

### Opcionales
- **openpyxl**: Exportación Excel
- **geopandas**: Integración GIS

## 📖 Documentación

- **API Reference**: Ver docstrings en código
- **Ejemplos**: Carpeta `examples/`
- **Tutoriales**: Notebooks en `notebooks/`

## 🤝 Contribuir

1. Fork del repositorio
2. Crear feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📜 Licencia

MIT License - ver archivo [LICENSE](LICENSE)

## 👨‍💻 Autor

**José María García Márquez**
- 📧 josemariagarciamarquez2.72@gmail.com
- 🐙 GitHub: [JoseMariaGarciaMarquez](https://github.com/JoseMariaGarciaMarquez)

## 🎯 Roadmap

### Versión 2.1
- [ ] Integración con bases de datos
- [ ] Plugins personalizables
- [ ] Análisis de machine learning
- [ ] API REST

### Versión 2.2
- [ ] Visualización 3D
- [ ] Soporte para más formatos
- [ ] Colaboración en tiempo real
- [ ] Aplicación web

---

**⭐ Si PyPozo te resulta útil, ¡dale una estrella en GitHub!**

*PyPozo 2.0 - Democratizando el análisis profesional de pozos*
