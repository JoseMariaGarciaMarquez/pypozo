# Tests de PyPozo 2.0

Suite completa de tests para validar todas las funcionalidades del proyecto PyPozo.

## 📁 Estructura de Tests

```
tests/
├── conftest.py              # Configuración y fixtures compartidas
├── test_quick_check.py      # Verificación rápida del entorno
├── test_core.py             # Tests del módulo core (WellManager, etc.)
├── test_petrophysics.py     # Tests de cálculos petrofísicos
├── test_gui.py              # Tests de la interfaz gráfica
├── test_integration.py      # Tests de integración entre módulos
├── run_tests.py             # Script para ejecutar todos los tests
└── README.md                # Esta documentación
```

## 🚀 Ejecución Rápida

### Opción 1: Script automatizado (Recomendado)
```bash
cd tests
python run_tests.py
```

### Opción 2: pytest directo
```bash
# Verificación rápida del entorno
pytest tests/test_quick_check.py -v

# Tests individuales
pytest tests/test_core.py -v
pytest tests/test_petrophysics.py -v  
pytest tests/test_gui.py -v
pytest tests/test_integration.py -v

# Todos los tests
pytest tests/ -v
```

### Opción 3: Tests específicos
```bash
# Solo tests unitarios
pytest tests/ -m "unit" -v

# Solo tests de integración
pytest tests/ -m "integration" -v

# Tests que no requieren GUI
pytest tests/ -m "not gui" -v
```

## 📋 Tipos de Tests

### 🔧 Tests Core (`test_core.py`)
- **WellManager**: Creación, carga de LAS, gestión de curvas
- **WellDataFrame**: Fusión de pozos, validación de datos
- **IO Operations**: Exportación LAS/CSV, manejo de archivos
- **Real Data Integration**: Tests con archivos LAS reales del proyecto

### 🧮 Tests Petrofísicos (`test_petrophysics.py`) 
- **VclCalculator**: Métodos linear, Larionov, Clavier, Steiber
- **PorosityCalculator**: Densidad, neutrón, porosidad combinada
- **Integration**: Workflows VCL → porosidad → correcciones
- **Quality Control**: Validación de rangos y datos

### 🖥️ Tests GUI (`test_gui.py`)
- **Main Window**: Creación, componentes, menús, toolbars
- **Well Loading**: Diálogos, árbol de pozos, actualización UI
- **Petrophysics UI**: Pestañas, controles, estado de botones
- **Plotting**: Componentes de gráficos, estado, funcionalidad
- **Error Handling**: Manejo de archivos inválidos, pozos vacíos

### 🔄 Tests Integración (`test_integration.py`)
- **End-to-End Workflow**: Carga → cálculos → visualización → exportación
- **Multi-well Analysis**: Análisis comparativo, fusión de pozos
- **Real Data Processing**: Procesamiento de archivos LAS reales
- **System Integration**: Memoria, concurrencia, recuperación de errores

## 🛠️ Configuración

### Dependencias de Test
```bash
pip install pytest pytest-qt
```

### Dependencias Opcionales
```bash
pip install pytest-cov    # Para coverage
pip install pytest-xvfb   # Para tests GUI en Linux sin display
pip install psutil         # Para tests de memoria
```

### Variables de Entorno
```bash
# Para tests GUI sin ventanas
export QT_QPA_PLATFORM=offscreen

# Para tests con datos reales
export PYPOZO_TEST_DATA=/path/to/test/data
```

## 📊 Fixtures Disponibles

### Datos de Prueba
- `sample_las_data`: DataFrame con curvas típicas (GR, RHOB, NPHI, RT)
- `sample_well_metadata`: Metadatos de pozo de ejemplo
- `temp_las_file`: Archivo LAS temporal para tests
- `sample_vcl_data`: Serie GR para tests de VCL
- `sample_porosity_data`: Datos RHOB/NPHI para tests de porosidad

### Archivos y Directorios
- `real_las_file`: Path a archivo LAS real del proyecto
- `temp_output_dir`: Directorio temporal para outputs

### GUI (si PyQt5 disponible)
- `qapp`: Aplicación Qt para tests
- `main_window`: Ventana principal de PyPozo

## 🎯 Marcadores de Tests

```bash
# Tests por categoría
pytest -m "unit"          # Tests unitarios básicos
pytest -m "integration"   # Tests de integración
pytest -m "gui"           # Tests de GUI (requieren PyQt5)
pytest -m "slow"          # Tests lentos
pytest -m "real_data"     # Tests con datos reales
```

## 📈 Interpretación de Resultados

### ✅ Test Exitoso
```
test_core.py::TestWellManager::test_well_manager_creation PASSED
```

### ❌ Test Fallido
```
test_core.py::TestWellManager::test_load_from_las FAILED
```

### ⚠️ Test Saltado
```
test_gui.py::TestMainWindow::test_window_creation SKIPPED [PyQt5 no disponible]
```

## 🔧 Troubleshooting

### Error: "PyQt5 no disponible"
```bash
pip install PyQt5
# o ejecutar sin tests GUI:
pytest tests/ -m "not gui"
```

### Error: "No se pudieron importar módulos de PyPozo"
- Verificar que `src/` está en el PYTHONPATH
- Ejecutar desde el directorio raíz del proyecto
- Verificar instalación de dependencias

### Error: "No hay archivos LAS reales"
- Verificar que existe el directorio `data/` con archivos `.las`
- Los tests de datos reales se saltarán automáticamente si no hay datos

### Tests de GUI fallan en servidor
```bash
# Linux sin display
export QT_QPA_PLATFORM=offscreen
pytest tests/test_gui.py

# O instalar xvfb
sudo apt-get install xvfb
pytest tests/test_gui.py
```

## 📝 Añadir Nuevos Tests

### 1. Test Unitario Básico
```python
def test_new_functionality():
    """Test nueva funcionalidad."""
    # Arrange
    data = setup_test_data()
    
    # Act
    result = function_to_test(data)
    
    # Assert
    assert result is not None
    assert result.shape == expected_shape
```

### 2. Test con Fixture
```python
def test_with_fixture(sample_las_data):
    """Test usando fixture de datos."""
    assert len(sample_las_data) > 0
    assert 'GR' in sample_las_data.columns
```

### 3. Test Parametrizado
```python
@pytest.mark.parametrize("method,expected", [
    ("linear", 0.5),
    ("larionov", 0.4),
])
def test_vcl_methods(method, expected):
    """Test múltiples métodos VCL."""
    # Test implementation
```

## 📞 Soporte

- **Issues**: Reportar problemas en GitHub Issues
- **Documentación**: Ver `/docs/` para más detalles
- **Logs**: Activar logging verbose con `-v -s` en pytest

---

**🧪 Suite de Tests PyPozo 2.0 - Asegurando calidad y confiabilidad**
