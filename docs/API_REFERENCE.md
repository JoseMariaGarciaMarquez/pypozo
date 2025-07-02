# API Reference - PyPozo Library

## 📚 Documentación de la API

### Módulos Principales

- `pypozo.core.well` - Gestión de datos de pozos
- `pypozo.core.plotter` - Visualización de registros
- `pypozo.core.project` - Gestión de proyectos
- `pypozo.petrophysics` - Cálculos petrofísicos

---

## 🏗️ pypozo.core.well

### WellManager

Clase principal para manejar datos de pozos petroleros.

```python
from pypozo import WellManager
```

#### Constructor

```python
WellManager(name: str, data: pd.DataFrame, metadata: dict = None)
```

**Parámetros:**
- `name`: Nombre del pozo
- `data`: DataFrame con datos de curvas (índice = profundidad)
- `metadata`: Diccionario con metadatos opcionales

#### Métodos de Clase

##### from_las()

```python
@classmethod
WellManager.from_las(file_path: str, encoding: str = 'utf-8') -> WellManager
```

Carga un pozo desde archivo LAS.

**Parámetros:**
- `file_path`: Ruta al archivo LAS
- `encoding`: Codificación del archivo (default: 'utf-8')

**Retorna:** Instancia de WellManager

**Ejemplo:**
```python
well = WellManager.from_las("mi_pozo.las")
```

##### from_dataframe()

```python
@classmethod
WellManager.from_dataframe(df: pd.DataFrame, name: str, metadata: dict = None) -> WellManager
```

Crea un pozo desde DataFrame de pandas.

**Ejemplo:**
```python
import pandas as pd
df = pd.read_csv("datos.csv", index_col=0)
well = WellManager.from_dataframe(df, "Pozo_Test")
```

#### Propiedades

##### name

```python
@property
def name(self) -> str
```

Nombre del pozo.

##### depth_range

```python
@property
def depth_range(self) -> Tuple[float, float]
```

Rango de profundidad (min, max) en metros.

##### curves

```python
@property
def curves(self) -> List[str]
```

Lista de nombres de curvas disponibles.

##### data

```python
@property
def data(self) -> WellDataFrame
```

Wrapper DataFrame-like para acceso a datos de curvas.

##### metadata

```python
@property
def metadata(self) -> dict
```

Diccionario con metadatos del pozo.

#### Métodos de Instancia

##### get_curve_data()

```python
def get_curve_data(self, curve_name: str) -> Optional[pd.Series]
```

Obtiene datos de una curva específica.

**Parámetros:**
- `curve_name`: Nombre de la curva

**Retorna:** Serie de pandas con los datos (índice = profundidad)

**Ejemplo:**
```python
gr_data = well.get_curve_data("GR")
print(f"GR promedio: {gr_data.mean():.2f}")
```

##### get_curve_units()

```python
def get_curve_units(self, curve_name: str) -> str
```

Obtiene las unidades de una curva.

**Parámetros:**
- `curve_name`: Nombre de la curva

**Retorna:** String con las unidades

##### add_curve()

```python
def add_curve(self, curve_name: str, data: Union[np.ndarray, pd.Series], 
              units: str = "", description: str = "") -> bool
```

Agrega una nueva curva al pozo.

**Parámetros:**
- `curve_name`: Nombre de la nueva curva
- `data`: Datos de la curva (mismo índice que pozo)
- `units`: Unidades de la curva
- `description`: Descripción opcional

**Retorna:** True si se agregó exitosamente

**Ejemplo:**
```python
import numpy as np
vcl_data = np.random.rand(len(well.data))
success = well.add_curve("VCL_TEST", vcl_data, "fraction", "Test VCL curve")
```

##### remove_curve()

```python
def remove_curve(self, curve_name: str) -> bool
```

Elimina una curva del pozo.

##### filter_depth()

```python
def filter_depth(self, min_depth: float, max_depth: float) -> 'WellManager'
```

Filtra el pozo por rango de profundidad.

**Ejemplo:**
```python
well_filtered = well.filter_depth(1500, 2000)
```

##### export_to_las()

```python
def export_to_las(self, file_path: str, curves: List[str] = None) -> bool
```

Exporta el pozo a archivo LAS.

**Parámetros:**
- `file_path`: Ruta del archivo de salida
- `curves`: Lista de curvas a exportar (None = todas)

---

## 📊 pypozo.core.plotter

### WellPlotter

Clase para visualización de registros de pozos.

```python
from pypozo import WellPlotter
```

#### Constructor

```python
WellPlotter(style: str = 'professional', figsize: Tuple[int, int] = (12, 8))
```

