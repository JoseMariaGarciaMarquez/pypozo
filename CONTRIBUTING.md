# 🤝 Guía de Contribución - PyPozo 2.0

¡Gracias por tu interés en contribuir a PyPozo 2.0! Este proyecto es una alternativa open source profesional para análisis petrofísico, y valoramos mucho las contribuciones de la comunidad.

## 📋 Tabla de Contenidos

- [🎯 Cómo Contribuir](#-cómo-contribuir)
- [🐛 Reportar Issues](#-reportar-issues)
- [🔧 Pull Requests](#-pull-requests)
- [📝 Estándares de Código](#-estándares-de-código)
- [🧪 Testing](#-testing)
- [📚 Documentación](#-documentación)
- [💬 Comunicación](#-comunicación)

## 🎯 Cómo Contribuir

Hay muchas formas de contribuir a PyPozo 2.0:

### 🐛 **Reportar Bugs**
- Encuentra y reporta errores
- Proporciona casos de prueba reproducibles
- Mejora el manejo de errores

### ✨ **Nuevas Funcionalidades**
- Implementa nuevos métodos petrofísicos
- Mejora la interfaz de usuario
- Añade nuevos tipos de visualización
- Integra con otros formatos de datos

### 📊 **Mejoras en Análisis**
- Nuevos algoritmos de cálculo
- Optimización de performance
- Validaciones de QC más robustas
- Métodos de interpretación avanzados

### 📚 **Documentación**
- Mejora la documentación existente
- Añade ejemplos y tutoriales
- Traduce documentación
- Crea videos demostrativos

### 🧪 **Testing**
- Mejora la cobertura de tests
- Añade tests de rendimiento
- Tests con datos reales
- Tests de integración

## 🐛 Reportar Issues

### Antes de Crear un Issue

1. **🔍 Busca issues existentes** - Verifica que no exista ya un reporte similar
2. **✅ Usa la última versión** - Asegúrate de usar la versión más reciente
3. **🧪 Reproduce el problema** - Confirma que el issue es reproducible

### Tipos de Issues

#### 🐛 **Bug Report**
```markdown
**Descripción del Bug**
Descripción clara y concisa del problema.

**Pasos para Reproducir**
1. Cargar archivo LAS...
2. Seleccionar método...
3. Ver error...

**Comportamiento Esperado**
Qué esperabas que pasara.

**Comportamiento Actual**
Qué pasó realmente.

**Screenshots/Logs**
Si aplica, añade capturas o logs.

**Entorno:**
- OS: [Windows/Linux/macOS]
- Python: [3.8/3.9/3.10/3.11/3.12]
- PyPozo: [2.0.0]
- PyQt5: [5.15.x]

**Datos de Prueba**
Si es posible, adjunta archivo LAS que reproduce el issue.
```

#### 💡 **Feature Request**
```markdown
**¿Tu feature request está relacionado con un problema?**
Descripción clara del problema: "Estoy frustrado cuando..."

**Describe la solución que te gustaría**
Descripción clara y concisa de lo que quieres que pase.

**Describe alternativas consideradas**
Descripción de soluciones alternativas.

**Contexto Adicional**
Cualquier otro contexto o screenshots sobre el feature request.

**Beneficio para la Comunidad**
Cómo beneficiaría esto a otros usuarios de PyPozo.
```

#### 📚 **Documentation Issue**
```markdown
**Sección de Documentación**
¿Qué parte de la documentación necesita mejora?

**Problema Actual**
¿Qué está mal o falta?

**Mejora Sugerida**
¿Cómo se podría mejorar?

**Audiencia Objetivo**
¿Para qué tipo de usuario es esta mejora?
```

### 🏷️ **Labels de Issues**

- `bug` - Algo no está funcionando
- `enhancement` - Nueva funcionalidad o solicitud
- `documentation` - Mejoras o adiciones a la documentación
- `good first issue` - Bueno para principiantes
- `help wanted` - Se necesita ayuda extra
- `question` - Información adicional solicitada
- `wontfix` - No será trabajado
- `duplicate` - Este issue ya existe
- `priority:high` - Prioridad alta
- `priority:low` - Prioridad baja
- `area:petro` - Relacionado con cálculos petrofísicos
- `area:gui` - Relacionado con interfaz gráfica
- `area:io` - Relacionado con entrada/salida de datos
- `area:plotting` - Relacionado con visualización

## 🔧 Pull Requests

### Proceso de Pull Request

1. **🍴 Fork el repositorio**
2. **🌿 Crea una rama** (`git checkout -b feature/nueva-funcionalidad`)
3. **💻 Haz tus cambios**
4. **🧪 Ejecuta los tests** (`python tests/run_tests.py`)
5. **📝 Commitea tus cambios** (`git commit -am 'Añade nueva funcionalidad'`)
6. **📤 Push a la rama** (`git push origin feature/nueva-funcionalidad`)
7. **🔄 Abre un Pull Request**

### Directrices para Pull Requests

#### ✅ **Checklist del PR**

Antes de enviar tu PR, asegúrate de que:

- [ ] El código sigue las [convenciones de estilo](#-estándares-de-código)
- [ ] Los tests pasan (`python tests/run_tests.py`)
- [ ] Se añadieron tests para nueva funcionalidad
- [ ] La documentación está actualizada
- [ ] El CHANGELOG.md está actualizado
- [ ] No hay archivos de configuración personal incluidos

#### 📝 **Template de Pull Request**

```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix (cambio no breaking que arregla un issue)
- [ ] Nueva funcionalidad (cambio no breaking que añade funcionalidad)
- [ ] Breaking change (fix o feature que causaría que funcionalidad existente no funcione como se espera)
- [ ] Actualización de documentación

## ¿Cómo se ha probado?
Describe las pruebas que ejecutaste para verificar tus cambios.

## Screenshots (si aplica)
Añade screenshots para ayudar a explicar tus cambios.

## Checklist:
- [ ] Mi código sigue las directrices de estilo de este proyecto
- [ ] He realizado una auto-revisión de mi código
- [ ] He comentado mi código, particularmente en áreas difíciles de entender
- [ ] He realizado cambios correspondientes a la documentación
- [ ] Mis cambios no generan nuevos warnings
- [ ] He añadido tests que prueban que mi fix es efectivo o que mi feature funciona
- [ ] Tests unitarios nuevos y existentes pasan localmente con mis cambios

## Issues Relacionados
Cierra #(número del issue)
```

### 🔍 **Proceso de Review**

1. **Automated Checks**: CI/CD ejecuta tests automáticamente
2. **Code Review**: Al menos un maintainer revisará el código
3. **Testing**: Los maintainers pueden probar la funcionalidad
4. **Merge**: Una vez aprobado, se hace merge a la rama principal

## 📝 Estándares de Código

### 🐍 **Python Style Guide**

Seguimos [PEP 8](https://pep8.org/) con algunas adaptaciones:

```python
# ✅ Bueno
def calculate_vcl(gamma_ray_data, method='linear', gr_clean=20, gr_clay=120):
    """
    Calcular volumen de arcilla usando diferentes métodos.
    
    Args:
        gamma_ray_data (pd.Series): Datos de gamma ray
        method (str): Método de cálculo ('linear', 'larionov_older', etc.)
        gr_clean (float): Valor GR para arena limpia
        gr_clay (float): Valor GR para arcilla pura
    
    Returns:
        dict: Resultado con VCL calculado y metadatos
    """
    if method == 'linear':
        vcl = (gamma_ray_data - gr_clean) / (gr_clay - gr_clean)
        vcl = np.clip(vcl, 0, 1)
    
    return {
        'vcl': vcl,
        'method': method,
        'parameters': {'gr_clean': gr_clean, 'gr_clay': gr_clay}
    }

# ❌ Malo
def calc_vcl(gr,m,gc,gcl):
    if m=='lin':
        return (gr-gc)/(gcl-gc)
```

### 📁 **Estructura de Archivos**

```
nueva_funcionalidad/
├── __init__.py                 # Imports públicos
├── calculator.py               # Lógica principal
├── validators.py               # Validaciones
├── constants.py                # Constantes
└── tests/
    ├── test_calculator.py      # Tests unitarios
    └── test_integration.py     # Tests de integración
```

### 🎨 **Naming Conventions**

- **Clases**: `PascalCase` (ej: `VclCalculator`)
- **Funciones/métodos**: `snake_case` (ej: `calculate_porosity`)
- **Variables**: `snake_case` (ej: `gamma_ray_data`)
- **Constantes**: `UPPER_SNAKE_CASE` (ej: `DEFAULT_MATRIX_DENSITY`)
- **Archivos**: `snake_case` (ej: `water_saturation.py`)

### 📖 **Documentación de Código**

```python
def calculate_porosity(bulk_density, matrix_density=2.65, fluid_density=1.0):
    """
    Calcular porosidad usando el método de densidad.
    
    Esta función implementa la ecuación estándar de porosidad por densidad
    utilizada en petrofísica para estimar la porosidad de la formación.
    
    Args:
        bulk_density (pd.Series or np.array): Densidad bulk de la formación [g/cc]
        matrix_density (float, optional): Densidad de la matriz. Defaults to 2.65.
        fluid_density (float, optional): Densidad del fluido. Defaults to 1.0.
    
    Returns:
        dict: Diccionario conteniendo:
            - 'porosity' (pd.Series): Porosidad calculada [fracción]
            - 'method' (str): Método utilizado
            - 'qc_flags' (pd.Series): Flags de quality control
            - 'statistics' (dict): Estadísticas del resultado
    
    Raises:
        ValueError: Si matrix_density <= fluid_density
        TypeError: Si bulk_density no es numérico
    
    Example:
        >>> import pandas as pd
        >>> rhob = pd.Series([2.3, 2.4, 2.2, 2.5])
        >>> result = calculate_porosity(rhob, matrix_density=2.65)
        >>> print(result['porosity'].mean())
        0.185
    
    Note:
        La ecuación utilizada es: φ = (ρma - ρb) / (ρma - ρfl)
        donde φ es porosidad, ρma es densidad matriz, ρb es densidad bulk,
        y ρfl es densidad del fluido.
    
    References:
        - Schlumberger (2013). Cased Hole Log Interpretation Principles
        - Ellis & Singer (2007). Well Logging for Earth Scientists
    """
```

## 🧪 Testing

### 📋 **Requisitos de Testing**

- **Cobertura mínima**: 80% para nuevo código
- **Tests unitarios**: Para cada función pública
- **Tests de integración**: Para workflows completos
- **Tests de regresión**: Para bugs fix

### 🧪 **Escribir Tests**

```python
# tests/test_vcl_calculator.py
import pytest
import numpy as np
import pandas as pd
from pypozo.petrophysics import VclCalculator

class TestVclCalculator:
    
    @pytest.fixture
    def sample_gr_data(self):
        """Sample gamma ray data for testing."""
        return pd.Series([30, 50, 80, 120, 90], name='GR')
    
    @pytest.fixture
    def vcl_calculator(self):
        """VCL calculator instance."""
        return VclCalculator()
    
    def test_linear_method(self, vcl_calculator, sample_gr_data):
        """Test linear VCL calculation method."""
        result = vcl_calculator.calculate(
            gamma_ray=sample_gr_data,
            method='linear',
            gr_clean=20,
            gr_clay=120
        )
        
        # Test return structure
        assert 'vcl' in result
        assert 'method' in result
        assert result['method'] == 'linear'
        
        # Test VCL values are in valid range
        vcl_values = result['vcl']
        assert all(vcl_values >= 0)
        assert all(vcl_values <= 1)
        
        # Test specific values
        expected_vcl = (sample_gr_data - 20) / (120 - 20)
        expected_vcl = np.clip(expected_vcl, 0, 1)
        pd.testing.assert_series_equal(vcl_values, expected_vcl)
    
    def test_invalid_parameters(self, vcl_calculator, sample_gr_data):
        """Test handling of invalid parameters."""
        with pytest.raises(ValueError):
            vcl_calculator.calculate(
                gamma_ray=sample_gr_data,
                method='linear',
                gr_clean=120,  # Invalid: gr_clean > gr_clay
                gr_clay=20
            )
    
    @pytest.mark.parametrize("method,expected_range", [
        ('linear', (0, 1)),
        ('larionov_older', (0, 1)),
        ('larionov_tertiary', (0, 1)),
    ])
    def test_all_methods_valid_range(self, vcl_calculator, sample_gr_data, method, expected_range):
        """Test that all methods return values in valid range."""
        result = vcl_calculator.calculate(
            gamma_ray=sample_gr_data,
            method=method,
            gr_clean=20,
            gr_clay=120
        )
        
        vcl_values = result['vcl'].dropna()
        assert all(vcl_values >= expected_range[0])
        assert all(vcl_values <= expected_range[1])
```

### 🏃 **Ejecutar Tests**

```bash
# Tests completos con el script automático
python tests/run_tests.py

# Tests específicos por módulo
pytest tests/test_core.py -v
pytest tests/test_petrophysics.py -v
pytest tests/test_gui.py -v
pytest tests/test_integration.py -v

# Tests rápidos (solo environment y básicos)
pytest tests/test_quick_check.py tests/test_basic.py -v

# Tests con cobertura
pytest tests/ --cov=src --cov-report=html

# Tests de performance (excluyendo los lentos)
pytest tests/ -m "not slow"

# Tests específicos por funcionalidad
pytest tests/ -k "porosity" -v
pytest tests/ -k "vcl" -v
pytest tests/ -k "gui" -v

# Ejecutar tests en paralelo (si tienes pytest-xdist instalado)
pytest tests/ -n auto

# Tests con output detallado para debugging
pytest tests/test_gui.py -v -s --tb=long
```

### 📊 **Estructura del Testing Suite**

Nuestro testing suite está organizado de la siguiente manera:

```
tests/
├── conftest.py              # Fixtures y configuración compartida
├── test_basic.py           # Tests básicos de importación y dependencias
├── test_quick_check.py     # Tests rápidos de environment
├── test_core.py            # Tests del núcleo: WellManager, IO, etc.
├── test_petrophysics.py    # Tests de cálculos petrofísicos
├── test_gui.py             # Tests de interfaz gráfica (PyQt5)
├── test_integration.py     # Tests de integración end-to-end
├── run_tests.py           # Script para ejecución automática
└── README.md              # Documentación detallada del testing
```

### 🎯 **Markers de Testing**

Usamos los siguientes markers para categorizar tests:

```python
# Markers disponibles
@pytest.mark.slow          # Tests que toman más tiempo
@pytest.mark.integration   # Tests de integración completa
@pytest.mark.gui          # Tests que requieren GUI
@pytest.mark.real_data    # Tests con datos reales de pozos
@pytest.mark.synthetic    # Tests con datos sintéticos
@pytest.mark.core         # Tests de funcionalidad core
@pytest.mark.petrophysics # Tests de cálculos petrofísicos

# Ejecutar por markers
pytest -m "not slow"                    # Excluir tests lentos
pytest -m "integration"                 # Solo tests de integración
pytest -m "core and not gui"           # Core sin GUI
pytest -m "petrophysics and real_data" # Petrofísica con datos reales
```

### 🔧 **Setup de Testing para Contributors**

Para configurar tu entorno de testing:

```bash
# 1. Instalar dependencias de testing
pip install pytest pytest-qt pytest-cov pytest-mock

# 2. Verificar instalación con tests básicos
python tests/run_tests.py --basic-only

# 3. Ejecutar suite completo
python tests/run_tests.py

# 4. Verificar que tu código no rompe tests existentes
pytest tests/ --tb=short

# 5. Generar reporte de cobertura
pytest tests/ --cov=src --cov-report=html
# Ver reporte en: htmlcov/index.html
```

### ✅ **Checklist Pre-Commit Testing**

Antes de hacer commit, asegúrate de que:

- [ ] `pytest tests/test_basic.py` pasa (importaciones básicas)
- [ ] `pytest tests/test_core.py` pasa (funcionalidad core) 
- [ ] Tests específicos de tu cambio pasan
- [ ] No hay regresiones en tests existentes
- [ ] Cobertura de tests no disminuye significativamente
- [ ] Tests con datos reales pasan (si aplica)

### 🐛 **Debugging Tests**

Si encuentras tests fallando:

```bash
# Ver output completo y traceback detallado
pytest tests/test_failing.py -v -s --tb=long

# Ejecutar solo el test específico que falla
pytest tests/test_file.py::TestClass::test_method -v -s

# Ver warnings y información adicional
pytest tests/ -v --tb=short -W ignore::DeprecationWarning

# Debugging con pdb (Python debugger)
pytest tests/test_file.py --pdb

# Ver fixtures disponibles
pytest --fixtures tests/
```

## 📚 Documentación

### 📝 **Tipos de Documentación**

1. **API Documentation**: Docstrings en el código
2. **User Guide**: Guías paso a paso
3. **Developer Guide**: Información técnica para desarrolladores
4. **Examples**: Notebooks y scripts de ejemplo

### 📋 **Actualizando Documentación**

Al añadir nueva funcionalidad, actualiza:

- [ ] Docstrings en el código
- [ ] `README.md` si es funcionalidad principal
- [ ] `docs/API_REFERENCE.md`
- [ ] `docs/MANUAL_USUARIO.md` si afecta la UI
- [ ] Ejemplos en `examples/` o `notebooks/`

## 💬 Comunicación

### 🗨️ **Canales de Comunicación**

- **GitHub Issues**: Para bugs, features, y discusiones técnicas
- **GitHub Discussions**: Para preguntas generales y discusiones de comunidad
- **Email**: Para asuntos privados o de seguridad

### 🏷️ **Etiquetas y Menciones**

- Usa `@username` para mencionar específicamente
- Etiqueta issues relacionados con `#issue_number`
- Usa labels apropiados para categorizar

### 📅 **Tiempos de Respuesta**

- **Issues críticos**: 24-48 horas
- **Issues normales**: 1-2 semanas
- **Feature requests**: 2-4 semanas
- **Pull requests**: 3-7 días

## 🏆 Reconocimiento

### 👥 **Contributors**

Todos los contributors serán:
- Listados en `CONTRIBUTORS.md`
- Mencionados en releases notes
- Reconocidos en la documentación

### 🎖️ **Tipos de Contribución**

- 💻 **Code**: Contribuciones de código
- 📖 **Documentation**: Mejoras en documentación
- 🐛 **Bug reports**: Reportes de bugs de calidad
- 💡 **Ideas**: Sugerencias de funcionalidades
- 🧪 **Testing**: Mejoras en testing
- 🎨 **Design**: Mejoras en UI/UX
- ❓ **Answering Questions**: Ayuda en issues y discussions

## 📜 Código de Conducta

### 🤝 **Nuestro Compromiso**

Nos comprometemos a hacer de la participación en PyPozo 2.0 una experiencia libre de acoso para todos, independientemente de:

- Edad, tamaño corporal, discapacidad visible o invisible
- Etnicidad, características sexuales, identidad y expresión de género
- Nivel de experiencia, educación, estatus socioeconómico
- Nacionalidad, apariencia personal, raza, religión
- Identidad y orientación sexual

### ✅ **Comportamiento Esperado**

- Usar lenguaje acogedor e inclusivo
- Respetar diferentes puntos de vista y experiencias
- Aceptar críticas constructivas con gracia
- Enfocarse en lo que es mejor para la comunidad
- Mostrar empatía hacia otros miembros de la comunidad

### ❌ **Comportamiento Inaceptable**

- Lenguaje o imágenes sexualizadas
- Trolling, comentarios insultantes/despectivos
- Acoso público o privado
- Publicar información privada de otros sin permiso
- Otras conductas que podrían considerarse inapropiadas en un entorno profesional

## 🚀 ¡Empezando!

¿Listo para contribuir? ¡Genial!

1. **🍴 Fork el repositorio**
2. **📋 Elige un issue** (especialmente los marcados como `good first issue`)
3. **📝 Comenta en el issue** que planeas trabajar en él
4. **💻 Comienza a codificar**
5. **❓ Haz preguntas** si necesitas ayuda

### 🆕 **Para Principiantes**

Si eres nuevo en el proyecto, busca issues etiquetados como:
- `good first issue` - Ideales para empezar
- `help wanted` - Necesitamos ayuda específica
- `documentation` - Mejoras en documentación

---

## 📞 Contacto

- **Project Maintainer**: José María García Márquez
- **Email**: [tu-email@ejemplo.com]
- **GitHub**: [@tu-usuario]

---

**¡Gracias por contribuir a PyPozo 2.0! 🎉**

*Juntos estamos construyendo la mejor herramienta open source para análisis petrofísico.*
