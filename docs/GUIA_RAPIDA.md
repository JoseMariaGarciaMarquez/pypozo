# Guía Rápida de Inicio - PyPozo 2.0

## 🚀 Primeros Pasos (5 minutos)

### 1. Ejecutar la Aplicación

```bash
# Navegar al directorio de PyPozo
cd c:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\pypozo

# Ejecutar la aplicación GUI
python pypozo_app.py
```

### 2. Cargar tu Primer Pozo

1. **Hacer clic** en "📂 Cargar Pozo"
2. **Seleccionar** un archivo `.las` (usar datos de ejemplo en `data/`)
3. **Esperar** que aparezca en el explorador izquierdo
4. **Hacer clic** en el pozo para seleccionarlo

### 3. Visualizar Curvas

1. **Ir** a la pestaña "📊 Curvas" (panel derecho)
2. **Hacer clic** en "📊 Básicas" para seleccionar curvas estándar
3. **Hacer clic** en "🎨 Graficar Seleccionadas"
4. **Ver** el resultado en el panel central

## 📊 Tutorial Básico: Análisis de Pozo

### Paso 1: Cargar Pozo de Ejemplo

```bash
# Usar uno de los pozos de ejemplo incluidos
data/ABEDUL-1_MERGED.las
data/ARIEL-1_MERGED.las
data/PALO BLANCO 791_PROCESADO.las
```

### Paso 2: Explorar Datos

1. **Seleccionar** el pozo cargado
2. **Revisar** propiedades en panel izquierdo:
   - Profundidad total
   - Número de curvas
   - Lista de curvas disponibles

### Paso 3: Visualización Básica

**Curvas básicas recomendadas:**
- **GR**: Gamma Ray (radioactividad natural)
- **RHOB**: Densidad volumétrica
- **NPHI**: Porosidad neutrón
- **RT**: Resistividad total

**Procedimiento:**
1. **Pestaña** "📊 Curvas"
2. **Botón** "📊 Básicas"
3. **Botón** "🎨 Graficar Seleccionadas"

### Paso 4: Cálculo de VCL (Volumen de Arcilla)

1. **Ir** a pestaña "🧪 Petrofísica"
2. **Sección VCL:**
   - Método: `larionov_tertiary` (recomendado)
   - Curva GR: seleccionar automáticamente
   - GR min: `15` (arena limpia)
   - GR max: `150` (arcilla pura)
3. **Hacer clic** "🧮 Calcular VCL"
4. **Revisar** resultados en panel inferior

### Paso 5: Cálculo de Porosidad

1. **Sección PHIE:**
   - Método: `combined` (densidad + neutrón)
   - RHOB: seleccionar automáticamente
   - NPHI: seleccionar automáticamente
   - ρma: `265` (cuarzo/arenisca)
   - ρfl: `100` (agua dulce)
2. **Opciones avanzadas:**
   - ☑️ **Corrección de arcilla**: Si hay curva VCL calculada
   - ☑️ **Corrección de gas**: Para detectar efectos de hidrocarburos
3. **Hacer clic** "🧮 Calcular PHIE"
4. **Revisar** estadísticas generadas

### Paso 5b: Análisis Litológico (NUEVO ✨)

1. **Hacer clic** "🪨 Análisis Litológico"
2. **Revisar** recomendaciones automáticas:
   - Litología dominante detectada
   - Densidad de matriz recomendada
   - Distribución litológica estimada
3. **Aplicar** parámetros sugeridos en cálculos

### Paso 6: Visualizar Resultados

1. **Hacer clic** "📈 Graficar Resultados" (en pestaña Petrofísica)
2. **Alternativamente:**
   - Ir a pestaña "📊 Curvas"
   - Seleccionar "VCL_LARIONOV_TERTIARY" y "PHIE_COMBINED"
   - Graficar normalmente

## 🔧 Ejemplo con Código (Librería)

