<!-- 
🔧 PULL REQUEST TEMPLATE
Gracias por contribuir a PyPozo 2.0! 
Por favor, completa esta información para ayudar con la revisión.
-->

## 📋 Descripción

<!-- Proporciona una descripción clara y concisa de los cambios -->

### 🎯 Tipo de Cambio

<!-- Marca todas las que apliquen -->

- [ ] 🐛 **Bug fix** (cambio no-breaking que arregla un issue)
- [ ] ✨ **Nueva funcionalidad** (cambio no-breaking que añade funcionalidad)
- [ ] 💥 **Breaking change** (fix o feature que causaría que funcionalidad existente no funcione)
- [ ] 📚 **Actualización de documentación**
- [ ] 🔧 **Refactoring** (cambios de código que no afectan funcionalidad)
- [ ] ⚡ **Mejora de rendimiento**
- [ ] 🧪 **Mejoras en testing**
- [ ] 🎨 **Mejoras de UI/UX**

## 🔗 Issues Relacionados

<!-- Vincula issues relacionados usando palabras clave -->

- Fixes #(issue_number)
- Closes #(issue_number)  
- Related to #(issue_number)
- Part of #(issue_number)

## 💾 Cambios Realizados

<!-- Lista detallada de cambios -->

### ➕ Añadido
- [ ] Funcionalidad X
- [ ] Método Y para cálculo Z
- [ ] Validación de entrada para...

### 🔧 Modificado
- [ ] Algoritmo de cálculo para...
- [ ] Interfaz de usuario de...
- [ ] Documentación de...

### ❌ Eliminado
- [ ] Código deprecado...
- [ ] Dependencia no utilizada...

### 🐛 Corregido
- [ ] Error en cálculo de...
- [ ] Problema de GUI con...
- [ ] Issue de compatibilidad...

## 🧪 Testing

### ✅ Tests Ejecutados

<!-- Marca todos los tests que has ejecutado -->

- [ ] **Basic Tests**: `python tests/run_tests.py --basic-only`
- [ ] **Core Tests**: `pytest tests/test_core.py -v`
- [ ] **Petrophysics Tests**: `pytest tests/test_petrophysics.py -v`
- [ ] **GUI Tests**: `pytest tests/test_gui.py -v` (si aplica)
- [ ] **Integration Tests**: `pytest tests/test_integration.py -v`
- [ ] **All Tests**: `python tests/run_tests.py`

### 🆕 Nuevos Tests

<!-- Si añadiste nuevos tests -->

- [ ] Tests unitarios para nueva funcionalidad
- [ ] Tests de integración
- [ ] Tests de regresión
- [ ] Tests con datos reales

### 📊 Cobertura de Tests

<!-- Si es relevante -->

- **Cobertura actual**: X%
- **Cobertura después de cambios**: Y%
- **Archivos con nueva cobertura**: [lista de archivos]

## 🔍 Descripción Técnica

### 🏗️ Arquitectura

<!-- Describe cambios arquitectónicos importantes -->

### 📦 Dependencias

<!-- ¿Se añadieron, modificaron o eliminaron dependencias? -->

- [ ] No hay cambios en dependencias
- [ ] Añadidas: [lista]
- [ ] Modificadas: [lista]
- [ ] Eliminadas: [lista]

### 🔄 Backward Compatibility

<!-- ¿Los cambios son compatible con versiones anteriores? -->

- [ ] ✅ Totalmente compatible hacia atrás
- [ ] ⚠️ Compatible con warnings de deprecación
- [ ] ❌ Breaking changes (requiere actualización de código)

## 📱 Screenshots / Output

<!-- Para cambios de UI o nuevas funcionalidades visuales -->

### Antes
<!-- Screenshot o descripción del estado anterior -->

### Después  
<!-- Screenshot o descripción del nuevo estado -->

## ⚡ Performance

<!-- Si hay implicaciones de rendimiento -->

### Benchmarks
<!-- Resultados de pruebas de rendimiento si aplica -->

- **Antes**: X segundos / Y MB memoria
- **Después**: X segundos / Y MB memoria
- **Mejora**: Z% más rápido / W% menos memoria

## 📝 Checklist Pre-Merge

### 🔧 Código

- [ ] Mi código sigue las [convenciones de estilo](../CONTRIBUTING.md#-estándares-de-código)
- [ ] He realizado una auto-revisión de mi código
- [ ] He comentado áreas complejas de mi código
- [ ] He eliminado código comentado no necesario
- [ ] No hay archivos temporales o de configuración personal incluidos

### 📚 Documentación

- [ ] He actualizado documentación relevante
- [ ] Docstrings están actualizados para nuevas funciones
- [ ] README.md actualizado si es necesario
- [ ] CHANGELOG.md actualizado (si aplica)
- [ ] Ejemplos actualizados si es necesario

### 🧪 Testing

- [ ] Tests existentes siguen pasando
- [ ] He añadido tests para nueva funcionalidad
- [ ] Tests cubren casos edge/error
- [ ] No hay tests flakey o que fallan intermitentemente

### 🔄 Git

- [ ] Commits tienen mensajes descriptivos
- [ ] Historia de commits está limpia (squash si es necesario)
- [ ] Branch está actualizado con main/develop
- [ ] No hay merge conflicts

## 👀 Notas para Reviewers

<!-- Información específica para quienes revisen el PR -->

### 🎯 Áreas de Enfoque

<!-- ¿En qué deberían enfocarse los reviewers? -->

- [ ] Lógica de negocio en [archivo/función]
- [ ] Manejo de errores en [archivo/función]
- [ ] Performance de [algoritmo/proceso]
- [ ] Usabilidad de [componente GUI]
- [ ] Documentación de [API/funcionalidad]

### 🤔 Decisiones de Diseño

<!-- Explica decisiones de diseño importantes o alternativas consideradas -->

### ❓ Preguntas Específicas

<!-- ¿Hay algo específico sobre lo que quieres feedback? -->

1. ¿Opinión sobre el approach para...?
2. ¿Debería considerar alternativa para...?
3. ¿La API propuesta es intuitiva para...?

## 🚀 Deploy Notes

<!-- Si hay consideraciones especiales para deployment -->

- [ ] No hay consideraciones especiales
- [ ] Requiere migración de datos
- [ ] Requiere actualización de configuración
- [ ] Requiere instalación de nuevas dependencias

---

<!-- 
Checklist final antes de enviar:
- He leído el CONTRIBUTING.md
- He probado los cambios localmente  
- He verificado que no rompo funcionalidad existente
- He proporcionado suficiente contexto para la revisión
-->

**¿Listo para review?** 🎉
