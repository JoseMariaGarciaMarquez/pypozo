# PyPozo 2.0 - Organización del Proyecto

## 📁 Estructura Propuesta

```
pypozo/
├── 📄 README.md                 # Documentación principal
├── 📄 LICENSE                   # Licencia
├── 📄 pyproject.toml           # Configuración del proyecto
├── 📄 requirements.txt         # Dependencias
├── 📄 .gitignore               # Archivos ignorados por Git
├── 📄 setup.py                 # Script de instalación (opcional)
│
├── 📁 src/pypozo/              # Código fuente principal
│   ├── 📄 __init__.py
│   ├── 📁 core/                # Funcionalidades principales
│   │   ├── 📄 __init__.py
│   │   ├── 📄 well.py          # Gestión de pozos
│   │   ├── 📄 plotter.py       # Visualización
│   │   └── 📄 project.py       # Gestión de proyectos
│   ├── 📁 gui/                 # Interfaz gráfica
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main_window.py   # Ventana principal
│   │   ├── 📄 widgets/         # Widgets personalizados
│   │   └── 📄 styles/          # Estilos y temas
│   ├── 📁 utils/               # Utilidades
│   │   ├── 📄 __init__.py
│   │   ├── 📄 io.py            # Entrada/salida de archivos
│   │   └── 📄 helpers.py       # Funciones auxiliares
│   └── 📁 analysis/            # Análisis petrofísico
│       ├── 📄 __init__.py
│       ├── 📄 petrophysics.py  # Cálculos petrofísicos
│       └── 📄 statistics.py    # Estadísticas
│
├── 📁 tests/                   # Tests organizados
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py          # Configuración de pytest
│   ├── 📁 unit/                # Tests unitarios
│   ├── 📁 integration/         # Tests de integración
│   └── 📁 fixtures/            # Datos de prueba
│
├── 📁 docs/                    # Documentación
│   ├── 📄 user_guide.md       # Guía de usuario
│   ├── 📄 developer_guide.md  # Guía de desarrollador
│   ├── 📄 api_reference.md    # Referencia API
│   └── 📁 images/             # Imágenes de documentación
│
├── 📁 examples/                # Ejemplos de uso
│   ├── 📄 basic_usage.py      # Uso básico
│   ├── 📄 advanced_analysis.py # Análisis avanzado
│   └── 📁 sample_data/        # Datos de ejemplo
│
├── 📁 scripts/                 # Scripts utilitarios
│   ├── 📄 launch_app.py       # Lanzador de la aplicación
│   ├── 📄 data_converter.py   # Convertidor de datos
│   └── 📄 setup_dev.py        # Configuración de desarrollo
│
├── 📁 output/                  # Archivos de salida (ignorado por Git)
│   ├── 📁 plots/              # Gráficos generados
│   ├── 📁 exports/            # Archivos exportados
│   └── 📁 logs/               # Archivos de log
│
└── 📁 data/                    # Datos de desarrollo/prueba
    ├── 📁 samples/            # Muestras de pozos
    ├── 📁 test_files/         # Archivos para testing
    └── 📄 README.md           # Descripción de los datos
```

## 🔄 Plan de Reorganización

### Fase 1: Crear estructura base
1. Crear directorios principales
2. Mover archivos a sus ubicaciones correctas
3. Actualizar imports

### Fase 2: Limpiar archivos obsoletos
1. Consolidar documentación
2. Eliminar archivos duplicados
3. Mover archivos de test a carpeta unificada

### Fase 3: Actualizar configuración
1. Actualizar pyproject.toml
2. Crear requirements.txt
3. Actualizar .gitignore

### Fase 4: Documentación
1. README.md principal actualizado
2. Documentación de API
3. Guías de usuario y desarrollador

## 🎯 Beneficios

- **Navegación clara**: Estructura lógica y predecible
- **Mantenimiento fácil**: Código organizado por funcionalidad
- **Testing robusto**: Tests separados y organizados
- **Documentación accesible**: Docs centralizadas
- **Desarrollo colaborativo**: Estándares claros