```python
# Script básico para análisis automatizado
from pypozo import WellManager
from pypozo.petrophysics import VclCalculator, PorosityCalculator

# 1. Cargar pozo
well = WellManager.from_las("data/ABEDUL-1_MERGED.las")
print(f"✅ Pozo cargado: {well.name}")
print(f"📏 Profundidad: {well.depth_range[0]:.0f} - {well.depth_range[1]:.0f} m")
print(f"📊 Curvas: {len(well.curves)}")

# 2. Calcular VCL
vcl_calc = VclCalculator()
vcl_result = vcl_calc.calculate(
    gamma_ray=well.data["GR"],
    gr_clean=15,
    gr_clay=150,
    method="larionov_tertiary"
)

# Agregar al pozo
well.add_curve("VCL", vcl_result['vcl'], units="fraction")
print(f"🏔️ VCL promedio: {vcl_result['vcl'].mean():.3f}")

# 3. Calcular Porosidad
por_calc = PorosityCalculator()
por_result = por_calc.calculate_density_neutron_porosity(
    bulk_density=well.data["RHOB"],
    neutron_porosity=well.data["NPHI"],
    matrix_density=2.65,
    fluid_density=1.00
)

# Agregar al pozo
well.add_curve("PHIE", por_result['phie'], units="fraction")
print(f"🕳️ PHIE promedio: {por_result['phie'].mean():.3f}")

# 4. Exportar
well.export_to_las("ABEDUL-1_procesado.las")
print("💾 Archivo exportado exitosamente")
```

## 🎯 Flujo de Trabajo Típico

### Para Análisis Individual

1. **Cargar** → 2. **Visualizar** → 3. **Calcular VCL** → 4. **Calcular PHIE** → 5. **Exportar**

### Para Comparación de Pozos

1. **Cargar múltiples pozos** ("📁 Cargar Múltiples")
2. **Pestaña "⚖️ Comparar"**
3. **Seleccionar pozos** y curva de interés
4. **"⚖️ Comparar Seleccionados"**

### Para Workflow Automatizado

```python
# Procesar múltiples pozos automáticamente
import glob
from pathlib import Path

archivos = glob.glob("data/*.las")
for archivo in archivos:
    well = WellManager.from_las(archivo)
    
    # Calcular VCL si hay GR
    if "GR" in well.curves:
        vcl_calc = VclCalculator()
        result = vcl_calc.calculate(well.data["GR"], 15, 150)
        well.add_curve("VCL", result['vcl'])
    
    # Exportar con sufijo _processed
    output = archivo.replace(".las", "_processed.las")
    well.export_to_las(output)
    print(f"✅ Procesado: {Path(archivo).name}")
```

## 🐛 Solución Rápida de Problemas

**Error al cargar archivo:**
- Verificar que es formato `.las` válido
- Probar con archivos de ejemplo en `data/`

**No aparecen curvas:**
- Hacer clic en el pozo en el explorador izquierdo
- Verificar que el archivo LAS tiene datos

**Cálculos dan error:**
- Verificar que existen las curvas necesarias (GR, RHOB, NPHI)
- Ajustar parámetros GR_min < GR_max

**Aplicación no inicia:**
```bash
pip install PyQt5
pip install -e .
```

## 📚 Siguiente Paso

Una vez que domines estos básicos, consulta el **Manual Completo** en `docs/MANUAL_USUARIO.md` para:

- Funciones avanzadas de visualización
- Métodos petrofísicos adicionales
- Automatización con scripts
- Configuración de proyectos complejos

## 💡 Consejos Útiles

1. **Usa archivos de ejemplo** en `data/` para practicar
2. **El panel de actividades** (pestaña Análisis) muestra todas las operaciones
3. **Normalización opcional** al graficar curvas juntas es muy útil
4. **Exporta frecuentemente** para guardar tu trabajo
5. **Los cálculos se agregan como nuevas curvas** al pozo

---

**🎉 ¡Listo para comenzar! En 5 minutos ya estarás analizando pozos como un profesional.**