#### Métodos

##### plot_curves()

```python
def plot_curves(self, well: WellManager, curves: List[str], 
                figsize: Tuple[int, int] = None) -> Tuple[plt.Figure, List[plt.Axes]]
```

Grafica múltiples curvas en subplots separados.

**Ejemplo:**
```python
plotter = WellPlotter()
fig, axes = plotter.plot_curves(well, ["GR", "RHOB", "NPHI"])
plt.show()
```

##### compare_wells()

```python
def compare_wells(self, wells: List[WellManager], curve: str, 
                  names: List[str] = None) -> Tuple[plt.Figure, plt.Axes]
```

Compara la misma curva entre múltiples pozos.

**Ejemplo:**
```python
fig, ax = plotter.compare_wells([well1, well2], "GR", ["Pozo A", "Pozo B"])
```

##### crossplot()

```python
def crossplot(self, well: WellManager, x_curve: str, y_curve: str,
              color_curve: str = None) -> Tuple[plt.Figure, plt.Axes]
```

Crea un crossplot entre dos curvas.

**Ejemplo:**
```python
fig, ax = plotter.crossplot(well, "RHOB", "NPHI", color_curve="GR")
```

---

## 🧪 pypozo.petrophysics

### VclCalculator

Calculadora de Volumen de Arcilla desde Gamma Ray.

```python
from pypozo.petrophysics import VclCalculator
```

#### Constructor

```python
VclCalculator()
```

#### Métodos

##### calculate()

```python
def calculate(self, gamma_ray: Union[np.ndarray, List[float]],
              gr_clean: float = None, gr_clay: float = None,
              method: str = 'larionov_tertiary',
              auto_percentiles: bool = True,
              percentiles: tuple = (5, 95)) -> Dict
```

Calcula volumen de arcilla desde Gamma Ray.

**Parámetros:**
- `gamma_ray`: Valores de Gamma Ray [API]
- `gr_clean`: GR de arena limpia [API]
- `gr_clay`: GR de arcilla pura [API]
- `method`: Método de cálculo ('linear', 'larionov_older', 'larionov_tertiary', 'clavier', 'steiber')
- `auto_percentiles`: Si calcular GR_clean/clay automáticamente
- `percentiles`: Percentiles para cálculo automático

**Retorna:** Diccionario con resultados:
```python
{
    'vcl': np.ndarray,          # Valores de VCL [0-1]
    'igr': np.ndarray,          # Índice Gamma Ray [0-1]
    'parameters': dict,         # Parámetros utilizados
    'qc_stats': dict,          # Estadísticas QC
    'warnings': list,          # Advertencias
    'quality_flags': dict      # Flags de calidad
}
```

**Ejemplo:**
```python
calc = VclCalculator()
result = calc.calculate(
    gamma_ray=well.data["GR"],
    gr_clean=15,
    gr_clay=150,
    method="larionov_tertiary"
)

vcl = result['vcl']
print(f"VCL promedio: {vcl.mean():.3f}")
```

##### get_method_info()

```python
def get_method_info(self) -> Dict
```

Obtiene información sobre métodos disponibles.

**Retorna:**
```python
{
    'available_methods': list,
    'descriptions': dict,
    'recommendations': dict
}
```

### PorosityCalculator

Calculadora de Porosidad Efectiva.

```python
from pypozo.petrophysics import PorosityCalculator
```

#### Métodos

##### calculate_density_porosity()

```python
def calculate_density_porosity(self, bulk_density: Union[np.ndarray, List[float]],
                             matrix_density: float = 2.65,
                             fluid_density: float = 1.00,
                             vcl: Optional[Union[np.ndarray, List[float]]] = None) -> Dict
```

Calcula porosidad desde densidad volumétrica.

**Fórmula:** `PHID = (RHOMA - RHOB) / (RHOMA - RHOF)`

**Parámetros:**
- `bulk_density`: Densidad volumétrica [g/cm³]
- `matrix_density`: Densidad de matriz [g/cm³]
- `fluid_density`: Densidad del fluido [g/cm³]
- `vcl`: Volumen de arcilla para corrección [fracción]

**Retorna:** Diccionario con 'phid', 'parameters', 'qc_stats', etc.

##### calculate_neutron_porosity()

```python
def calculate_neutron_porosity(self, neutron_porosity: Union[np.ndarray, List[float]],
                             vcl: Optional[Union[np.ndarray, List[float]]] = None,
                             lithology: str = 'sandstone') -> Dict
```

Calcula porosidad corregida desde neutrón.

