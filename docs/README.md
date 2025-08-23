# � Documentación PyPozo

Centro de documentación completo para PyPozo - Software profesional de análisis de pozos petroleros.

## 🎯 Inicio Rápido

### Para Usuarios Nuevos
- **[Guía Rápida](GUIA_RAPIDA.md)** - Inicio en 5 minutos
- **[Manual de Usuario](MANUAL_USUARIO.md)** - Tutorial completo paso a paso

### Para Desarrolladores  
- **[API Reference](API_REFERENCE.md)** - Documentación técnica completa
- **[Guía de Desarrollo](DEVELOPMENT.md)** - Configuración del entorno de desarrollo
- **[Contribuir](CONTRIBUTING.md)** - Cómo contribuir al proyecto

## 📖 Documentación Completa

### Manuales de Usuario
- **[Manual de Usuario](MANUAL_USUARIO.md)** - Guía completa de la aplicación GUI
- **[Guía Rápida](GUIA_RAPIDA.md)** - Tutorial de 5 minutos para empezar

### Documentación Técnica
- **[API Reference](API_REFERENCE.md)** - Documentación completa de la API
- **[Desarrollo](DEVELOPMENT.md)** - Guía para desarrolladores
- **[Arquitectura](SETUP_COMPLETE.md)** - Documentación de la arquitectura del sistema

### Guías Específicas
- **[Mejoras Geológicas](IMPLEMENTACION_MEJORAS_GEOLOGICAS_COMPLETA.md)** - Análisis petrofísico avanzado  
- **[Sistema Pozo Inteligente](IMPLEMENTACION_SISTEMA_POZO_INTELIGENTE.md)** - Funciones de IA
- **[Mejoras Neural](MEJORAS_NEURAL_COMPLETION.md)** - Machine Learning aplicado

### Comunidad y Soporte
- **[Soporte](SUPPORT_PYPOZO.md)** - Formas de apoyar el proyecto
- **[Contribuidores](CONTRIBUTORS.md)** - Reconocimientos a colaboradores
- **[Código de Conducta](CODE_OF_CONDUCT.md)** - Normas de la comunidad
- **[Seguridad](SECURITY.md)** - Políticas de seguridad

## 🚀 Enlaces Rápidos

