"""
PyPozo 2.0 - Workflow Estándar
==============================

StandardWorkflow coordina el procesamiento completo de pozos,
desde la carga hasta la exportación, siguiendo las mejores prácticas
de la industria.

Flujo del workflow:
1. Carga y validación de datos
2. Estandarización de mnemonics y limpieza
3. Cálculos geofísicos estándar
4. Generación de visualizaciones
5. Exportación a múltiples formatos
6. Generación de reportes

Autor: José María García Márquez
Fecha: Junio 2025
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import pandas as pd
from datetime import datetime
import time

from ..core.well import WellManager
from ..core.project import ProjectManager
from ..processors.standardizer import DataStandardizer
from ..processors.calculator import GeophysicsCalculator

logger = logging.getLogger(__name__)

class StandardWorkflow:
    """
    Workflow estándar para procesamiento completo de pozos.
    
    Esta clase coordina todos los pasos del procesamiento de pozos,
    desde la carga inicial hasta la exportación final.
    """
    
    def __init__(self, output_dir: Union[str, Path] = "pypozo_output"):
        """
        Inicializar workflow estándar.
        
        Args:
            output_dir: Directorio de salida para resultados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Inicializar componentes
        self.standardizer = DataStandardizer()
        self.calculator = GeophysicsCalculator()
        
        # Historial de procesamiento
        self.processing_history = []
        
        logger.info(f"🚀 Workflow estándar inicializado. Salida: {self.output_dir}")
    
    def process_single_well(self, well_source: Union[str, Path, WellManager],
                           generate_plots: bool = True,
                           export_formats: List[str] = None,
                           custom_parameters: Dict = None) -> Dict[str, Any]:
        """
        Procesar un pozo individual con workflow completo.
        
        Args:
            well_source: Fuente del pozo (archivo LAS o WellManager)
            generate_plots: Generar visualizaciones
            export_formats: Formatos de exportación ['csv', 'excel', 'json']
            custom_parameters: Parámetros personalizados
            
        Returns:
            Dict: Resultados del procesamiento
        """
        start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("🛢️ INICIANDO WORKFLOW ESTÁNDAR")
        logger.info("=" * 60)
        
        if export_formats is None:
            export_formats = ['csv', 'json']
        
        if custom_parameters is None:
            custom_parameters = {}
        
        results = {
            'success': False,
            'well_name': '',
            'start_time': datetime.now().isoformat(),
            'processing_steps': [],
            'generated_files': [],
            'errors': [],
            'warnings': []
        }
        
        try:
            # PASO 1: Cargar y validar pozo
            logger.info("📁 PASO 1: CARGA Y VALIDACIÓN")
            logger.info("-" * 30)
            
            if isinstance(well_source, WellManager):
                well = well_source
            else:
                well = WellManager.from_las(well_source)
            
            if not well.is_valid:
                raise ValueError(f"Pozo no válido: {well.name}")
            
            results['well_name'] = well.name
            results['processing_steps'].append('well_loaded')
            
            logger.info(f"✅ Pozo cargado: {well.name}")
            logger.info(f"   • Curvas disponibles: {len(well.curves)}")
            logger.info(f"   • Rango profundidad: {well.depth_range[0]:.1f} - {well.depth_range[1]:.1f} m")
            
            # PASO 2: Estandarización
            logger.info("\n🔧 PASO 2: ESTANDARIZACIÓN")
            logger.info("-" * 30)
            
            standardization_result = self.standardizer.standardize_well(well)
            results['processing_steps'].append('standardization')
            
            if standardization_result['success']:
                logger.info("✅ Estandarización completada")
                logger.info(f"   • Mnemonics estandarizados: {len(standardization_result['standardized_mnemonics'])}")
                logger.info(f"   • Curvas limpiadas: {len(standardization_result['cleaned_curves'])}")
            else:
                results['warnings'].append(f"Estandarización parcial: {standardization_result.get('error', '')}")
            
            # PASO 3: Cálculos geofísicos
            logger.info("\n🔬 PASO 3: ANÁLISIS GEOFÍSICO")
            logger.info("-" * 30)
            
            geophysics_result = self.calculator.perform_complete_analysis(well)
            results['processing_steps'].append('geophysical_analysis')
            
            if geophysics_result['success']:
                logger.info("✅ Análisis geofísico completado")
                logger.info(f"   • Cálculos realizados: {geophysics_result['calculations_performed']}")
                
                # Mostrar resultados importantes
                if 'reservoir_zones' in geophysics_result['results']:
                    zones = geophysics_result['results']['reservoir_zones']['zones_identified']
                    logger.info(f"   • Zonas de yacimiento: {zones}")
                
                if 'hard_formations' in geophysics_result['results']:
                    hard = geophysics_result['results']['hard_formations']['hard_formations']
                    logger.info(f"   • Formaciones duras: {hard}")
            else:
                results['errors'].append(f"Error en análisis geofísico: {geophysics_result.get('error', '')}")
            
            # PASO 4: Generar visualizaciones (si está habilitado)
            if generate_plots:
                logger.info("\n📊 PASO 4: VISUALIZACIÓN")
                logger.info("-" * 30)
                
                plot_results = self._generate_visualizations(well, results)
                results['processing_steps'].append('visualization')
                results['generated_files'].extend(plot_results.get('generated_files', []))
                
                if plot_results.get('success', False):
                    logger.info(f"✅ Visualizaciones generadas: {len(plot_results['generated_files'])} archivos")
                else:
                    results['warnings'].append("Algunas visualizaciones fallaron")
            
            # PASO 5: Exportación
            logger.info("\n💾 PASO 5: EXPORTACIÓN")
            logger.info("-" * 30)
            
            export_results = self._export_data(well, export_formats, results)
            results['processing_steps'].append('export')
            results['generated_files'].extend(export_results.get('generated_files', []))
            
            if export_results.get('success', False):
                logger.info(f"✅ Exportación completada: {len(export_formats)} formatos")
            else:
                results['warnings'].append("Algunas exportaciones fallaron")
            
            # FINALIZACIÓN
            end_time = time.time()
            processing_time = end_time - start_time
            
            results['success'] = True
            results['end_time'] = datetime.now().isoformat()
            results['processing_time_seconds'] = processing_time
            results['output_directory'] = str(self.output_dir)
            
            # Crear resumen del workflow
            results['workflow_summary'] = {
                'total_curves': len(well.curves),
                'curve_names': well.curves,
                'depth_range_m': well.depth_range,
                'processing_steps_completed': len(results['processing_steps']),
                'files_generated': len(results['generated_files']),
                'standardization': standardization_result,
                'geophysics': geophysics_result
            }
            
            logger.info("\n🎉 WORKFLOW COMPLETADO")
            logger.info(f"⏱️ Tiempo total: {processing_time:.1f} segundos")
            logger.info(f"📂 Archivos generados: {len(results['generated_files'])}")
            logger.info("=" * 60)
            
        except Exception as e:
            error_msg = f"Error crítico en workflow: {str(e)}"
            logger.error(f"❌ {error_msg}")
            results['success'] = False
            results['errors'].append(error_msg)
            results['end_time'] = datetime.now().isoformat()
            results['processing_time_seconds'] = time.time() - start_time
        
        return results
    
    def process_project(self, project: ProjectManager,
                       generate_summary: bool = True,
                       cross_well_analysis: bool = True,
                       export_formats: List[str] = None) -> Dict[str, Any]:
        """
        Procesar proyecto multi-pozo con workflow coordinado.
        
        Args:
            project: ProjectManager con pozos
            generate_summary: Generar resumen del proyecto
            cross_well_analysis: Realizar análisis cruzado entre pozos
            export_formats: Formatos de exportación
            
        Returns:
            Dict: Resultados del procesamiento del proyecto
        """
        start_time = time.time()
        
        logger.info("=" * 60)
        logger.info(f"🏗️ PROCESANDO PROYECTO: {project.name}")
        logger.info("=" * 60)
        
        if export_formats is None:
            export_formats = ['csv', 'json']
        
        results = {
            'success': False,
            'project_name': project.name,
            'total_wells': project.total_wells,
            'processed_wells': 0,
            'start_time': datetime.now().isoformat(),
            'well_results': {},
            'project_summary': {},
            'generated_files': [],
            'errors': [],
            'warnings': []
        }
        
        try:
            # Procesar cada pozo individualmente
            logger.info(f"📁 Procesando {project.total_wells} pozos...")
            
            for i, well in enumerate(project.wells, 1):
                logger.info(f"\n🛢️ Procesando pozo {i}/{project.total_wells}: {well.name}")
                
                try:
                    well_result = self.process_single_well(
                        well, 
                        generate_plots=True,
                        export_formats=export_formats
                    )
                    
                    results['well_results'][well.name] = well_result
                    
                    if well_result['success']:
                        results['processed_wells'] += 1
                        results['generated_files'].extend(well_result.get('generated_files', []))
                    else:
                        results['errors'].append(f"{well.name}: {well_result.get('errors', ['Unknown error'])[0]}")
                
                except Exception as e:
                    error_msg = f"Error procesando {well.name}: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            # Generar resumen del proyecto (si está habilitado)
            if generate_summary:
                logger.info("\n📊 Generando resumen del proyecto...")
                
                summary = self._generate_project_summary(project, results)
                results['project_summary'] = summary
            
            # Análisis cruzado entre pozos (si está habilitado)
            if cross_well_analysis and project.total_wells > 1:
                logger.info("\n🔗 Realizando análisis cruzado...")
                
                cross_analysis = self._perform_cross_well_analysis(project)
                results['cross_well_analysis'] = cross_analysis
            
            # Finalización
            end_time = time.time()
            processing_time = end_time - start_time
            
            results['success'] = True
            results['end_time'] = datetime.now().isoformat()
            results['total_processing_time_seconds'] = processing_time
            results['output_directory'] = str(self.output_dir)
            
            success_rate = results['processed_wells'] / results['total_wells'] if results['total_wells'] > 0 else 0
            
            logger.info("\n🎉 PROYECTO COMPLETADO")
            logger.info(f"⏱️ Tiempo total: {processing_time:.1f} segundos")
            logger.info(f"✅ Pozos procesados: {results['processed_wells']}/{results['total_wells']} ({success_rate:.1%})")
            logger.info(f"📂 Archivos generados: {len(results['generated_files'])}")
            logger.info("=" * 60)
            
        except Exception as e:
            error_msg = f"Error crítico en proyecto: {str(e)}"
            logger.error(f"❌ {error_msg}")
            results['success'] = False
            results['errors'].append(error_msg)
            results['end_time'] = datetime.now().isoformat()
            results['total_processing_time_seconds'] = time.time() - start_time
        
        return results
    
    def _generate_visualizations(self, well: WellManager, results: Dict) -> Dict[str, Any]:
        """
        Generar visualizaciones para un pozo.
        
        Args:
            well: WellManager
            results: Resultados acumulados
            
        Returns:
            Dict: Resultados de visualización
        """
        plot_results = {
            'success': True,
            'generated_files': [],
            'errors': []
        }
        
        try:
            # Por ahora, simulamos la generación de plots
            # En la implementación real, aquí iría WellPlotter
            
            well_output_dir = self.output_dir / f"{well.name}_plots"
            well_output_dir.mkdir(exist_ok=True)
            
            # Simular archivos de plots generados
            plot_files = [
                f"{well.name}_standard_logs.png",
                f"{well.name}_petrophysics.png",
                f"{well.name}_correlations.png"
            ]
            
            for plot_file in plot_files:
                plot_path = well_output_dir / plot_file
                # Crear archivo vacío para simular
                plot_path.touch()
                plot_results['generated_files'].append(str(plot_path))
            
            logger.info(f"📊 Visualizaciones simuladas: {len(plot_files)} plots")
            
        except Exception as e:
            plot_results['success'] = False
            plot_results['errors'].append(str(e))
            logger.error(f"❌ Error en visualizaciones: {str(e)}")
        
        return plot_results
    
    def _export_data(self, well: WellManager, formats: List[str], results: Dict) -> Dict[str, Any]:
        """
        Exportar datos del pozo a múltiples formatos.
        
        Args:
            well: WellManager
            formats: Lista de formatos
            results: Resultados acumulados
            
        Returns:
            Dict: Resultados de exportación
        """
        export_results = {
            'success': True,
            'generated_files': [],
            'errors': []
        }
        
        try:
            well_output_dir = self.output_dir / f"{well.name}_export"
            well_output_dir.mkdir(exist_ok=True)
            
            for format_type in formats:
                try:
                    if format_type.lower() == 'csv':
                        # Exportar datos principales a CSV
                        df = well.get_curves_dataframe()
                        if not df.empty:
                            csv_path = well_output_dir / f"{well.name}_data.csv"
                            df.to_csv(csv_path)
                            export_results['generated_files'].append(str(csv_path))
                    
                    elif format_type.lower() == 'excel':
                        # Exportar a Excel con múltiples hojas
                        df = well.get_curves_dataframe()
                        if not df.empty:
                            excel_path = well_output_dir / f"{well.name}_data.xlsx"
                            with pd.ExcelWriter(excel_path) as writer:
                                df.to_excel(writer, sheet_name='Curves')
                                
                                # Agregar metadatos
                                metadata_df = pd.DataFrame([well.metadata])
                                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                            
                            export_results['generated_files'].append(str(excel_path))
                    
                    elif format_type.lower() == 'json':
                        # Exportar resumen completo a JSON
                        import json
                        summary = well.get_well_summary()
                        json_path = well_output_dir / f"{well.name}_summary.json"
                        
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
                        
                        export_results['generated_files'].append(str(json_path))
                    
                    elif format_type.lower() == 'las':
                        # Exportar de vuelta a LAS
                        las_path = well_output_dir / f"{well.name}_processed.las"
                        if well.export_to_las(las_path):
                            export_results['generated_files'].append(str(las_path))
                
                except Exception as e:
                    export_results['errors'].append(f"Error exportando {format_type}: {str(e)}")
            
            logger.info(f"💾 Exportación completada: {len(export_results['generated_files'])} archivos")
            
        except Exception as e:
            export_results['success'] = False
            export_results['errors'].append(str(e))
            logger.error(f"❌ Error en exportación: {str(e)}")
        
        return export_results
    
    def _generate_project_summary(self, project: ProjectManager, results: Dict) -> Dict[str, Any]:
        """
        Generar resumen del proyecto.
        
        Args:
            project: ProjectManager
            results: Resultados del procesamiento
            
        Returns:
            Dict: Resumen del proyecto
        """
        summary = project.get_project_summary()
        
        # Agregar estadísticas del procesamiento
        summary['processing_statistics'] = {
            'total_wells_processed': results['processed_wells'],
            'success_rate': results['processed_wells'] / results['total_wells'] if results['total_wells'] > 0 else 0,
            'total_files_generated': len(results['generated_files']),
            'errors_count': len(results['errors']),
            'warnings_count': len(results['warnings'])
        }
        
        return summary
    
    def _perform_cross_well_analysis(self, project: ProjectManager) -> Dict[str, Any]:
        """
        Realizar análisis cruzado entre pozos.
        
        Args:
            project: ProjectManager
            
        Returns:
            Dict: Resultados del análisis cruzado
        """
        cross_analysis = {
            'common_curves': project.get_common_curves(),
            'comparative_statistics': {},
            'depth_correlations': {}
        }
        
        # Obtener estadísticas comparativas
        try:
            stats_df = project.get_comparative_statistics()
            if not stats_df.empty:
                cross_analysis['comparative_statistics'] = stats_df.to_dict('records')
        except Exception as e:
            logger.warning(f"⚠️ Error en estadísticas comparativas: {str(e)}")
        
        return cross_analysis