**Parámetros:**
- `neutron_porosity`: Porosidad neutrón aparente [fracción]
- `vcl`: Volumen de arcilla [fracción]
- `lithology`: Tipo de litología ('sandstone', 'limestone', 'dolomite')

##### calculate_density_neutron_porosity()

```python
def calculate_density_neutron_porosity(self, bulk_density: Union[np.ndarray, List[float]],
                                     neutron_porosity: Union[np.ndarray, List[float]],
                                     matrix_density: float = 2.65,
                                     fluid_density: float = 1.00,
                                     vcl: Optional[Union[np.ndarray, List[float]]] = None,
                                     lithology: str = 'sandstone',
                                     combination_method: str = 'arithmetic') -> Dict
```

Calcula porosidad efectiva combinando densidad y neutrón.

**Parámetros:**
- `combination_method`: 'arithmetic', 'geometric', 'harmonic'

**Ejemplo completo:**
```python
por_calc = PorosityCalculator()

# Porosidad desde densidad
result_den = por_calc.calculate_density_porosity(
    bulk_density=well.data["RHOB"],
    matrix_density=2.65,  # Arenisca
    fluid_density=1.00    # Agua
)

# Porosidad combinada
result_comb = por_calc.calculate_density_neutron_porosity(
    bulk_density=well.data["RHOB"],
    neutron_porosity=well.data["NPHI"],
    matrix_density=2.65,
    combination_method="arithmetic"
)

phie = result_comb['phie']
well.add_curve("PHIE", phie, "fraction")
```

##### apply_clay_correction() ✨

```python
def apply_clay_correction(self, porosity_result: Dict,
                        vcl: Union[np.ndarray, List[float]],
                        clay_porosity_density: float = 0.40,
                        clay_porosity_neutron: float = 0.45) -> Dict
```

Aplica corrección por arcilla usando el modelo Thomas-Stieber.

**Parámetros:**
- `porosity_result`: Resultado de cálculo de porosidad
- `vcl`: Volumen de arcilla [fracción]
- `clay_porosity_density`: Porosidad aparente de arcilla en densidad
- `clay_porosity_neutron`: Porosidad aparente de arcilla en neutrón

**Retorna:** Diccionario con resultados corregidos

**Ejemplo:**
```python
# Calcular porosidad base
base_result = por_calc.calculate_density_porosity(rhob_data)

# Aplicar corrección por arcilla
corrected_result = por_calc.apply_clay_correction(base_result, vcl_data)

# Usar resultado corregido
phie_corrected = corrected_result['porosity_corrected']
```

##### apply_gas_correction() ✨

```python
def apply_gas_correction(self, porosity_result: Dict,
                       gas_correction_factor: float = 0.15) -> Dict
```

Aplica corrección básica por efectos de gas.

**Parámetros:**
- `porosity_result`: Resultado de cálculo de porosidad
- `gas_correction_factor`: Factor de corrección [fracción]

**Retorna:** Diccionario con corrección aplicada

**Detección automática:** Identifica zonas con posible gas usando separación PHID-PHIN.

##### get_lithology_recommendations() ✨

```python
def get_lithology_recommendations(self, phid: np.ndarray, phin: np.ndarray) -> Dict
```

Analiza litología automáticamente desde registros de porosidad.

**Parámetros:**
- `phid`: Porosidad densidad [fracción]
- `phin`: Porosidad neutrón [fracción]

**Retorna:** Diccionario con análisis litológico:
```python
{
    'dominant_lithology': str,           # Litología dominante
    'confidence': float,                 # Confianza del análisis
    'lithology_distribution': dict,      # Distribución porcentual
    'recommended_matrix_density': float, # Densidad de matriz sugerida
    'recommendations': list              # Lista de recomendaciones
}
```

**Ejemplo:**
```python
# Análisis litológico automático
litho_analysis = por_calc.get_lithology_recommendations(phid, phin)

print(f"Litología: {litho_analysis['dominant_lithology']}")
print(f"Confianza: {litho_analysis['confidence']:.1%}")
print(f"ρma recomendada: {litho_analysis['recommended_matrix_density']:.2f} g/cc")

# Usar densidad recomendada en cálculos
matrix_density = litho_analysis['recommended_matrix_density']
improved_result = por_calc.calculate_density_porosity(
    bulk_density=rhob_data,
    matrix_density=matrix_density
)
```

---

## 🗂️ pypozo.core.project

### ProjectManager

Gestor de proyectos multi-pozo.

```python
from pypozo import ProjectManager
```

#### Constructor

```python
ProjectManager(project_name: str = "Untitled Project")
```

#### Métodos

