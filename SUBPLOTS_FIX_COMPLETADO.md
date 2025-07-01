# Corrección de Subplots - Eje de Profundidad Compartido

## Problema Identificado

Cuando PyPozo 2.0 genera subplots para múltiples curvas con diferentes rangos de profundidad, cada subplot se mostraba en su propio rango individual, resultando en una visualización incorrecta donde las curvas no podían compararse adecuadamente.

**Ejemplo del problema:**
- Curva GR: profundidad de 200m a 800m
- Curva SP: profundidad de 1000m a 1100m

Cada curva se mostraba en su propio rango, haciendo imposible la comparación visual correcta.

## Solución Implementada

### 1. Modificación en `_plot_curves_to_figure()`

Se modificó la función `_plot_curves_to_figure()` en `pypozo_app.py` para:

1. **Calcular rango común de profundidad:**
   ```python
   # Determinar el rango de profundidad común para todos los subplots
   all_depths = []
   valid_curves = []
   
   # Recopilar todos los datos válidos y sus rangos de profundidad
   for curve_name in curves:
       # ... procesamiento de datos ...
       all_depths.extend(valid_depth)
       
   # Calcular rango común
   common_depth_min = min(all_depths)
   common_depth_max = max(all_depths)
   ```

2. **Crear subplots con eje Y compartido:**
   ```python
   for i, (curve_name, depth, values) in enumerate(valid_curves):
       if i == 0:
           # Primer subplot
           ax = self.figure.add_subplot(1, len(valid_curves), i + 1)
           axes.append(ax)
       else:
           # Subplots subsecuentes comparten el eje Y
           ax = self.figure.add_subplot(1, len(valid_curves), i + 1, sharey=axes[0])
           axes.append(ax)
   ```

3. **Aplicar rango común a todos los subplots:**
   ```python
   # Establecer el rango de profundidad común para todos los subplots
   ax.set_ylim(common_depth_max, common_depth_min)  # Invertido para profundidad
   ```

4. **Optimizar etiquetas Y:**
   ```python
   # Solo el primer subplot tiene etiqueta Y
   if i == 0:
       ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
   else:
       # Ocultar etiquetas del eje Y en subplots subsecuentes
       ax.set_yticklabels([])
   ```

### 2. Actualización del título

Se corrigió también un título duplicado y se mejoró la información mostrada:

```python
# Título principal con rango común
title = f'{well.name} | Profundidad: {common_depth_min:.0f}-{common_depth_max:.0f}m | {len(valid_curves)} curvas'
self.figure.suptitle(title, fontsize=14, fontweight='bold')
```

## Verificación

### Test Automático

Se creó `test_subplots_fix.py` que verifica:

1. Carga de un pozo de prueba
2. Creación de subplots con diferentes curvas
3. Verificación de que todos los subplots tienen el mismo rango Y
4. Generación de imagen de prueba

**Resultado del test:**
```
✅ Todos los subplots comparten el mismo rango Y: (1849.58, 800.0)
✅ TEST EXITOSO: Los subplots comparten correctamente el eje de profundidad
```

### Beneficios de la Corrección

1. **Visualización coherente:** Todas las curvas se muestran en el mismo rango de profundidad
2. **Comparación visual correcta:** Es posible comparar visualmente las curvas a la misma profundidad
3. **Interpretación geológica mejorada:** Los registros pueden correlacionarse correctamente por profundidad
4. **Interfaz más limpia:** Etiquetas Y solo en el primer subplot para evitar redundancia

## Ubicación de Archivos

- **Código corregido:** `pypozo_app.py` (función `_plot_curves_to_figure`)
- **Test de verificación:** `tests/test_subplots_fix.py`
- **Imagen de prueba:** `test_subplots_shared.png`

## Estado

✅ **CORRECCIÓN COMPLETADA Y VERIFICADA**

La funcionalidad de subplots ahora muestra correctamente todos los registros en el mismo eje de profundidad, permitiendo una interpretación adecuada de los datos de pozo.
