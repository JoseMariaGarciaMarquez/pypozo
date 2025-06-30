"""
PyPozo 2.0 - Motor de Visualización
===================================

WellPlotter proporciona capacidades de visualización profesional
para registros geofísicos, incluyendo plots estándar, correlaciones,
histogramas y análisis interpretativo.

Tipos de visualización:
- Log tracks estándar (GR, RT, RHOB, NPHI)
- Plots petrofísicos (VSH, porosidad, saturación)
- Histogramas y estadísticas
- Correlaciones cruzadas
- Mapas de calor
- Interpretación automática

Autor: José María García Márquez
Fecha: Junio 2025
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import pandas as pd

# Matplotlib para visualización
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import seaborn as sns

from ..core.well import WellManager

logger = logging.getLogger(__name__)

class WellPlotter:
    """
    Motor de visualización para pozos.
    
    Esta clase genera visualizaciones profesionales de registros
    geofísicos con opciones de personalización y exportación.
    """
    
    def __init__(self, style: str = 'professional'):
        """
        Inicializar plotter.
        
        Args:
            style: Estilo de visualización ('professional', 'simple', 'publication')
        """
        self.style = style
        self._setup_matplotlib_style()
        
        logger.info(f"📊 WellPlotter inicializado con estilo: {style}")
    
    def _setup_matplotlib_style(self):
        """Configurar estilo de matplotlib."""
        if self.style == 'professional':
            plt.style.use('seaborn-v0_8-whitegrid')
            self.colors = {
                'gr': '#2E8B57',      # Verde para GR
                'rt': '#DC143C',      # Rojo para resistividad
                'rhob': '#4169E1',    # Azul para densidad
                'nphi': '#FF8C00',    # Naranja para neutrón
                'vsh': '#8B4513',     # Marrón para VSH
                'porosity': '#00CED1', # Cyan para porosidad
                'saturation': '#9932CC' # Púrpura para saturación
            }
        
        # Configuraciones globales
        plt.rcParams['figure.dpi'] = 150
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 9
    
    def plot_standard_logs(self, well: WellManager, 
                          curves: Optional[List[str]] = None,
                          depth_range: Optional[Tuple[float, float]] = None,
                          save_path: Optional[Union[str, Path]] = None) -> Optional[plt.Figure]:
        """
        Crear plot estándar de registros geofísicos.
        
        Args:
            well: WellManager con datos
            curves: Lista de curvas a plotear (None para automático)
            depth_range: Rango de profundidad a mostrar
            save_path: Ruta para guardar (None para mostrar)
            
        Returns:
            plt.Figure: Figura de matplotlib
        """
        if not well.is_valid:
            logger.error("❌ Pozo no válido para plotting")
            return None
        
        # Seleccionar curvas automáticamente si no se especifican
        if curves is None:
            available_curves = well.curves
            standard_curves = ['GR', 'RT', 'RHOB', 'NPHI']
            curves = [c for c in standard_curves if c in available_curves]
            
            if not curves:
                curves = available_curves[:4]  # Primeras 4 curvas disponibles
        
        # Obtener datos
        df = well.get_curves_dataframe(curves)
        if df.empty:
            logger.warning("⚠️ No hay datos para plotear")
            return None
        
        # Aplicar rango de profundidad si se especifica
        if depth_range:
            df = df[(df.index >= depth_range[0]) & (df.index <= depth_range[1])]
        
        # Crear figura con subplots
        fig, axes = plt.subplots(1, len(curves), figsize=(3*len(curves), 10), sharey=True)
        if len(curves) == 1:
            axes = [axes]
        
        fig.suptitle(f'Registros Geofísicos - {well.name}', fontsize=14, fontweight='bold')
        
        for i, curve in enumerate(curves):
            ax = axes[i]
            
            if curve in df.columns:
                # Plotear curva
                color = self.colors.get(curve.lower(), '#1f77b4')
                ax.plot(df[curve], df.index, color=color, linewidth=1.5, label=curve)
                
                # Configurar eje
                ax.set_xlabel(f'{curve}')
                ax.grid(True, alpha=0.3)
                ax.invert_yaxis()  # Profundidad aumenta hacia abajo
                
                # Solo mostrar ylabel en el primer subplot
                if i == 0:
                    ax.set_ylabel('Profundidad (m)')
                
                # Agregar estadísticas básicas
                stats_text = f'Min: {df[curve].min():.2f}\nMax: {df[curve].max():.2f}\nMedia: {df[curve].mean():.2f}'
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                       verticalalignment='top', fontsize=8,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Guardar o mostrar
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"📊 Plot estándar guardado: {save_path}")
        
        return fig
    
    def plot_petrophysical_analysis(self, well: WellManager,
                                   vsh_data: Optional[pd.Series] = None,
                                   porosity_data: Optional[pd.Series] = None,
                                   saturation_data: Optional[pd.Series] = None,
                                   save_path: Optional[Union[str, Path]] = None) -> Optional[plt.Figure]:
        """
        Crear plot de análisis petrofísico.
        
        Args:
            well: WellManager con datos
            vsh_data: Datos de VSH calculado
            porosity_data: Datos de porosidad calculada
            saturation_data: Datos de saturación calculada
            save_path: Ruta para guardar
            
        Returns:
            plt.Figure: Figura de matplotlib
        """
        # Crear figura con grid personalizado
        fig = plt.figure(figsize=(12, 10))
        gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        fig.suptitle(f'Análisis Petrofísico - {well.name}', fontsize=14, fontweight='bold')
        
        # Plot 1: VSH vs Profundidad
        if vsh_data is not None and len(vsh_data) > 0:
            ax1 = fig.add_subplot(gs[0, 0])
            ax1.plot(vsh_data, vsh_data.index, color=self.colors['vsh'], linewidth=1.5)
            ax1.set_xlabel('VSH (fracción)')
            ax1.set_ylabel('Profundidad (m)')
            ax1.set_title('Volumen de Lutitas')
            ax1.grid(True, alpha=0.3)
            ax1.invert_yaxis()
            ax1.set_xlim(0, 1)
        
        # Plot 2: Porosidad vs Profundidad
        if porosity_data is not None and len(porosity_data) > 0:
            ax2 = fig.add_subplot(gs[0, 1])
            ax2.plot(porosity_data, porosity_data.index, color=self.colors['porosity'], linewidth=1.5)
            ax2.set_xlabel('Porosidad (fracción)')
            ax2.set_title('Porosidad')
            ax2.grid(True, alpha=0.3)
            ax2.invert_yaxis()
            ax2.set_xlim(0, 0.4)
        
        # Plot 3: Saturación vs Profundidad
        if saturation_data is not None and len(saturation_data) > 0:
            ax3 = fig.add_subplot(gs[0, 2])
            ax3.plot(saturation_data, saturation_data.index, color=self.colors['saturation'], linewidth=1.5)
            ax3.set_xlabel('Sw (fracción)')
            ax3.set_title('Saturación de Agua')
            ax3.grid(True, alpha=0.3)
            ax3.invert_yaxis()
            ax3.set_xlim(0, 1)
        
        # Plot 4: Histograma de VSH
        if vsh_data is not None and len(vsh_data) > 0:
            ax4 = fig.add_subplot(gs[1, 0])
            ax4.hist(vsh_data.dropna(), bins=30, alpha=0.7, color=self.colors['vsh'], edgecolor='black')
            ax4.set_xlabel('VSH (fracción)')
            ax4.set_ylabel('Frecuencia')
            ax4.set_title('Distribución VSH')
            ax4.grid(True, alpha=0.3)
        
        # Plot 5: Scatter Porosidad vs VSH
        if vsh_data is not None and len(vsh_data) > 0 and porosity_data is not None and len(porosity_data) > 0:
            ax5 = fig.add_subplot(gs[1, 1])
            ax5.scatter(vsh_data, porosity_data, alpha=0.6, s=10)
            ax5.set_xlabel('VSH (fracción)')
            ax5.set_ylabel('Porosidad (fracción)')
            ax5.set_title('Porosidad vs VSH')
            ax5.grid(True, alpha=0.3)
        
        # Plot 6: Scatter Saturación vs Porosidad
        if porosity_data is not None and len(porosity_data) > 0 and saturation_data is not None and len(saturation_data) > 0:
            ax6 = fig.add_subplot(gs[1, 2])
            ax6.scatter(porosity_data, saturation_data, alpha=0.6, s=10)
            ax6.set_xlabel('Porosidad (fracción)')
            ax6.set_ylabel('Sw (fracción)')
            ax6.set_title('Saturación vs Porosidad')
            ax6.grid(True, alpha=0.3)
        
        # Guardar o mostrar
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"📊 Plot petrofísico guardado: {save_path}")
        
        return fig
    
    def plot_correlation_matrix(self, well: WellManager,
                               curves: Optional[List[str]] = None,
                               save_path: Optional[Union[str, Path]] = None) -> Optional[plt.Figure]:
        """
        Crear matriz de correlación entre curvas.
        
        Args:
            well: WellManager con datos
            curves: Lista de curvas (None para todas)
            save_path: Ruta para guardar
            
        Returns:
            plt.Figure: Figura de matplotlib
        """
        df = well.get_curves_dataframe(curves)
        if df.empty:
            logger.warning("⚠️ No hay datos para matriz de correlación")
            return None
        
        # Calcular matriz de correlación
        corr_matrix = df.corr()
        
        # Crear heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0,
                   square=True, ax=ax, cbar_kws={'label': 'Correlación'})
        
        ax.set_title(f'Matriz de Correlación - {well.name}', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Guardar o mostrar
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"📊 Matriz de correlación guardada: {save_path}")
        
        return fig
    
    def plot_well_summary(self, well: WellManager,
                         save_path: Optional[Union[str, Path]] = None) -> Optional[plt.Figure]:
        """
        Crear plot resumen completo del pozo.
        
        Args:
            well: WellManager con datos
            save_path: Ruta para guardar
            
        Returns:
            plt.Figure: Figura de matplotlib
        """
        # Crear figura compleja con múltiples subplots
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 4, figure=fig, hspace=0.3, wspace=0.3)
        
        fig.suptitle(f'Resumen Completo - {well.name}', fontsize=16, fontweight='bold')
        
        # Obtener datos principales
        df = well.get_curves_dataframe()
        
        # Plot 1-2: Registros principales (ocupa 2 columnas)
        ax_main = fig.add_subplot(gs[:, :2])
        
        main_curves = ['GR', 'RT', 'RHOB', 'NPHI']
        available_main = [c for c in main_curves if c in df.columns]
        
        if available_main:
            for i, curve in enumerate(available_main):
                if curve in df.columns:
                    # Normalizar datos para plotting conjunto
                    norm_data = (df[curve] - df[curve].min()) / (df[curve].max() - df[curve].min())
                    color = self.colors.get(curve.lower(), f'C{i}')
                    ax_main.plot(norm_data + i*1.2, df.index, color=color, linewidth=1.5, label=curve)
            
            ax_main.set_xlabel('Curvas Normalizadas')
            ax_main.set_ylabel('Profundidad (m)')
            ax_main.set_title('Registros Principales')
            ax_main.legend()
            ax_main.grid(True, alpha=0.3)
            ax_main.invert_yaxis()
        
        # Plot 3: Histograma de GR
        if 'GR' in df.columns:
            ax3 = fig.add_subplot(gs[0, 2])
            ax3.hist(df['GR'].dropna(), bins=30, alpha=0.7, color=self.colors['gr'], edgecolor='black')
            ax3.set_xlabel('GR (API)')
            ax3.set_ylabel('Frecuencia')
            ax3.set_title('Distribución GR')
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Estadísticas del pozo
        ax4 = fig.add_subplot(gs[0, 3])
        ax4.axis('off')
        
        # Texto con estadísticas
        stats_text = f"""
        ESTADÍSTICAS DEL POZO
        ═══════════════════
        Nombre: {well.name}
        
        Profundidad:
        • Mínima: {well.depth_range[0]:.1f} m
        • Máxima: {well.depth_range[1]:.1f} m
        • Intervalo: {well.depth_range[1] - well.depth_range[0]:.1f} m
        
        Curvas disponibles: {len(well.curves)}
        {', '.join(well.curves[:5])}
        {'...' if len(well.curves) > 5 else ''}
        
        Datos válidos:
        • Total puntos: {len(df)}
        • Completitud: {(1 - df.isnull().sum().sum()/(len(df)*len(df.columns))):.1%}
        """
        
        ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, 
                verticalalignment='top', fontsize=9, fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        # Plots adicionales según datos disponibles
        plot_row = 1
        
        # Plot 5: Scatter plot si hay múltiples curvas
        if len(df.columns) >= 2:
            ax5 = fig.add_subplot(gs[plot_row, 2])
            curve1, curve2 = df.columns[0], df.columns[1]
            ax5.scatter(df[curve1], df[curve2], alpha=0.6, s=10)
            ax5.set_xlabel(curve1)
            ax5.set_ylabel(curve2)
            ax5.set_title(f'{curve1} vs {curve2}')
            ax5.grid(True, alpha=0.3)
        
        # Plot 6: Información de calidad de datos
        ax6 = fig.add_subplot(gs[plot_row, 3])
        
        # Calcular completitud por curva
        completeness = (1 - df.isnull().sum() / len(df)) * 100
        
        if len(completeness) > 0:
            bars = ax6.barh(range(len(completeness)), completeness.values)
            ax6.set_yticks(range(len(completeness)))
            ax6.set_yticklabels(completeness.index)
            ax6.set_xlabel('Completitud (%)')
            ax6.set_title('Calidad de Datos')
            ax6.grid(True, alpha=0.3)
            
            # Colorear barras según completitud
            for i, bar in enumerate(bars):
                if completeness.iloc[i] >= 90:
                    bar.set_color('green')
                elif completeness.iloc[i] >= 70:
                    bar.set_color('orange')
                else:
                    bar.set_color('red')
        
        # Guardar o mostrar
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"📊 Resumen completo guardado: {save_path}")
        
        return fig
    
    def generate_interpretation_report(self, well: WellManager,
                                     geophysics_results: Optional[Dict] = None,
                                     save_path: Optional[Union[str, Path]] = None) -> str:
        """
        Generar reporte de interpretación textual.
        
        Args:
            well: WellManager con datos
            geophysics_results: Resultados de análisis geofísico
            save_path: Ruta para guardar reporte
            
        Returns:
            str: Texto del reporte
        """
        depth_min, depth_max = well.depth_range
        
        report_lines = [
            f"REPORTE DE INTERPRETACIÓN GEOFÍSICA",
            f"=" * 50,
            f"Pozo: {well.name}",
            f"Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"INFORMACIÓN GENERAL:",
            f"• Intervalo analizado: {depth_min:.1f} - {depth_max:.1f} m",
            f"• Espesor total: {depth_max - depth_min:.1f} m",
            f"• Curvas disponibles: {len(well.curves)}",
            f"  - {', '.join(well.curves)}",
            f"",
        ]
        
        # Análisis de curvas básicas
        df = well.get_curves_dataframe()
        
        if 'GR' in df.columns:
            gr_stats = df['GR'].describe()
            report_lines.extend([
                f"ANÁLISIS DE GAMMA RAY:",
                f"• Valor promedio: {gr_stats['mean']:.1f} API",
                f"• Rango: {gr_stats['min']:.1f} - {gr_stats['max']:.1f} API",
                f"• Interpretación: {'Secuencia arcillosa' if gr_stats['mean'] > 80 else 'Secuencia arenosa'}",
                f"",
            ])
        
        if 'RHOB' in df.columns:
            rhob_stats = df['RHOB'].describe()
            report_lines.extend([
                f"ANÁLISIS DE DENSIDAD:",
                f"• Densidad promedio: {rhob_stats['mean']:.2f} g/cm³",
                f"• Rango: {rhob_stats['min']:.2f} - {rhob_stats['max']:.2f} g/cm³",
                f"• Interpretación: {'Formación densa' if rhob_stats['mean'] > 2.5 else 'Formación porosa'}",
                f"",
            ])
        
        # Agregar resultados geofísicos si están disponibles
        if geophysics_results and geophysics_results.get('success'):
            results = geophysics_results.get('results', {})
            
            if 'reservoir_zones' in results:
                zones = results['reservoir_zones']
                report_lines.extend([
                    f"ANÁLISIS DE YACIMIENTO:",
                    f"• Zonas de interés identificadas: {zones['zones_identified']}",
                    f"• Espesor neto estimado: {zones['total_thickness']:.1f} m",
                    f"• Criterios aplicados:",
                    f"  - VSH < {zones['criteria']['vsh_cutoff']}",
                    f"  - Porosidad > {zones['criteria']['porosity_cutoff']}",
                    f"  - Sw < {zones['criteria']['saturation_cutoff']}",
                    f"",
                ])
            
            if 'vsh' in results:
                vsh_stats = results['vsh']
                report_lines.extend([
                    f"VOLUMEN DE LUTITAS (VSH):",
                    f"• VSH promedio: {vsh_stats['mean']:.3f} ({vsh_stats['mean']*100:.1f}%)",
                    f"• Rango: {vsh_stats['min']:.3f} - {vsh_stats['max']:.3f}",
                    f"• Calidad del yacimiento: {'Buena' if vsh_stats['mean'] < 0.3 else 'Regular' if vsh_stats['mean'] < 0.5 else 'Pobre'}",
                    f"",
                ])
            
            if 'porosity' in results:
                phi_stats = results['porosity']
                report_lines.extend([
                    f"POROSIDAD:",
                    f"• Porosidad promedio: {phi_stats['mean']:.3f} ({phi_stats['mean']*100:.1f}%)",
                    f"• Rango: {phi_stats['min']:.3f} - {phi_stats['max']:.3f}",
                    f"• Calidad del yacimiento: {'Excelente' if phi_stats['mean'] > 0.15 else 'Buena' if phi_stats['mean'] > 0.08 else 'Pobre'}",
                    f"",
                ])
        
        # Recomendaciones
        report_lines.extend([
            f"RECOMENDACIONES:",
            f"• Análisis adicionales recomendados:",
            f"  - Análisis de núcleos si están disponibles",
            f"  - Pruebas de formación en zonas de interés",
            f"  - Correlación con pozos vecinos",
            f"• Consideraciones operacionales:",
            f"  - Evaluar riesgos de perforación",
            f"  - Optimizar diseño de completación",
            f"",
            f"═" * 50,
            f"Reporte generado por PyPozo 2.0",
        ])
        
        report_text = "\n".join(report_lines)
        
        # Guardar si se especifica ruta
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"📄 Reporte de interpretación guardado: {save_path}")
        
        return report_text

    def plot_well_logs(self, well: 'WellManager', curves: List[str], 
                      title: str = "Registros Geofísicos", show_grid: bool = True,
                      save_path: Optional[Path] = None, figsize: Tuple[int, int] = (12, 10),
                      show: bool = True) -> Optional[Path]:
        """
        Crear gráfico de registros geofísicos con mejoras automáticas.
        
        Args:
            well: Instancia de WellManager
            curves: Lista de curvas a graficar
            title: Título del gráfico
            show_grid: Mostrar grilla
            save_path: Ruta para guardar (opcional)
            figsize: Tamaño de la figura
            show: Mostrar el gráfico
            
        Returns:
            Path: Ruta del archivo guardado (si se especifica)
        """
        # Usar la versión mejorada con escala logarítmica automática
        return self.plot_well_logs_enhanced(
            well=well,
            curves=curves,
            title=title,
            show_grid=show_grid,
            save_path=save_path,
            figsize=figsize
        )
        """
        Crear gráfico de registros geofísicos.
        
        Args:
            well: Instancia de WellManager
            curves: Lista de curvas a graficar
            title: Título del gráfico
            show_grid: Mostrar grilla
            save_path: Ruta para guardar (opcional)
            figsize: Tamaño de la figura
            
        Returns:
            Path: Ruta del archivo guardado (si se especifica)
        """
        logger.info(f"📊 Graficando registros: {curves}")
        
        # Validar curvas disponibles
        available_curves = well.curves
        valid_curves = [curve for curve in curves if curve in available_curves]
        
        if not valid_curves:
            logger.error(f"❌ No se encontraron curvas válidas: {curves}")
            logger.info(f"💡 Curvas disponibles: {available_curves}")
            return None
        
        # Obtener datos del pozo
        try:
            df = well._well.df()  # Usar el DataFrame de Welly
            if df is None or df.empty:
                logger.error("❌ No hay datos en el pozo")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos: {str(e)}")
            return None
        
        # Crear figura con mejor espaciado
        n_curves = len(valid_curves)
        # Ajustar el ancho según el número de curvas para evitar superposición
        width_per_curve = max(4, 12 / n_curves)  # Mínimo 4 pulgadas por curva
        fig_width = min(width_per_curve * n_curves, 20)  # Máximo 20 pulgadas
        
        fig, axes = plt.subplots(1, n_curves, figsize=(fig_width, figsize[1]), sharey=True)
        
        # Si solo hay una curva, convertir a lista
        if n_curves == 1:
            axes = [axes]
        
        # Configurar estilo
        try:
            plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        except:
            pass
        
        # Colores profesionales para las curvas
        colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00', '#8B4513', '#00CED1', '#9932CC', '#FF1493']
        
        # Graficar cada curva
        for i, curve_name in enumerate(valid_curves):
            ax = axes[i]
            
            # Obtener datos de la curva
            if curve_name in df.columns:
                curve_data = df[curve_name].dropna()
                
                # Verificar que hay datos válidos
                if curve_data is None or len(curve_data) == 0:
                    logger.warning(f"⚠️ Curva {curve_name} no tiene datos válidos")
                    continue
                    
                depth = curve_data.index
                values = curve_data.values
                
                # Graficar
                color = colors[i % len(colors)]
                ax.plot(values, depth, linewidth=1.5, color=color, label=curve_name)
                ax.fill_betweenx(depth, values, alpha=0.3, color=color)
                
                # Configurar ejes with mejor espaciado
                ax.set_xlabel(f'{curve_name}', fontsize=11, fontweight='bold', labelpad=8)
                ax.set_title(f'{curve_name}', fontsize=12, fontweight='bold', pad=15)
                ax.invert_yaxis()  # Profundidad aumenta hacia abajo (como en geología)
                
                # Configurar grilla
                if show_grid:
                    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.3, which='minor')
                
                # Estadísticas en el gráfico - posición optimizada
                stats_text = f'N: {len(values)}\nMin: {values.min():.1f}\nMax: {values.max():.1f}\nμ: {values.mean():.1f}\nσ: {values.std():.1f}'
                
                # Calcular posición óptima para las estadísticas
                text_x = 0.02 if i == 0 else 0.98
                text_align = 'left' if i == 0 else 'right'
                
                ax.text(text_x, 0.02, stats_text, transform=ax.transAxes, 
                       verticalalignment='bottom', horizontalalignment=text_align,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='gray'),
                       fontsize=8, fontfamily='monospace')
                
                logger.info(f"✅ Curva {curve_name} graficada: {len(values)} puntos")
            else:
                logger.warning(f"⚠️ Curva {curve_name} no encontrada en datos")
        
        # Configurar eje Y común (profundidad) with mejor formato
        axes[0].set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold', labelpad=10)
        
        # Título principal con mejor espaciado
        title_text = f'{title}\nPozo: {well.name} | Intervalo: {well.depth_range[0]:.0f}-{well.depth_range[1]:.0f}m'
        fig.suptitle(title_text, fontsize=14, fontweight='bold', y=0.96)
        
        # Ajustar layout con espaciado optimizado
        plt.tight_layout()
        plt.subplots_adjust(top=0.88, bottom=0.12, left=0.08, right=0.95, wspace=0.3)
        
        # Guardar si se especifica
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
                logger.info(f"💾 Gráfico guardado en: {save_path}")
            except Exception as e:
                logger.error(f"❌ Error guardando gráfico: {str(e)}")
        
        # Mostrar gráfico
        plt.show()
        
        return save_path if save_path else None

    def plot_multiple_curves(self, well: 'WellManager', 
                           title: str = "Análisis Multi-Curva", 
                           save_path: Optional[Path] = None) -> Optional[Path]:
        """
        Graficar todas las curvas disponibles en el pozo.
        
        Args:
            well: Instancia de WellManager
            title: Título del gráfico
            save_path: Ruta para guardar (opcional)
            
        Returns:
            Path: Ruta del archivo guardado (si se especifica)
        """
        logger.info(f"📊 Graficando todas las curvas del pozo: {well.name}")
        
        # Obtener todas las curvas disponibles
        curves = well.curves
        if not curves:
            logger.error("❌ No hay curvas disponibles")
            return None
        
        return self.plot_well_logs(
            well=well,
            curves=curves,
            title=title,
            save_path=save_path,
            figsize=(max(4*len(curves), 12), 12)
        )

    def plot_well_comparison(self, wells: List['WellManager'], curve: str = "GR",
                           title: str = "Comparación de Pozos", 
                           save_path: Optional[Path] = None) -> Optional[Path]:
        """
        Comparar la misma curva entre múltiples pozos.
        
        Args:
            wells: Lista de WellManager
            curve: Curva a comparar
            title: Título del gráfico
            save_path: Ruta para guardar (opcional)
            
        Returns:
            Path: Ruta del archivo guardado (si se especifica)
        """
        logger.info(f"📊 Comparando curva {curve} entre {len(wells)} pozos")
        
        # Validar que todos los pozos tengan la curva
        valid_wells = []
        for well in wells:
            if curve in well.curves:
                valid_wells.append(well)
            else:
                logger.warning(f"⚠️ Pozo {well.name} no tiene curva {curve}")
        
        if not valid_wells:
            logger.error(f"❌ Ningún pozo tiene la curva {curve}")
            return None
        
        # Crear figura
        fig, ax = plt.subplots(1, 1, figsize=(10, 12))
        
        # Colores para cada pozo
        colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00', '#8B4513', '#00CED1', '#9932CC', '#FF1493']
        
        # Graficar cada pozo
        for i, well in enumerate(valid_wells):
            curve_data = well.get_curve_data(curve)
            if curve_data is not None and len(curve_data) > 0:
                color = colors[i % len(colors)]
                ax.plot(curve_data.values, curve_data.index, 
                       color=color, linewidth=1.5, label=f'{well.name}', alpha=0.8)
        
        # Configurar ejes
        ax.set_xlabel(f'{curve}', fontsize=12, fontweight='bold')
        ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
        ax.set_title(f'{title}\nCurva: {curve}', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', framealpha=0.9)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar si se especifica
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
                logger.info(f"💾 Comparación guardada en: {save_path}")
            except Exception as e:
                logger.error(f"❌ Error guardando comparación: {str(e)}")
        
        # Mostrar gráfico
        plt.show()
        
        return save_path if save_path else None

    def plot_selected_curves(self, well: 'WellManager', curves: List[str],
                           title: str = "Registros Seleccionados", 
                           save_path: Optional[Path] = None) -> Optional[Path]:
        """
        Graficar curvas específicas seleccionadas por el usuario.
        
        Args:
            well: Instancia de WellManager
            curves: Lista de curvas específicas a graficar
            title: Título del gráfico
            save_path: Ruta para guardar (opcional)
            
        Returns:
            Path: Ruta del archivo guardado (si se especifica)
        """
        logger.info(f"📊 Graficando curvas seleccionadas: {curves}")
        
        # Validar que las curvas existan
        available_curves = well.curves
        valid_curves = []
        missing_curves = []
        
        for curve in curves:
            if curve in available_curves:
                valid_curves.append(curve)
            else:
                missing_curves.append(curve)
        
        if missing_curves:
            logger.warning(f"⚠️ Curvas no encontradas: {missing_curves}")
            logger.info(f"💡 Curvas disponibles: {available_curves}")
        
        if not valid_curves:
            logger.error("❌ Ninguna de las curvas solicitadas está disponible")
            return None
        
        # Usar el método plot_well_logs con las curvas válidas
        return self.plot_well_logs(
            well=well,
            curves=valid_curves,
            title=title,
            save_path=save_path,
            figsize=(max(4 * len(valid_curves), 8), 12)  # Tamaño dinámico
        )

    def plot_curves_together(self, well: 'WellManager', curves: List[str], 
                           title: str = "Registros Combinados", 
                           normalize: bool = True,
                           use_log_scale: bool = None,
                           save_path: Optional[Path] = None,
                           figsize: Tuple[int, int] = (12, 10)) -> Optional[Path]:
        """
        Graficar múltiples curvas en la misma figura (mismo eje X) con unidades.
        
        Args:
            well: Instancia de WellManager
            curves: Lista de curvas a graficar juntas
            title: Título del gráfico
            normalize: Si normalizar las curvas para comparación visual
            use_log_scale: Forzar escala logarítmica (None = automático basado en unidades)
            save_path: Ruta para guardar (opcional)
            figsize: Tamaño de la figura
            
        Returns:
            Path: Ruta del archivo guardado (si se especifica)
        """
        logger.info(f"📊 Graficando curvas juntas: {curves}")
        
        # Validar curvas disponibles
        available_curves = well.curves
        valid_curves = [curve for curve in curves if curve in available_curves]
        
        if not valid_curves:
            logger.error(f"❌ No se encontraron curvas válidas: {curves}")
            return None
        
        try:
            # Obtener datos del pozo
            df = well._well.df()
            if df.empty:
                logger.error("❌ No hay datos en el pozo")
                return None
            
            # Crear figura
            fig, ax = plt.subplots(figsize=figsize)
            
            # Colores para cada curva
            colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00', '#8B4513', '#00CED1', '#9932CC', '#FF1493']
            
            # Detectar si usar escala logarítmica
            if use_log_scale is None:
                # Verificar si alguna curva es eléctrica
                has_electrical = any(self._is_electrical_curve(curve, well) for curve in valid_curves)
                use_log_scale = has_electrical
            
            # Obtener unidades comunes
            units_list = []
            for curve_name in valid_curves:
                units = well.get_curve_units(curve_name)
                if units:
                    units_list.append(units)
            
            # Determinar unidades para el xlabel
            if units_list:
                # Si todas las unidades son iguales, usar esa
                unique_units = list(set(units_list))
                if len(unique_units) == 1:
                    xlabel_units = unique_units[0]
                else:
                    xlabel_units = " / ".join(unique_units)
            else:
                xlabel_units = "Valores"
            
            # Graficar cada curva
            for i, curve_name in enumerate(valid_curves):
                if curve_name in df.columns:
                    curve_data = df[curve_name].dropna()
                    
                    if len(curve_data) == 0:
                        logger.warning(f"⚠️ Curva {curve_name} no tiene datos válidos")
                        continue
                    
                    depth = curve_data.index
                    values = curve_data.values
                    
                    # Normalizar valores si se solicita
                    if normalize and len(valid_curves) > 1:
                        # Escalar cada curva al rango 0-1 para poder compararlas
                        values_normalized = (values - values.min()) / (values.max() - values.min())
                        plot_values = values_normalized
                        curve_label = f"{curve_name} (normalizado)"
                    else:
                        plot_values = values
                        curve_label = curve_name
                    
                    color = colors[i % len(colors)]
                    ax.plot(plot_values, depth, linewidth=2, color=color, 
                           label=curve_label, alpha=0.8)
            
            # Configurar ejes
            if normalize and len(valid_curves) > 1:
                xlabel = 'Valores Normalizados (0-1)'
            else:
                xlabel = f'Valores ({xlabel_units})'
            
            ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
            ax.set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold')
            ax.set_title(f'{title}\nPozo: {well.name}', fontsize=14, fontweight='bold')
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best', framealpha=0.9)
            
            # Aplicar escala logarítmica si es necesario
            if use_log_scale and not normalize:
                ax.set_xscale('log')
                logger.info("📊 Aplicando escala logarítmica al eje X")
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar si se especifica
            if save_path:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"💾 Gráfico guardado: {save_path}")
                plt.close(fig)
                return save_path
            else:
                plt.show()
                return None
                
        except Exception as e:
            logger.error(f"❌ Error graficando curvas juntas: {str(e)}")
            return None
    
    def _is_electrical_curve(self, curve_name: str, well: 'WellManager' = None) -> bool:
        """
        Determinar si una curva es de resistividad eléctrica basándose en nombre y unidades.
        
        Args:
            curve_name: Nombre de la curva
            well: Instancia de WellManager para obtener unidades
            
        Returns:
            bool: True si es curva eléctrica
        """
        # Primero verificar por unidades si tenemos acceso al pozo
        if well:
            units = well.get_curve_units(curve_name).upper()
            if 'OHM' in units or 'OHMM' in units or 'OHMS' in units:
                return True
        
        # Si no hay unidades, verificar por patrones de nombre
        electrical_patterns = [
            'RT', 'R_', 'RES', 'RESIST', 'ILM', 'ILD', 'SFLU', 'MSFL',
            'M1R', 'M2R', 'M3R', 'M4R', 'M5R', 'M6R', 'M7R', 'M8R', 'M9R',
            'AT10', 'AT20', 'AT30', 'AT60', 'AT90',
            'LLD', 'LLS', 'RLLD', 'RLLS', 'RXO'
        ]
        
        curve_upper = curve_name.upper()
        return any(pattern in curve_upper for pattern in electrical_patterns)
    
    def plot_well_logs_enhanced(self, well: 'WellManager', curves: List[str], 
                               title: str = "Registros Geofísicos Mejorados", 
                               show_grid: bool = True,
                               save_path: Optional[Path] = None, 
                               figsize: Tuple[int, int] = (14, 10)) -> Optional[Path]:
        """
        Versión mejorada del graficador con eje logarítmico automático para curvas eléctricas.
        
        Args:
            well: Instancia de WellManager
            curves: Lista de curvas a graficar
            title: Título del gráfico
            show_grid: Mostrar grilla
            save_path: Ruta para guardar (opcional)
            figsize: Tamaño de la figura
            
        Returns:
            Path: Ruta del archivo guardado (si se especifica)
        """
        logger.info(f"📊 Graficando registros mejorados: {curves}")
        
        # Validar curvas disponibles
        available_curves = well.curves
        valid_curves = [curve for curve in curves if curve in available_curves]
        
        if not valid_curves:
            logger.error(f"❌ No se encontraron curvas válidas: {curves}")
            return None
        
        try:
            # Obtener datos del pozo
            df = well._well.df()
            if df.empty:
                logger.error("❌ No hay datos en el pozo")
                return None
            
            # Crear figura con subplots
            n_curves = len(valid_curves)
            width_per_curve = max(3, 12 / n_curves)
            fig_width = min(width_per_curve * n_curves, 20)
            
            fig, axes = plt.subplots(1, n_curves, figsize=(fig_width, figsize[1]), sharey=True)
            
            if n_curves == 1:
                axes = [axes]
            
            # Colores profesionales
            colors = ['#2E8B57', '#DC143C', '#4169E1', '#FF8C00', '#8B4513', '#00CED1', '#9932CC', '#FF1493']
            
            # Graficar cada curva
            for i, curve_name in enumerate(valid_curves):
                ax = axes[i]
                
                if curve_name in df.columns:
                    curve_data = df[curve_name].dropna()
                    
                    if len(curve_data) == 0:
                        logger.warning(f"⚠️ Curva {curve_name} no tiene datos válidos")
                        continue
                    
                    depth = curve_data.index
                    values = curve_data.values
                    
                    # Verificar si es curva eléctrica
                    is_electrical = self._is_electrical_curve(curve_name, well)
                    
                    # Obtener unidades
                    units = well.get_curve_units(curve_name)
                    xlabel = f'{curve_name} ({units})' if units else curve_name
                    
                    # Graficar
                    color = colors[i % len(colors)]
                    ax.plot(values, depth, linewidth=1.5, color=color, label=curve_name)
                    ax.fill_betweenx(depth, values, alpha=0.3, color=color)
                    
                    # Configurar eje X
                    if is_electrical:
                        # Usar escala logarítmica para curvas eléctricas
                        ax.set_xscale('log')
                        logger.info(f"🔌 Aplicando escala logarítmica a {curve_name}")
                    
                    # Configurar ejes
                    ax.set_xlabel(xlabel, fontsize=11, fontweight='bold', labelpad=8)
                    title_text = f'{curve_name}'
                    if is_electrical:
                        title_text += ' (log)'
                    ax.set_title(title_text, fontsize=12, fontweight='bold', pad=15)
                    ax.invert_yaxis()
                    
                    # Configurar grilla
                    if show_grid:
                        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
                        if is_electrical:
                            ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.3, which='minor')
                    
                    # Estadísticas
                    if is_electrical:
                        # Para curvas eléctricas, mostrar rango en log
                        stats_text = f'N: {len(values)}\nMin: {values.min():.1f}\nMax: {values.max():.1f}\nGM: {np.exp(np.log(values).mean()):.1f}'
                    else:
                        stats_text = f'N: {len(values)}\nMin: {values.min():.1f}\nMax: {values.max():.1f}\nμ: {values.mean():.1f}'
                    
                    # Posición de estadísticas
                    text_x = 0.02 if i == 0 else 0.98
                    text_align = 'left' if i == 0 else 'right'
                    
                    ax.text(text_x, 0.02, stats_text, transform=ax.transAxes,
                           verticalalignment='bottom', horizontalalignment=text_align,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='gray'),
                           fontsize=8, fontfamily='monospace')
                    
                    logger.info(f"✅ Curva {curve_name} graficada: {len(values)} puntos {'(log)' if is_electrical else ''}")
                else:
                    logger.warning(f"⚠️ Curva {curve_name} no encontrada en datos")
            
            # Configurar eje Y común
            axes[0].set_ylabel('Profundidad (m)', fontsize=12, fontweight='bold', labelpad=10)
            
            # Título principal
            title_text = f'{title}\nPozo: {well.name} | Intervalo: {well.depth_range[0]:.0f}-{well.depth_range[1]:.0f}m'
            fig.suptitle(title_text, fontsize=14, fontweight='bold', y=0.96)
            
            # Ajustar layout
            try:
                plt.tight_layout()
                plt.subplots_adjust(top=0.9, wspace=0.3)
            except:
                logger.warning("⚠️ Layout automático no aplicado")
            
            # Guardar o mostrar
            if save_path:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"💾 Gráfico guardado: {save_path}")
                plt.close(fig)
                return save_path
            else:
                plt.show()
                return None
                
        except Exception as e:
            logger.error(f"❌ Error graficando registros mejorados: {str(e)}")
            return None
