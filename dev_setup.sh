# Configuración del entorno de desarrollo para PyPozo

# Instalar paquete en modo desarrollo
pip install -e .

# Dependencias de desarrollo
pip install pytest pytest-cov black flake8 mypy jupyter

# Para ejecutar tests
pytest tests/

# Para formatear código
black src/

# Para linting
flake8 src/

# Para type checking
mypy src/
