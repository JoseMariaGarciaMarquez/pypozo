# PyPozo 🛢️ - Aprende Geofísica de Pozos

<div align="center">
  <img src="images/logo_completo.png" alt="PyPozo Logo" width="300"/>
  
  **Tu primer software para aprender análisis de pozos petroleros** 🎓
  
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![Status](https://img.shields.io/badge/Status-Educativo-brightgreen.svg)](https://github.com/JoseMariaGarciaMarquez/pypozo)
  
  ---
  
## ☕ ¿Te ayudó con tu tesis o proyecto?

  [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/ingjoma)
  
</div>

¿Estudias **Geología, Ingeniería de Petróleos o Geofísica**? PyPozo es la herramienta perfecta para aprender análisis de registros de pozos. Con una interfaz súper fácil de usar, podrás entender conceptos complejos de petrofísica mientras practicas con datos reales.

## 🎓 ¿Por qué PyPozo es perfecto para estudiantes?

### 🎯 Aprende Haciendo

- **Interfaz Visual**: No necesitas ser programador para empezar
- **Datos Reales**: Archivos LAS incluidos para practicar  
- **Resultados Inmediatos**: Ve los gráficos al instante
- **Gratis y Abierto**: Sin licencias costosas como otros softwares

### � Conceptos que Aprenderás

- **Volumen de Arcilla (VCL)**: 5 métodos diferentes explicados paso a paso
- **Porosidad Efectiva**: Cómo calcularla con registros de densidad y neutrón
- **Análisis Litológico**: Identifica areniscas, lutitas y carbonatos
- **Interpretación de Curvas**: GR, SP, resistividades, densidad, neutrón

### 🔄 Perfecto para Proyectos Académicos

- **Tesis de Grado**: Analiza pozos reales para tu investigación
- **Trabajos de Clase**: Reportes con gráficos profesionales
- **Prácticas de Laboratorio**: Complementa tu aprendizaje teórico
- **Proyectos Grupales**: Fácil de compartir y colaborar

### 💡 Ventajas sobre Software Comercial

- **Costo $0**: A diferencia de Petrel, Techlog o WellCAD
- **Fácil de Instalar**: Solo necesitas Python (viene con Anaconda)
- **Código Abierto**: Puedes ver exactamente cómo se hacen los cálculos
- **Comunidad Estudiantil**: Otros estudiantes que pueden ayudarte

## 🚀 Instalación Súper Fácil (5 minutos)

### Opción 1: Para estudiantes con Anaconda 🐍

```bash
# 1. Descargar el proyecto
git clone https://github.com/JoseMariaGarciaMarquez/pypozo.git
cd pypozo

# 2. Instalar todo de una vez
pip install -e .

# 3. ¡Empezar a usar!
python pypozo_app.py
```

### Opción 2: Si no tienes Python instalado

1. **Descarga Anaconda** desde [anaconda.com](https://www.anaconda.com/)
2. **Instala Anaconda** (incluye Python + todas las librerías científicas)
3. **Abre Anaconda Prompt** y sigue los pasos de arriba

### Opción 3: Ambiente separado (Recomendado)

```bash
# Crear ambiente solo para PyPozo
conda create -n pypozo python=3.11
conda activate pypozo

# Instalar PyPozo
pip install -e .
python pypozo_app.py
```

## 📖 Tu Primera Sesión de Aprendizaje

### Paso 1: Lanza la aplicación

```bash
python pypozo_app.py
```

¡Se abrirá una ventana con interfaz gráfica súper intuitiva!

### Paso 2: Carga tu primer pozo

1. Haz clic en "📂 Cargar Pozo"
2. Ve a la carpeta `data/` y selecciona `ABEDUL-1_MERGED_COMPLETE.las`
3. ¡Ya tienes datos reales de un pozo colombiano!

### Paso 3: Haz tu primer gráfico

1. Selecciona el pozo que cargaste
2. Ve a la pestaña "📊 Curvas"  
3. Haz clic en "📊 Básicas" (selecciona GR, SP, CAL automáticamente)
4. Haz clic en "🎨 Graficar Seleccionadas"
5. ¡Boom! 💥 Ya tienes tu primer log de pozo

## 🎓 Ejercicios y Proyectos para Estudiantes

### 📋 Proyecto Nivel Principiante (Para comenzar)

**Objetivo**: Hacer tu primer análisis básico de pozo

1. **Carga el pozo** `ABEDUL-1_MERGED_COMPLETE.las`
2. **Grafica las curvas básicas**: GR, SP, CAL
3. **Identifica zonas**: ¿Dónde hay lutitas? ¿Dónde hay areniscas?
4. **Exporta tu gráfico** para incluirlo en un reporte
5. **Pregunta clave**: ¿Por qué el GR es alto en algunas zonas?

### 🔬 Proyecto Nivel Intermedio (Para tu tesis)

**Objetivo**: Cálculo de propiedades petrofísicas

1. **Calcula VCL** usando el método de Larionov
2. **Calcula Porosidad** con registros de densidad y neutrón  
3. **Compara diferentes métodos** de cálculo
4. **Haz un análisis litológico** completo
5. **Pregunta clave**: ¿Cuál es la mejor zona reservorio?

### 🚀 Proyecto Avanzado (Para trabajos de grado)

**Objetivo**: Análisis completo de yacimiento

1. **Fusiona múltiples pozos** del mismo campo
2. **Compara propiedades** entre pozos
3. **Identifica tendencias regionales**
4. **Crea mapas de propiedades**
5. **Pregunta clave**: ¿Cómo varía la calidad del reservorio espacialmente?

## 📊 Datos Incluidos para Practicar

El proyecto incluye pozos reales colombianos para que practiques:

- **`ABEDUL-1`** - Pozo completo con registros básicos y avanzados
- **`ARIEL-1`** - Excelente para aprender curvas eléctricas
- **`PALO BLANCO`** - Datos procesados ideales para principiantes

## 💡 ¿Necesitas Ayuda con tu Proyecto?

### 🆘 Problemas Comunes y Soluciones

**"No puedo instalar PyPozo"**

- Asegúrate de tener Python 3.8 o superior
- Usa Anaconda (es más fácil para estudiantes)
- Revisa la [Guía de Instalación Detallada](docs/GUIA_RAPIDA.md)

**"Los gráficos se ven raros"**

- Verifica que el archivo LAS esté completo
- Usa los datos de ejemplo primero
- Consulta el [Manual de Usuario](docs/MANUAL_USUARIO.md)

**"No entiendo los cálculos"**

- Lee la [documentación técnica](docs/API_REFERENCE.md)
- El código es abierto: puedes ver exactamente qué hace cada función
- Pregunta en los Issues de GitHub

### 📚 Recursos Adicionales

- **[Guía Rápida](docs/GUIA_RAPIDA.md)** - Aprende lo básico en 5 minutos
- **[Manual Completo](docs/MANUAL_USUARIO.md)** - Tutorial paso a paso  
- **[Documentación Técnica](docs/API_REFERENCE.md)** - Para los que quieren programar
- **[Jupyter Notebooks](notebooks/)** - Ejemplos interactivos

### 🤝 Comunidad Estudiantil

- **GitHub Issues**: Haz preguntas técnicas
- **Discussions**: Comparte tu experiencia con otros estudiantes
- **Pull Requests**: Mejora el código (¡suma puntos en tu CV!)

## 🎯 Roadmap Estudiantil

### ✅ Ya Disponible

- Interfaz gráfica súper fácil de usar
- Cálculos básicos de petrofísica (VCL, Porosidad)
- Datos reales para practicar
- Documentación en español

### 🚧 En Desarrollo (¡Puedes contribuir!)

- Más métodos de cálculo de saturación de agua
- Tutorials en video paso a paso
- Ejercicios guiados por materia
- Integración con Jupyter para clases

### 🎓 Ideas para tu Tesis

- Machine Learning aplicado a registros de pozo
- Caracterización de yacimientos no convencionales
- Análisis de incertidumbre en cálculos petrofísicos
- Integración con datos sísmicos

## 📄 Licencia

Este proyecto es completamente **GRATIS** y está bajo la Licencia MIT. Úsalo para tu tesis, trabajos, proyectos personales - ¡lo que quieras!

## 🙏 Agradecimientos Especiales

- **Estudiantes** que han probado y mejorado PyPozo
- **Profesores** que lo han recomendado en sus clases  
- **Comunidad open source** de geofísica
- **Contributors** que han agregado funcionalidades

---

<div align="center">
  
**🎓 Hecho por estudiantes, para estudiantes**

**¿Te ayudó con tu proyecto? ¡Compártelo con tus compañeros!**

[⭐ Dale una estrella en GitHub](https://github.com/JoseMariaGarciaMarquez/pypozo) • [📚 Documentación](docs/) • [☕ Buy Me a Coffee](https://buymeacoffee.com/ingjoma)

*"La mejor manera de aprender petrofísica es practicando con datos reales"*

</div>
