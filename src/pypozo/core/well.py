"""
PyPozo 2.0 - Gestor de Pozos (Core)
===================================

WellManager es la clase principal para el manejo de pozos individuales,
construida sobre Welly para máxima robustez y compatibilidad.

Esta clase encapsula un objeto Welly Well y proporciona:
- Carga y validación de archivos LAS
- Acceso simplificado a curvas y metadatos
- Métodos de procesamiento básico
- Interfaz limpia para la GUI
- Exportación a múltiples formatos

Autor: José María García Márquez
Fecha: Junio 2025
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np

# Welly para manejo robusto de pozos
import welly
from welly import Well as WellyWell

# LasIO para lectura directa de LAS
import lasio

logger = logging.getLogger(__name__)

class WellManager:
    """
    Gestor principal de pozos basado en Welly.
    
    Esta clase proporciona una interfaz limpia y robusta para el manejo
    de pozos individuales, encapsulando la funcionalidad de Welly.
    """
    
    def __init__(self, well: Optional[WellyWell] = None):
        """
        Inicializar el gestor de pozos.
        
        Args:
            well: Objeto Welly Well existente (opcional)
        """
        self._well = well
        self._metadata = {}
        self._processing_history = []
        self._is_valid = False
        
        if well:
            self._validate_well()
    
    @classmethod
    def from_las(cls, file_path: Union[str, Path]) -> 'WellManager':
        """
        Crear WellManager desde archivo LAS.
        
        Args:
            file_path: Ruta al archivo LAS
            
        Returns:
            WellManager: Nueva instancia
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el archivo no es válido
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        logger.info(f"📁 Cargando archivo LAS: {file_path.name}")
        
        try:
            # Usar Welly para cargar el pozo
            well = WellyWell.from_las(str(file_path))
            
            # Crear instancia del gestor
            manager = cls(well)
            
            # Agregar información del archivo
            manager._metadata['source_file'] = str(file_path)
            manager._metadata['file_name'] = file_path.name
            
            logger.info(f"✅ Pozo cargado: {manager.name}")
            logger.info(f"✅ Curvas disponibles: {len(manager.curves)}")
            
            return manager
            
        except Exception as e:
            logger.error(f"❌ Error cargando archivo LAS: {str(e)}")
            raise ValueError(f"Error cargando archivo LAS: {str(e)}")
    
    @classmethod 
    def from_welly(cls, well: WellyWell) -> 'WellManager':
        """
        Crear WellManager desde objeto Welly existente.
        
        Args:
            well: Objeto Welly Well
            
        Returns:
            WellManager: Nueva instancia
        """
        return cls(well)
    
    def _validate_well(self) -> bool:
        """
        Validar el pozo cargado.
        
        Returns:
            bool: True si el pozo es válido
        """
        if not self._well:
            self._is_valid = False
            return False
        
        # Validaciones básicas
        validations = {
            'has_curves': len(self._well.data) > 0 if hasattr(self._well, 'data') and self._well.data else False,
            'has_depth': True,  # Welly siempre maneja profundidad correctamente
            'has_header': hasattr(self._well, 'header') and not self._well.header.empty if hasattr(self._well, 'header') else False
        }
        
        self._is_valid = all(validations.values())
        
        if not self._is_valid:
            failed = [k for k, v in validations.items() if not v]
            logger.warning(f"⚠️ Validación falló: {failed}")
        
        return self._is_valid
    
    @property
    def is_valid(self) -> bool:
        """Verificar si el pozo es válido."""
        return self._is_valid
    
    @property
    def name(self) -> str:
        """Obtener nombre del pozo."""
        if not self._well:
            return "Unnamed Well"
        
        # Usar el atributo name de Welly
        if hasattr(self._well, 'name') and self._well.name:
            return self._well.name
        
        # Si no hay name, intentar obtener desde el header DataFrame
        if hasattr(self._well, 'header') and not self._well.header.empty:
            try:
                well_section = self._well.header[self._well.header['section'] == 'WELL']
                if not well_section.empty:
                    well_name = well_section[well_section['mnemonic'] == 'WELL']['value']
                    if not well_name.empty:
                        return str(well_name.iloc[0])
            except:
                pass
        
        return "Unnamed Well"
    
    @property
    def curves(self) -> List[str]:
        """Obtener lista de nombres de curvas disponibles."""
        if not self._well or not hasattr(self._well, 'data') or not self._well.data:
            return []
        
        # En Welly, data es un diccionario con las curvas
        return list(self._well.data.keys())
    
    @property
    def depth_range(self) -> Tuple[float, float]:
        """
        Obtener rango de profundidad del pozo.
        
        Returns:
            Tuple[float, float]: (profundidad_min, profundidad_max)
        """
        if not self._well or not hasattr(self._well, 'data') or not self._well.data:
            return (0.0, 0.0)
        
        # Obtener el rango de profundidad desde las curvas
        try:
            # Usar el DataFrame del pozo
            df = self._well.df()
            if not df.empty:
                return (float(df.index.min()), float(df.index.max()))
        except:
            pass
        
        # Fallback: usar la primera curva disponible
        try:
            first_curve = list(self._well.data.values())[0]
            if hasattr(first_curve, 'basis') and first_curve.basis is not None:
                basis = first_curve.basis
                return (float(basis.min()), float(basis.max()))
        except:
            pass
        
        return (0.0, 0.0)
    
    @property
    def metadata(self) -> Dict:
        """Obtener metadatos del pozo."""
        meta = self._metadata.copy()
        
        if self._well and hasattr(self._well, 'header') and not self._well.header.empty:
            # Convertir el DataFrame del header a diccionario
            try:
                for _, row in self._well.header.iterrows():
                    section = row.get('section', 'unknown')
                    mnemonic = row.get('mnemonic', 'unknown')
                    value = row.get('value', '')
                    
                    if section not in meta:
                        meta[section] = {}
                    meta[section][mnemonic] = value
            except Exception as e:
                logger.warning(f"Error procesando header: {str(e)}")
        
        return meta
    
    def get_curve_data(self, curve_name: str) -> Optional[pd.Series]:
        """
        Obtener datos de una curva específica.
        
        Args:
            curve_name: Nombre de la curva
            
        Returns:
            pd.Series: Datos de la curva con índice de profundidad
        """
        if not self._well or not hasattr(self._well, 'data') or not self._well.data:
            return None
        
        try:
            # Obtener el DataFrame completo del pozo
            df = self._well.df()
            
            # Buscar la curva (case-insensitive)
            curve_found = None
            for col in df.columns:
                if col.upper() == curve_name.upper():
                    curve_found = col
                    break
            
            if curve_found is None:
                logger.warning(f"⚠️ Curva no encontrada: {curve_name}")
                logger.info(f"💡 Curvas disponibles: {list(df.columns)}")
                return None
            
            # Retornar la serie con datos no nulos
            return df[curve_found].dropna()
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo curva {curve_name}: {str(e)}")
            return None
        
        # Crear Series con índice de profundidad
        depth = self._well.basis
        return pd.Series(curve.data, index=depth, name=curve_name)
    
    def get_curves_dataframe(self, curves: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Obtener DataFrame con múltiples curvas.
        
        Args:
            curves: Lista de curvas (None para todas)
            
        Returns:
            pd.DataFrame: DataFrame con curvas e índice de profundidad
        """
        if not self._well:
            return pd.DataFrame()
        
        if curves is None:
            curves = self.curves
        
        # Crear DataFrame
        data = {}
        depth = self._well.basis
        
        for curve_name in curves:
            curve_data = self.get_curve_data(curve_name)
            if curve_data is not None:
                data[curve_name] = curve_data
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data, index=depth)
        df.index.name = 'DEPTH'
        
        return df
    
    def get_curve_info(self, curve_name: str) -> Dict:
        """
        Obtener información detallada de una curva.
        
        Args:
            curve_name: Nombre de la curva
            
        Returns:
            Dict: Información de la curva
        """
        if not self._well:
            return {}
        
        # Buscar la curva
        curve = None
        for c in self._well.data:
            if c.mnemonic.upper() == curve_name.upper():
                curve = c
                break
        
        if not curve:
            return {}
        
        return {
            'mnemonic': curve.mnemonic,
            'description': curve.description or '',
            'units': curve.units or '',
            'data_type': str(curve.data.dtype),
            'null_value': curve.null_value,
            'min_value': float(np.nanmin(curve.data)),
            'max_value': float(np.nanmax(curve.data)),
            'mean_value': float(np.nanmean(curve.data)),
            'valid_points': int(np.sum(~np.isnan(curve.data))),
            'total_points': len(curve.data),
            'completeness': float(np.sum(~np.isnan(curve.data)) / len(curve.data))
        }
    
    def get_well_summary(self) -> Dict:
        """
        Obtener resumen completo del pozo.
        
        Returns:
            Dict: Resumen del pozo
        """
        if not self._well:
            return {'error': 'No well loaded'}
        
        depth_min, depth_max = self.depth_range
        
        summary = {
            'name': self.name,
            'is_valid': self.is_valid,
            'total_curves': len(self.curves),
            'curve_names': self.curves,
            'depth_range': {
                'min': depth_min,
                'max': depth_max,
                'interval': depth_max - depth_min
            },
            'metadata': self.metadata,
            'processing_history': self._processing_history.copy()
        }
        
        # Estadísticas de curvas
        curve_stats = {}
        for curve_name in self.curves:
            curve_stats[curve_name] = self.get_curve_info(curve_name)
        
        summary['curve_statistics'] = curve_stats
        
        return summary
    
    def add_processing_step(self, step_name: str, details: Dict = None):
        """
        Agregar paso de procesamiento al historial.
        
        Args:
            step_name: Nombre del paso de procesamiento
            details: Detalles adicionales
        """
        step = {
            'step': step_name,
            'timestamp': pd.Timestamp.now().isoformat(),
            'details': details or {}
        }
        
        self._processing_history.append(step)
        logger.info(f"📝 Paso agregado: {step_name}")
    
    def export_to_las(self, output_path: Union[str, Path]) -> bool:
        """
        Exportar pozo a archivo LAS.
        
        Args:
            output_path: Ruta del archivo de salida
            
        Returns:
            bool: True si la exportación fue exitosa
        """
        if not self._well:
            logger.error("❌ No hay pozo cargado para exportar")
            return False
        
        try:
            output_path = Path(output_path)
            self._well.to_las(str(output_path))
            
            logger.info(f"✅ Pozo exportado a: {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando a LAS: {str(e)}")
            return False
    
    def get_curve_units(self, curve_name: str) -> str:
        """
        Obtener las unidades de una curva específica.
        
        Args:
            curve_name: Nombre de la curva
            
        Returns:
            str: Unidades de la curva (vacío si no se encuentran)
        """
        try:
            curve = self._well.data.get(curve_name)
            if curve and hasattr(curve, 'units'):
                return curve.units or ''
            return ''
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo unidades de {curve_name}: {str(e)}")
            return ''
    
    def __str__(self) -> str:
        """Representación en string del pozo."""
        if not self._well:
            return "WellManager(no well loaded)"
        
        return f"WellManager(name='{self.name}', curves={len(self.curves)}, depth_range={self.depth_range})"
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return self.__str__()