- [Repositorio GitHub](https://github.com/JoseMariaGarciaMarquez/pypozo)
- [Reportar Issues](https://github.com/JoseMariaGarciaMarquez/pypozo/issues)
- [Buy Me a Coffee](https://buymeacoffee.com/ingjoma) ☕

---

**¿Necesitas ayuda?** Consulta primero la [Guía Rápida](GUIA_RAPIDA.md) o el [Manual de Usuario](MANUAL_USUARIO.md).

1. **[🛠️ API Reference](API_REFERENCE.md)**
   - Documentación técnica completa
   - Referencia de todas las clases y métodos
   - Ejemplos de código avanzados

2. **[💡 Mejores Prácticas](#mejores-prácticas)** *(esta página)*
   - Workflows recomendados
   - Optimización de rendimiento
   - Casos de uso comunes

---

## 📂 Documentación Disponible

### 📖 **Manuales Principales**

| Documento | Propósito | Audiencia | Tiempo |
|-----------|-----------|-----------|---------|
| [📋 Guía Rápida](GUIA_RAPIDA.md) | Inicio inmediato | Todos | 5 min |
| [📚 Manual de Usuario](MANUAL_USUARIO.md) | Guía completa | Usuarios finales | 30 min |
| [🛠️ API Reference](API_REFERENCE.md) | Referencia técnica | Desarrolladores | Consulta |

### 📋 **Documentación de Desarrollo**

| Documento | Contenido |
|-----------|-----------|
| [✅ PyPozo 2.0 Completado](PYPOZO_2.0_COMPLETADO.md) | Estado del proyecto |
| [🔧 Funcionalidades Completadas](FUNCIONALIDADES_COMPLETADAS.md) | Lista de características |
| [🔗 Funcionalidades de Fusión](FUNCIONALIDADES_FUSION.md) | Fusión de pozos |
| [📊 Visualización Corregida](VISUALIZATION_FIXES_COMPLETADO.md) | Mejoras gráficas |

---

## 🎓 Rutas de Aprendizaje

### 🎯 **Ruta 1: Usuario Casual** *(1 hora)*
*Para usuarios que quieren analizar pozos ocasionalmente*

```
1. Guía Rápida (5 min) 
   ↓
2. Sección "Uso de la Aplicación GUI" del Manual (15 min)
   ↓
3. Práctica con archivos de ejemplo (30 min)
   ↓
4. Sección "Solución de Problemas" (10 min)
```

### 🏭 **Ruta 2: Usuario Profesional** *(3 horas)*
*Para ingenieros que usarán PyPozo regularmente*

```
1. Manual de Usuario completo (45 min)
   ↓
2. Práctica con casos reales (60 min)
   ↓
3. Workflows automatizados básicos (30 min)
   ↓
4. API Reference - secciones básicas (45 min)
```

### 👨‍💻 **Ruta 3: Desarrollador** *(5 horas)*
*Para programadores que integrarán PyPozo*

```
1. Guía Rápida (5 min)
   ↓
2. Manual - sección "Uso de la Librería" (30 min)
   ↓
3. API Reference completa (120 min)
   ↓
4. Código fuente y ejemplos (90 min)
   ↓
5. Tests y debugging (45 min)
```

---

## 💡 Mejores Prácticas

### 🎯 **Para Análisis Básico de Pozos**

#### ✅ Workflow Recomendado

1. **Verificación inicial**
   ```python
   # Siempre verificar el pozo antes de procesar
   well = WellManager.from_las("mi_pozo.las")
   print(f"Curvas disponibles: {well.curves}")
   print(f"Profundidad: {well.depth_range}")
   ```

2. **Control de calidad**
   ```python
   # Verificar datos antes de cálculos
   gr_data = well.get_curve_data("GR")
   if gr_data is None:
       print("❌ No hay curva GR")
       return
   
   # Verificar rangos razonables
   if gr_data.max() > 1000 or gr_data.min() < 0:
       print("⚠️ Valores GR fuera de rango normal")
   ```

3. **Cálculos petrofísicos**
   ```python
   # Usar parámetros apropiados para la región
   vcl_result = vcl_calc.calculate(
       gr_data,
       method="larionov_tertiary",  # Para rocas jóvenes
       gr_clean=15,  # Ajustar según geología local
       gr_clay=150
   )
   ```

#### 🚫 Errores Comunes a Evitar

- **No verificar existencia de curvas** antes de usar
- **Usar parámetros genéricos** sin considerar geología local  
- **No validar rangos** de datos de entrada
- **Mezclar unidades** sin conversión
- **No guardar trabajo** intermedio

### 🔧 **Para Desarrollo con la API**

#### ✅ Buenas Prácticas de Código

```python
# ✅ BIEN: Manejo robusto de errores
def calcular_vcl_seguro(well, curve_name="GR"):
    """Calcular VCL con manejo robusto de errores."""
    try:
        # Verificar curva
        if curve_name not in well.curves:
            available = [c for c in well.curves if 'GR' in c.upper()]
            if available:
                print(f"Usando {available[0]} en lugar de {curve_name}")
                curve_name = available[0]
            else:
                raise ValueError(f"No se encontró curva GR en: {well.curves}")
        
        # Obtener datos
        gr_data = well.get_curve_data(curve_name)
        if gr_data is None or len(gr_data) == 0:
            raise ValueError("Datos GR vacíos o inválidos")
        
        # Calcular VCL
        vcl_calc = VclCalculator()
        result = vcl_calc.calculate(gr_data, method="larionov_tertiary")
        
        return result
        
    except Exception as e:
        print(f"Error calculando VCL: {e}")
        return None

# ❌ MAL: Sin manejo de errores
def calcular_vcl_inseguro(well):
    gr_data = well.get_curve_data("GR")  # Puede ser None
    vcl_calc = VclCalculator()
    return vcl_calc.calculate(gr_data)  # Fallará si gr_data es None
```

#### 🚀 Optimización de Rendimiento

```python
# ✅ Para archivos grandes: filtrar primero
def procesar_pozo_grande(well, depth_min=1000, depth_max=3000):
    """Procesar solo el intervalo de interés."""
    # Filtrar por profundidad primero
    well_filtered = well.filter_by_depth(depth_min, depth_max)
    
    # Luego procesar
    vcl_calc = VclCalculator()
    gr_data = well_filtered.get_curve_data("GR")
    result = vcl_calc.calculate(gr_data)
    
    return result

# ✅ Para múltiples pozos: procesamiento paralelo
from concurrent.futures import ThreadPoolExecutor

def procesar_pozos_paralelo(archivos_las):
    """Procesar múltiples pozos en paralelo."""
    def procesar_uno(archivo):
        well = WellManager.from_las(archivo)
        return calcular_vcl_seguro(well)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(procesar_uno, archivos_las))
    
    return results
```

### 📊 **Para Visualización Efectiva**

#### ✅ Gráficos Profesionales

```python
# Configuración recomendada para gráficos
def crear_grafico_profesional(well, curves):
    """Crear gráfico con estilo profesional."""
    plotter = WellPlotter()
    
    fig = plotter.plot_well(
        well,
        curves=curves,
        figsize=(15, 10),  # Tamaño adecuado para presentaciones
        title=f"Análisis de Registros - {well.name}"
    )
    
    # Configurar para exportación de alta calidad
    fig.savefig(
        f"{well.name}_analysis.png",
        dpi=300,  # Alta resolución
        bbox_inches='tight',  # Sin espacios extra
        facecolor='white'  # Fondo blanco
    )
    
    return fig
```

#### 🎨 Paletas de Colores Recomendadas

```python
# Colores profesionales para diferentes tipos de curvas
CURVE_COLORS = {
    'basic': ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00'],  # Verde, Rojo, Azul, Naranja
    'petrophysics': ['#8B4513', '#00CED1', '#9932CC'],      # Marrón, Cian, Violeta
    'comparison': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FCEA2B']
}
```

---

## 🔍 Solución Rápida de Problemas

### ❓ **Problemas Frecuentes**

| Problema | Síntoma | Solución Rápida |
|----------|---------|-----------------|
| **Archivo no carga** | `Error reading LAS` | Verificar encoding: `encoding='latin1'` |
| **Curva no existe** | `Curve not found` | Listar curvas: `well.curves` |
| **GUI no inicia** | `PyQt5 not available` | Instalar: `pip install PyQt5` |
| **Memoria insuficiente** | App se cuelga | Filtrar datos: `well.filter_by_depth()` |
| **Gráficos no aparecen** | Ventana vacía | Cambiar backend: `matplotlib.use('Qt5Agg')` |

### 🛠️ **Diagnóstico Rápido**

```bash
# Script de diagnóstico - guardar como diagnostico.py
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import pypozo
    print('✅ PyPozo: OK')
except:
    print('❌ PyPozo: ERROR')

try:
    from PyQt5 import QtCore
    print('✅ PyQt5: OK')
except:
    print('❌ PyQt5: ERROR')

try:
    import matplotlib
    print(f'✅ Matplotlib: {matplotlib.__version__}')
except:
    print('❌ Matplotlib: ERROR')
"
```

---

## 📊 Archivos de Ejemplo

PyPozo incluye varios archivos de ejemplo para práctica:

### 📂 **Directorio `data/`**

```
data/
├── ABEDUL-1_MERGED.las         # Pozo completo con múltiples curvas
├── ARIEL-1_MERGED.las          # Pozo con registros eléctricos
├── PALO BLANCO 791_PROCESADO.las # Pozo con cálculos petrofísicos
└── Originales/                 # Archivos originales sin procesar
```

### 🎯 **Casos de Uso de los Ejemplos**

| Archivo | Mejor Para | Curvas Principales |
|---------|------------|-------------------|
| **ABEDUL-1** | Aprendizaje básico | GR, RT, RHOB, NPHI |
| **ARIEL-1** | Análisis eléctrico | Múltiples resistividades |
| **PALO BLANCO** | Petrofísica avanzada | Incluye VCL, PHIE calculados |

### 🚀 **Ejercicios Sugeridos**

1. **Ejercicio Básico** (10 min)
   ```bash
   # Cargar ABEDUL-1 y crear gráfico básico
   python pypozo_app.py
   # Cargar data/ABEDUL-1_MERGED.las
   # Graficar curvas básicas
   ```

2. **Ejercicio Intermedio** (20 min)
   ```python
   # Calcular VCL en ABEDUL-1
   well = WellManager.from_las("data/ABEDUL-1_MERGED.las")
   vcl_calc = VclCalculator()
   result = vcl_calc.calculate(well.get_curve_data("GR"))
   well.add_curve("VCL_CALC", result["vcl"])
   ```

3. **Ejercicio Avanzado** (30 min)
   ```python
   # Comparar múltiples pozos
   pozos = ["ABEDUL-1", "ARIEL-1", "PALO BLANCO"]
   # Cargar todos, calcular VCL, comparar estadísticas
   ```

---

## 🚀 Próximos Pasos

### 📈 **Hoja de Ruta de Aprendizaje**

Después de dominar lo básico, puedes explorar:

1. **Automatización** - Scripts para procesamiento en lote
2. **Análisis Estadístico** - Correlaciones entre curvas
3. **Machine Learning** - Predicción de propiedades
4. **Integración** - Conectar con otras herramientas
5. **Desarrollo** - Contribuir al proyecto PyPozo

### 🤝 **Comunidad y Soporte**

- **Issues**: Reportar bugs y solicitar funcionalidades
- **Discussions**: Preguntas y casos de uso
- **Contribuciones**: Mejoras de código y documentación
- **Email**: Soporte directo para casos complejos

---

## ✅ Lista de Verificación

### 📋 **Para Nuevos Usuarios**

- [ ] Instalé PyPozo correctamente
- [ ] Ejecuté el diagnóstico del sistema
- [ ] Cargué mi primer pozo en la GUI
- [ ] Creé mi primer gráfico de curvas
- [ ] Calculé VCL usando la interfaz
- [ ] Leí la sección de solución de problemas

### 📋 **Para Desarrolladores**

- [ ] Revisé la API Reference completa
- [ ] Probé los ejemplos de código básicos
- [ ] Entendí el manejo de errores recomendado
- [ ] Configuré mi entorno de desarrollo
- [ ] Ejecuté los tests automatizados
- [ ] Contribuí con un ejemplo o mejora

---

**🎉 ¡Felicidades! Ya tienes todo lo necesario para convertirte en un experto en PyPozo.**

*Para preguntas específicas o casos complejos, consulta la documentación técnica o contacta al equipo de desarrollo.*

---

**Centro de Documentación PyPozo 2.0**  
*Actualizado: Julio 2025*