##### add_well()

```python
def add_well(self, well: WellManager) -> bool
```

##### remove_well()

```python
def remove_well(self, well_name: str) -> bool
```

##### get_well()

```python
def get_well(self, well_name: str) -> Optional[WellManager]
```

##### list_wells()

```python
def list_wells(self) -> List[str]
```

##### save()

```python
def save(self, file_path: str) -> bool
```

##### load()

```python
@classmethod
def load(cls, file_path: str) -> 'ProjectManager'
```

**Ejemplo de uso:**
```python
# Crear proyecto
project = ProjectManager("Campo_Norte")

# Agregar pozos
well1 = WellManager.from_las("pozo1.las")
well2 = WellManager.from_las("pozo2.las")
project.add_well(well1)
project.add_well(well2)

# Procesar todos los pozos
for well_name in project.list_wells():
    well = project.get_well(well_name)
    # Aplicar cálculos petrofísicos...

# Guardar proyecto
project.save("mi_proyecto.pypz")
```

---

## 🔧 Utilidades y Helpers

### Validación de Datos

```python
from pypozo.utils import validate_curve_data

# Validar datos de curva
is_valid, message = validate_curve_data(curve_data, "GR", (0, 1000))
if not is_valid:
    print(f"Error: {message}")
```

### Conversión de Unidades

```python
from pypozo.utils import convert_units

# Convertir unidades
api_to_gapi = convert_units(gr_values, "API", "GAPI")
feet_to_meters = convert_units(depth_values, "FT", "M")
```

### Estadísticas QC

```python
from pypozo.utils import calculate_qc_stats

stats = calculate_qc_stats(curve_data, "GR")
print(f"Media: {stats['mean']:.2f}")
print(f"Outliers: {stats['outlier_count']}")
```

---

## 🎯 Ejemplos de Workflows

### Workflow Básico

```python
from pypozo import WellManager
from pypozo.petrophysics import VclCalculator, PorosityCalculator

def process_well_basic(las_file):
    # Cargar
    well = WellManager.from_las(las_file)
    
    # VCL
    if "GR" in well.curves:
        vcl_calc = VclCalculator()
        result = vcl_calc.calculate(well.data["GR"], 15, 150)
        well.add_curve("VCL", result['vcl'], "fraction")
    
    # Porosidad
    if all(c in well.curves for c in ["RHOB", "NPHI"]):
        por_calc = PorosityCalculator()
        result = por_calc.calculate_density_neutron_porosity(
            well.data["RHOB"], well.data["NPHI"], 2.65, 1.00
        )
        well.add_curve("PHIE", result['phie'], "fraction")
    
    return well
```

### Workflow Avanzado con QC

```python
def process_well_advanced(las_file):
    well = WellManager.from_las(las_file)
    
    # QC de datos
    required_curves = ["GR", "RHOB", "NPHI"]
    missing = [c for c in required_curves if c not in well.curves]
    if missing:
        raise ValueError(f"Curvas faltantes: {missing}")
    
    # Validar rangos
    gr_data = well.get_curve_data("GR")
    if gr_data.max() > 1000 or gr_data.min() < 0:
        print("⚠️ Valores de GR fuera de rango normal")
    
    # Cálculos con parámetros automáticos
    vcl_calc = VclCalculator()
    vcl_result = vcl_calc.calculate(
        gr_data, 
        auto_percentiles=True,
        percentiles=(10, 90)  # Más conservador
    )
    
    # Verificar calidad del cálculo
    if vcl_result['warnings']:
        for warning in vcl_result['warnings']:
            print(f"⚠️ {warning}")
    
    well.add_curve("VCL", vcl_result['vcl'], "fraction")
    
    return well
```

---

## 📊 Constantes y Enumeraciones

### Litologías Estándar

```python
LITHOLOGY_DENSITIES = {
    'sandstone': 2.65,
    'limestone': 2.71,
    'dolomite': 2.87,
    'anhydrite': 2.98,
    'halite': 2.16,
    'coal': 1.30
}
```

### Métodos VCL

```python
VCL_METHODS = [
    'linear',
    'larionov_older',
    'larionov_tertiary',
    'clavier',
    'steiber'
]
```

### Unidades Comunes

```python
COMMON_UNITS = {
    'GR': 'API',
    'RHOB': 'g/cm3',
    'NPHI': 'fraction',
    'RT': 'ohmm',
    'DEPTH': 'm'
}
```

---

**Esta documentación de API cubre los aspectos principales de la librería PyPozo. Para ejemplos más específicos, consultar los notebooks en `examples/` y el manual de usuario completo.**
