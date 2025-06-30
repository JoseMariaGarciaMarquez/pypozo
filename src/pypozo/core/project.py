"""
PyPozo 2.0 - Gestor de Proyectos (Core)
=======================================

ProjectManager maneja múltiples pozos como un proyecto unificado,
proporcionando funcionalidades de análisis comparativo y workflows
coordinados entre pozos.

Características principales:
- Manejo de múltiples pozos
- Análisis comparativo
- Workflows coordinados
- Exportación de proyectos
- Interfaz para GUI

Autor: José María García Márquez
Fecha: Junio 2025
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import pandas as pd
from datetime import datetime

from .well import WellManager

logger = logging.getLogger(__name__)

class ProjectManager:
    """
    Gestor de proyectos multi-pozo.
    
    Esta clase coordina múltiples pozos como un proyecto unificado,
    permitiendo análisis comparativo y workflows colaborativos.
    """
    
    def __init__(self, project_name: str = "Unnamed Project"):
        """
        Inicializar gestor de proyectos.
        
        Args:
            project_name: Nombre del proyecto
        """
        self.name = project_name
        self.created_date = datetime.now()
        self.wells: List[WellManager] = []
        self.metadata = {}
        self.processing_history = []
        
        logger.info(f"📁 Proyecto creado: {self.name}")
    
    def add_well(self, well_source: Union[str, Path, WellManager]) -> bool:
        """
        Agregar pozo al proyecto.
        
        Args:
            well_source: Archivo LAS, Path o WellManager
            
        Returns:
            bool: True si se agregó exitosamente
        """
        try:
            if isinstance(well_source, WellManager):
                well = well_source
            elif isinstance(well_source, (str, Path)):
                well = WellManager.from_las(well_source)
            else:
                raise ValueError(f"Tipo de fuente no soportado: {type(well_source)}")
            
            if well.is_valid:
                self.wells.append(well)
                logger.info(f"✅ Pozo agregado al proyecto: {well.name}")
                
                # Registrar en historial
                self.add_processing_step(
                    "well_added",
                    {"well_name": well.name, "total_wells": len(self.wells)}
                )
                
                return True
            else:
                logger.warning(f"⚠️ Pozo no válido, no se agregó: {well.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error agregando pozo: {str(e)}")
            return False
    
    def add_wells_from_directory(self, directory: Union[str, Path], 
                                pattern: str = "*.las") -> int:
        """
        Agregar múltiples pozos desde un directorio.
        
        Args:
            directory: Directorio con archivos LAS
            pattern: Patrón de archivos (default: "*.las")
            
        Returns:
            int: Número de pozos agregados exitosamente
        """
        directory = Path(directory)
        
        if not directory.exists():
            logger.error(f"❌ Directorio no existe: {directory}")
            return 0
        
        las_files = list(directory.glob(pattern))
        logger.info(f"📁 Encontrados {len(las_files)} archivos en {directory}")
        
        added_count = 0
        for las_file in las_files:
            if self.add_well(las_file):
                added_count += 1
        
        logger.info(f"✅ {added_count}/{len(las_files)} pozos agregados al proyecto")
        return added_count
    
    def remove_well(self, well_identifier: Union[str, int, WellManager]) -> bool:
        """
        Remover pozo del proyecto.
        
        Args:
            well_identifier: Nombre, índice o WellManager
            
        Returns:
            bool: True si se removió exitosamente
        """
        try:
            if isinstance(well_identifier, str):
                # Buscar por nombre
                for i, well in enumerate(self.wells):
                    if well.name == well_identifier:
                        removed_well = self.wells.pop(i)
                        logger.info(f"🗑️ Pozo removido: {removed_well.name}")
                        return True
                return False
                
            elif isinstance(well_identifier, int):
                # Remover por índice
                if 0 <= well_identifier < len(self.wells):
                    removed_well = self.wells.pop(well_identifier)
                    logger.info(f"🗑️ Pozo removido: {removed_well.name}")
                    return True
                return False
                
            elif isinstance(well_identifier, WellManager):
                # Remover instancia específica
                if well_identifier in self.wells:
                    self.wells.remove(well_identifier)
                    logger.info(f"🗑️ Pozo removido: {well_identifier.name}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"❌ Error removiendo pozo: {str(e)}")
            return False
    
    def get_well(self, identifier: Union[str, int]) -> Optional[WellManager]:
        """
        Obtener pozo por nombre o índice.
        
        Args:
            identifier: Nombre o índice del pozo
            
        Returns:
            WellManager: Pozo encontrado o None
        """
        if isinstance(identifier, str):
            for well in self.wells:
                if well.name == identifier:
                    return well
        elif isinstance(identifier, int):
            if 0 <= identifier < len(self.wells):
                return self.wells[identifier]
        
        return None
    
    @property
    def well_names(self) -> List[str]:
        """Obtener lista de nombres de pozos."""
        return [well.name for well in self.wells]
    
    @property
    def total_wells(self) -> int:
        """Obtener número total de pozos."""
        return len(self.wells)
    
    @property
    def valid_wells(self) -> List[WellManager]:
        """Obtener lista de pozos válidos."""
        return [well for well in self.wells if well.is_valid]
    
    def get_common_curves(self) -> List[str]:
        """
        Obtener curvas comunes a todos los pozos.
        
        Returns:
            List[str]: Lista de curvas comunes
        """
        if not self.wells:
            return []
        
        # Obtener curvas del primer pozo
        common_curves = set(self.wells[0].curves)
        
        # Intersección con curvas de otros pozos
        for well in self.wells[1:]:
            common_curves = common_curves.intersection(set(well.curves))
        
        return list(common_curves)
    
    def get_all_curves(self) -> List[str]:
        """
        Obtener todas las curvas únicas del proyecto.
        
        Returns:
            List[str]: Lista de todas las curvas
        """
        all_curves = set()
        for well in self.wells:
            all_curves.update(well.curves)
        
        return list(all_curves)
    
    def get_depth_range_summary(self) -> Dict:
        """
        Obtener resumen de rangos de profundidad.
        
        Returns:
            Dict: Resumen de profundidades
        """
        if not self.wells:
            return {}
        
        depths = []
        for well in self.wells:
            depth_min, depth_max = well.depth_range
            depths.append((depth_min, depth_max))
        
        all_mins = [d[0] for d in depths]
        all_maxs = [d[1] for d in depths]
        
        return {
            'project_min_depth': min(all_mins),
            'project_max_depth': max(all_maxs),
            'project_depth_range': max(all_maxs) - min(all_mins),
            'individual_ranges': {
                well.name: {'min': depths[i][0], 'max': depths[i][1]}
                for i, well in enumerate(self.wells)
            }
        }
    
    def get_project_summary(self) -> Dict:
        """
        Obtener resumen completo del proyecto.
        
        Returns:
            Dict: Resumen del proyecto
        """
        summary = {
            'project_name': self.name,
            'created_date': self.created_date.isoformat(),
            'total_wells': self.total_wells,
            'valid_wells': len(self.valid_wells),
            'well_names': self.well_names,
            'common_curves': self.get_common_curves(),
            'all_curves': self.get_all_curves(),
            'depth_summary': self.get_depth_range_summary(),
            'metadata': self.metadata,
            'processing_history': self.processing_history
        }
        
        # Estadísticas por pozo
        well_summaries = {}
        for well in self.wells:
            well_summaries[well.name] = well.get_well_summary()
        
        summary['well_summaries'] = well_summaries
        
        return summary
    
    def get_comparative_statistics(self, curves: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Obtener estadísticas comparativas de curvas.
        
        Args:
            curves: Lista de curvas (None para curvas comunes)
            
        Returns:
            pd.DataFrame: Estadísticas comparativas
        """
        if curves is None:
            curves = self.get_common_curves()
        
        if not curves or not self.wells:
            return pd.DataFrame()
        
        stats_data = []
        
        for well in self.wells:
            well_stats = {'well_name': well.name}
            
            for curve_name in curves:
                curve_info = well.get_curve_info(curve_name)
                if curve_info:
                    well_stats[f'{curve_name}_min'] = curve_info.get('min_value', np.nan)
                    well_stats[f'{curve_name}_max'] = curve_info.get('max_value', np.nan)
                    well_stats[f'{curve_name}_mean'] = curve_info.get('mean_value', np.nan)
                    well_stats[f'{curve_name}_completeness'] = curve_info.get('completeness', 0)
                else:
                    well_stats[f'{curve_name}_min'] = np.nan
                    well_stats[f'{curve_name}_max'] = np.nan
                    well_stats[f'{curve_name}_mean'] = np.nan
                    well_stats[f'{curve_name}_completeness'] = 0
            
            stats_data.append(well_stats)
        
        return pd.DataFrame(stats_data)
    
    def add_processing_step(self, step_name: str, details: Dict = None):
        """
        Agregar paso de procesamiento al historial del proyecto.
        
        Args:
            step_name: Nombre del paso
            details: Detalles adicionales
        """
        step = {
            'step': step_name,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.processing_history.append(step)
        logger.info(f"📝 Paso del proyecto agregado: {step_name}")
    
    def save_project(self, output_path: Union[str, Path]) -> bool:
        """
        Guardar proyecto en formato JSON.
        
        Args:
            output_path: Ruta del archivo de proyecto
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            import json
            
            output_path = Path(output_path)
            
            # Preparar datos del proyecto
            project_data = self.get_project_summary()
            
            # Guardar JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Proyecto guardado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando proyecto: {str(e)}")
            return False
    
    def __str__(self) -> str:
        """Representación en string del proyecto."""
        return f"ProjectManager(name='{self.name}', wells={self.total_wells})"
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return self.__str__()
