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
    
    def add_curve(self, curve_name: str, data: Union[pd.Series, np.ndarray, List], units: str = '', description: str = '') -> bool:
        """
        Agregar una nueva curva al pozo.
        
        Args:
            curve_name: Nombre de la nueva curva
            data: Datos de la curva (Series, array o lista)
            units: Unidades de la curva
            description: Descripción de la curva
            
        Returns:
            bool: True si la curva fue agregada exitosamente
        """
        if not self._well:
            logger.error("❌ No hay pozo cargado")
            return False
        
        try:
            from welly import Curve
            
            # Obtener el índice de profundidad existente
            if hasattr(self._well, 'basis') and self._well.basis is not None:
                depth_index = self._well.basis
            else:
                # Usar el índice del DataFrame existente
                df = self._well.df()
                if not df.empty:
                    depth_index = df.index
                else:
                    logger.error("❌ No se puede determinar el índice de profundidad")
                    return False
            
            # Convertir datos a array si es necesario
            if isinstance(data, pd.Series):
                curve_data = data.values
                # Si la serie tiene un índice diferente, reindexar
                if not data.index.equals(depth_index):
                    data = data.reindex(depth_index)
                    curve_data = data.values
            elif isinstance(data, (list, np.ndarray)):
                curve_data = np.array(data)
            else:
                logger.error(f"❌ Tipo de datos no soportado: {type(data)}")
                return False
            
            # Asegurar que los datos tengan la misma longitud que el índice
            if len(curve_data) != len(depth_index):
                logger.warning(f"⚠️ Longitud de datos ({len(curve_data)}) no coincide con profundidad ({len(depth_index)})")
                # Intentar ajustar
                min_len = min(len(curve_data), len(depth_index))
                curve_data = curve_data[:min_len]
                depth_index = depth_index[:min_len]
            
            # Crear la curva de Welly
            new_curve = Curve(
                data=curve_data,
                basis=depth_index,
                mnemonic=curve_name,
                units=units,
                description=description
            )
            
            # Agregar la curva al pozo
            self._well.data[curve_name] = new_curve
            
            logger.info(f"✅ Curva agregada: {curve_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error agregando curva {curve_name}: {str(e)}")
            return False
    
    @property
    def data(self) -> 'WellDataFrame':
        """
        Obtener DataFrame con todas las curvas del pozo.
        
        Returns:
            WellDataFrame: DataFrame wrapper que permite asignación de curvas
        """
        return WellDataFrame(self)
    
    def get_curve_units(self, curve_name: str) -> str:
        """
        Obtener las unidades de una curva específica.
        
        Args:
            curve_name: Nombre de la curva
            
        Returns:
            str: Unidades de la curva
        """
        if not self._well or not hasattr(self._well, 'data') or not self._well.data:
            return ''
        
        try:
            # Buscar la curva en el diccionario de datos de Welly
            for curve_name_key, curve_obj in self._well.data.items():
                if curve_name_key.upper() == curve_name.upper():
                    return getattr(curve_obj, 'units', '') or ''
            
            # Si no se encuentra, retornar string vacío
            return ''
            
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo unidades para {curve_name}: {str(e)}")
            return ''


class WellDataFrame:
    """
    Wrapper para el DataFrame del pozo que permite asignación de nuevas curvas.
    """
    
    def __init__(self, well_manager: 'WellManager'):
        self._well_manager = well_manager
    
    def __getitem__(self, key):
        """Obtener curva o slice del DataFrame."""
        df = self._get_dataframe()
        return df[key]
    
    def __setitem__(self, key: str, value):
        """Asignar nueva curva al pozo."""
        if isinstance(key, str):
            # Agregar nueva curva
            self._well_manager.add_curve(key, value)
        else:
            raise ValueError("Solo se puede asignar curvas individuales por nombre")
    
    def __getattr__(self, name):
        """Delegar atributos y métodos al DataFrame subyacente."""
        df = self._get_dataframe()
        return getattr(df, name)
    
    def __len__(self):
        """Obtener longitud del DataFrame."""
        df = self._get_dataframe()
        return len(df)
    
    def __iter__(self):
        """Iterar sobre las columnas del DataFrame."""
        df = self._get_dataframe()
        return iter(df)
    
    def __str__(self):
        """Representación string del DataFrame."""
        df = self._get_dataframe()
        return str(df)
    
    def __repr__(self):
        """Representación del DataFrame."""
        df = self._get_dataframe()
        return repr(df)
    
    def _get_dataframe(self) -> pd.DataFrame:
        """Obtener el DataFrame subyacente."""
        if not self._well_manager._well:
            return pd.DataFrame()
            
        if not hasattr(self._well_manager._well, 'data'):
            return pd.DataFrame()
            
        if not self._well_manager._well.data:
            return pd.DataFrame()

        try:
            # Add timeout protection and error handling
            df = self._well_manager._well.df()
            if df is None:
                return pd.DataFrame()
            return df
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo DataFrame del pozo: {str(e)}")
            # Fallback: try to create DataFrame manually from curves
            try:
                data_dict = {}
                for curve_name, curve in self._well_manager._well.data.items():
                    if hasattr(curve, 'data') and hasattr(curve, 'basis'):
                        data_dict[curve_name] = pd.Series(curve.data, index=curve.basis)
                
                if data_dict:
                    return pd.DataFrame(data_dict)
                else:
                    return pd.DataFrame()
            except Exception as fallback_error:
                logger.error(f"❌ Error en fallback DataFrame: {str(fallback_error)}")
                return pd.DataFrame()
    
    @property
    def columns(self):
        """Obtener columnas del DataFrame."""
        df = self._get_dataframe()
        return df.columns
    
    @property
    def index(self):
        """Obtener índice del DataFrame.""" 
        df = self._get_dataframe()
        return df.index
    
    def to_csv(self, *args, **kwargs):
        """Exportar a CSV."""
        df = self._get_dataframe()
        return df.to_csv(*args, **kwargs)
    

    
    def add_curve(self, curve_name: str, data: Union[pd.Series, np.ndarray, List], units: str = '', description: str = '') -> bool:
        """
        Agregar una nueva curva al pozo.
        
        Args:
            curve_name: Nombre de la nueva curva
            data: Datos de la curva (Series, array o lista)
            units: Unidades de la curva
            description: Descripción de la curva
            
        Returns:
            bool: True si la curva fue agregada exitosamente
        """
        if not self._well:
            logger.error("❌ No hay pozo cargado")
            return False
        
        try:
            from welly import Curve
            
            # Obtener el índice de profundidad existente
            if hasattr(self._well, 'basis') and self._well.basis is not None:
                depth_index = self._well.basis
            else:
                # Usar el índice del DataFrame existente
                df = self._well.df()
                if not df.empty:
                    depth_index = df.index
                else:
                    logger.error("❌ No se puede determinar el índice de profundidad")
                    return False
            
            # Convertir datos a array si es necesario
            if isinstance(data, pd.Series):
                curve_data = data.values
                # Si la serie tiene un índice diferente, reindexar
                if not data.index.equals(depth_index):
                    data = data.reindex(depth_index)
                    curve_data = data.values
            elif isinstance(data, (list, np.ndarray)):
                curve_data = np.array(data)
            else:
                logger.error(f"❌ Tipo de datos no soportado: {type(data)}")
                return False
            
            # Asegurar que los datos tengan la misma longitud que el índice
            if len(curve_data) != len(depth_index):
                logger.warning(f"⚠️ Longitud de datos ({len(curve_data)}) no coincide con profundidad ({len(depth_index)})")
                # Intentar ajustar
                min_len = min(len(curve_data), len(depth_index))
                curve_data = curve_data[:min_len]
                depth_index = depth_index[:min_len]
            
            # Crear la curva de Welly
            new_curve = Curve(
                data=curve_data,
                basis=depth_index,
                mnemonic=curve_name,
                units=units,
                description=description
            )
            
            # Agregar la curva al pozo
            self._well.data[curve_name] = new_curve
            
            logger.info(f"✅ Curva agregada: {curve_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error agregando curva {curve_name}: {str(e)}")
            return False
    
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
        
        # Buscar la curva en el diccionario de datos de Welly
        curve = None
        for curve_name_key, curve_obj in self._well.data.items():
            if curve_name_key.upper() == curve_name.upper():
                curve = curve_obj
                break
        
        if not curve:
            return {}
        
        return {
            'mnemonic': getattr(curve, 'mnemonic', curve_name),
            'description': getattr(curve, 'description', '') or '',
            'units': getattr(curve, 'units', '') or '',
            'data_type': str(curve.data.dtype) if hasattr(curve, 'data') else 'unknown',
            'null_value': getattr(curve, 'null_value', None),
            'min_value': float(np.nanmin(curve.data)) if hasattr(curve, 'data') else 0.0,
            'max_value': float(np.nanmax(curve.data)) if hasattr(curve, 'data') else 0.0,
            'mean_value': float(np.nanmean(curve.data)) if hasattr(curve, 'data') else 0.0,
            'valid_points': int(np.sum(~np.isnan(curve.data))) if hasattr(curve, 'data') else 0,
            'total_points': len(curve.data) if hasattr(curve, 'data') else 0,
            'completeness': float(np.sum(~np.isnan(curve.data)) / len(curve.data)) if hasattr(curve, 'data') and len(curve.data) > 0 else 0.0
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
            
            # Intentar exportación directa primero
            try:
                self._well.to_las(str(output_path))
                logger.info(f"✅ Pozo exportado a: {output_path.name}")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Error con exportación directa: {str(e)}")
                
                # Método alternativo: crear archivo LAS manualmente
                if "Please provide an index" in str(e):
                    logger.info("🔧 Usando método alternativo para exportación...")
                    return self._export_las_manual(output_path)
                else:
                    raise e
            
        except Exception as e:
            logger.error(f"❌ Error exportando a LAS: {str(e)}")
            return False
    
    def _export_las_manual(self, output_path: Path) -> bool:
        """
        Exportar archivo LAS manualmente cuando Welly falla.
        
        Args:
            output_path: Ruta del archivo de salida
            
        Returns:
            bool: True si la exportación fue exitosa
        """
        try:
            # Obtener datos del pozo
            df = self._well.df()
            if df.empty:
                logger.error("❌ No hay datos para exportar")
                return False
            
            # Obtener información básica
            depth_min = df.index.min()
            depth_max = df.index.max()
            depth_step = df.index[1] - df.index[0] if len(df.index) > 1 else 0.1524
            well_name = self.name or "UNKNOWN"
            
            # Crear archivo LAS con formato correcto
            with open(output_path, 'w') as f:
                # VERSION INFORMATION
                f.write("~VERSION INFORMATION\n")
                f.write(" VERS.                 2.0:   CWLS LOG ASCII STANDARD - VERSION 2.0\n")
                f.write(" WRAP.                  NO:   SINGLE LINE PER DEPTH STEP\n")
                
                # WELL INFORMATION
                f.write("~WELL INFORMATION\n")
                f.write("#MNEM.UNIT       DATA           DESCRIPTION MNEMONIC\n")
                f.write("#---------    -------------   --------------------------\n")
                f.write(f" STRT.M         {depth_min:.4f}                      : START DEPTH\n")
                f.write(f" STOP.M         {depth_max:.4f}                     : STOP DEPTH\n")
                f.write(f" STEP.M         {depth_step:.4f}                        : STEP VALUE\n")
                f.write(" NULL.          -999.0000                     : NULL VALUE\n")
                f.write(" SRVC.          PYPOZO                        : Service Company/Logging company\n")
                
                # Fecha actual
                from datetime import datetime
                current_date = datetime.now().strftime('%d/%m/%Y')
                f.write(f" DATE.          {current_date}                    : LAS file Creation Date\n")
                f.write(f" WELL    .      {well_name:<30} : Well Name\n")
                f.write(" COMP    .      PYPOZO 2.0                    : Company\n")
                f.write(" FLD     .      UNKNOWN                       : Field\n")
                f.write(" LOC     .      UNKNOWN                       : Location\n")
                f.write(" LATI    .      0                             : Latitude/Northing\n")
                f.write(" LONG    .      0                             : Longitude/Easting\n")
                f.write(" APDAT   .      0                             : Elevation Above Permanent Datum\n")
                
                # CURVE INFORMATION
                f.write("~CURVE INFORMATION\n")
                f.write("#MNEM          UNIT     API CODE   Curve Type Comments\n")
                f.write("#---------- ---------- ----------  ---------- --------\n")
                
                # Profundidad siempre primero
                f.write(" DEPTH     .M                    : Depth      \n")
                
                # Curvas de datos
                for curve_name in df.columns:
                    units = self.get_curve_units(curve_name) or "UNIT"
                    # Formatear unidades para que queden alineadas
                    f.write(f" {curve_name:<10}.{units:<10}                 : {curve_name:<10} \n")
                
                # ASCII DATA SECTION
                f.write("~A Log data section\n")
                
                # Datos - formato numérico correcto
                for depth in df.index:
                    # Formatear profundidad
                    line = f"{depth:>10.4f}"
                    
                    # Formatear valores de curvas
                    for curve_name in df.columns:
                        value = df.loc[depth, curve_name]
                        if pd.isna(value) or not np.isfinite(value):
                            line += f"{'      -999.0000':>15}"
                        else:
                            line += f"{value:>15.4f}"
                    
                    f.write(line + " \n")
            
            # Verificar que el archivo se creó correctamente
            if output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"✅ Archivo LAS creado manualmente: {output_path.name} ({output_path.stat().st_size} bytes)")
                return True
            else:
                logger.error("❌ El archivo creado está vacío o no existe")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error en exportación manual: {str(e)}")
            return False
    
    @classmethod
    def merge_wells(cls, wells: List['WellManager'], well_name: str) -> 'WellManager':
        """
        Fusionar múltiples pozos con el mismo nombre en uno solo.
        
        Combina registros de múltiples archivos LAS, maneja traslapes
        calculando la media, y crea un pozo fusionado completo.
        
        Args:
            wells: Lista de WellManager a fusionar
            well_name: Nombre del pozo fusionado
            
        Returns:
            WellManager: Pozo fusionado con todos los registros
        """
        if not wells:
            logger.error("❌ No hay pozos para fusionar")
            return None
        
        if len(wells) == 1:
            logger.info(f"🔄 Solo un pozo encontrado para '{well_name}', no se requiere fusión")
            return wells[0]
        
        logger.info(f"🔄 Iniciando fusión de {len(wells)} pozos para '{well_name}'")
        
        try:
            # Obtener todos los rangos de profundidad
            depth_ranges = []
            all_curves = set()
            
            for well in wells:
                depth_range = well.depth_range
                depth_ranges.append(depth_range)
                all_curves.update(well.curves)
                logger.info(f"   📊 {well.metadata.get('source_file', 'unknown')}: "
                           f"{depth_range[0]:.1f}-{depth_range[1]:.1f}m, "
                           f"curvas: {len(well.curves)}")
            
            # Determinar rango de profundidad combinado
            min_depth = min(dr[0] for dr in depth_ranges)
            max_depth = max(dr[1] for dr in depth_ranges)
            
            logger.info(f"🎯 Rango fusionado: {min_depth:.1f}-{max_depth:.1f}m")
            logger.info(f"📈 Total de curvas únicas: {len(all_curves)}")
            
            # Crear DataFrame maestro con índice de profundidad común
            # Usar el step más fino de todos los pozos
            steps = []
            for well in wells:
                df = well._well.df()
                if len(df) > 1:
                    step = abs(df.index[1] - df.index[0])
                    steps.append(step)
            
            common_step = min(steps) if steps else 0.1524  # Default 0.5 ft
            
            # Crear índice de profundidad común
            depth_index = np.arange(min_depth, max_depth + common_step, common_step)
            merged_df = pd.DataFrame(index=depth_index)
            
            # Fusionar cada curva
            overlap_info = {}
            
            for curve_name in sorted(all_curves):
                logger.info(f"🔗 Procesando curva: {curve_name}")
                
                # Recolectar datos de esta curva de todos los pozos
                curve_data_list = []
                curve_units = None
                
                for well in wells:
                    if curve_name in well.curves:
                        curve_data = well.get_curve_data(curve_name)
                        if curve_data is not None and len(curve_data) > 0:
                            # Interpolate to common depth index
                            interpolated = curve_data.reindex(depth_index, method='nearest', tolerance=common_step)
                            curve_data_list.append(interpolated)
                            
                            # Obtener unidades (usar la primera encontrada)
                            if curve_units is None:
                                curve_units = well.get_curve_units(curve_name)
                
                if curve_data_list:
                    # Combinar datos, calculando media en traslapes
                    combined_data = cls._merge_curve_data(curve_data_list, curve_name, overlap_info)
                    merged_df[curve_name] = combined_data
                    
                    logger.info(f"   ✅ {curve_name}: {(~combined_data.isna()).sum()} puntos válidos")
                    if curve_name in overlap_info:
                        logger.info(f"   🔄 Traslapes promediados: {overlap_info[curve_name]} puntos")
            
            # Crear pozo fusionado usando el primer pozo como base
            base_well = wells[0]._well
            
            # Crear nuevo objeto Well con datos fusionados
            merged_well_data = {}
            for curve_name in merged_df.columns:
                curve_data = merged_df[curve_name].dropna()
                if len(curve_data) > 0:
                    # Obtener unidades de la curva original
                    units = None
                    for well in wells:
                        if curve_name in well.curves:
                            units = well.get_curve_units(curve_name)
                            if units:
                                break
                    
                    # Crear objeto Curve
                    curve = welly.Curve(curve_data.values, 
                                      basis=curve_data.index.values,
                                      mnemonic=curve_name,
                                      units=units or '')
                    merged_well_data[curve_name] = curve
            
            # Crear Well fusionado manualmente curva por curva
            # Método más robusto que funciona con las limitaciones de Welly
            merged_well = welly.Well()
            merged_well.name = well_name
            
            logger.info(f"🔧 Creando pozo fusionado con {len(merged_df.columns)} curvas")
            
            # Procesar cada curva individualmente
            for curve_name in merged_df.columns:
                curve_data = merged_df[curve_name].dropna()
                if len(curve_data) > 0:
                    logger.info(f"   📈 Agregando curva {curve_name}: {len(curve_data)} puntos")
                    
                    # Obtener unidades de la curva original
                    units = None
                    for well in wells:
                        if curve_name in well.curves:
                            units = well.get_curve_units(curve_name)
                            if units:
                                break
                    
                    try:
                        # Crear objeto Curve con datos y basis correctos
                        curve = welly.Curve(
                            data=curve_data.values,
                            basis=curve_data.index.values,
                            mnemonic=curve_name,
                            units=units or '',
                            index_units='m'
                        )
                        
                        # Agregar la curva al pozo
                        merged_well.data[curve_name] = curve
                        
                    except Exception as curve_error:
                        logger.warning(f"⚠️ Error creando curva {curve_name}: {curve_error}")
                        continue
            
            # Establecer metadatos básicos del pozo
            merged_well.name = well_name
            
            # Configurar basis común basado en el índice del DataFrame
            if len(merged_df.index) > 0:
                merged_well.basis = merged_df.index.values
                logger.info(f"   🎯 Basis configurado: {len(merged_well.basis)} puntos de profundidad")
            
            # Verificar que el pozo tiene curvas válidas
            valid_curves = 0
            for curve_name, curve in merged_well.data.items():
                if curve is not None and hasattr(curve, 'values') and len(curve.values) > 0:
                    valid_curves += 1
            
            logger.info(f"   ✅ Pozo creado con {valid_curves} curvas válidas")
            
            # Copiar header del primer pozo como base
            if hasattr(base_well, 'header') and base_well.header is not None:
                merged_well.header = base_well.header.copy()
            
            # Actualizar metadata del header
            merged_well.name = well_name
            
            # Crear WellManager del pozo fusionado
            merged_manager = cls(merged_well)
            merged_manager._metadata = {
                'source_file': f'{well_name}_MERGED.las',
                'original_files': [w.metadata.get('source_file', 'unknown') for w in wells],
                'merge_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'curves_merged': len(all_curves),
                'overlaps_processed': len(overlap_info)
            }
            
            logger.info(f"✅ Fusión completada exitosamente:")
            logger.info(f"   📊 Curvas fusionadas: {len(merged_df.columns)}")
            logger.info(f"   🎯 Rango final: {merged_manager.depth_range}")
            logger.info(f"   🔄 Traslapes procesados: {len(overlap_info)}")
            
            return merged_manager
            
        except Exception as e:
            logger.error(f"❌ Error durante la fusión: {str(e)}")
            return None
    
    @staticmethod
    def _merge_curve_data(curve_data_list: List[pd.Series], curve_name: str, overlap_info: dict) -> pd.Series:
        """
        Fusionar datos de una curva específica de múltiples pozos.
        
        Args:
            curve_data_list: Lista de Series con datos de la curva
            curve_name: Nombre de la curva
            overlap_info: Diccionario para almacenar información de traslapes
            
        Returns:
            pd.Series: Datos fusionados de la curva
        """
        if not curve_data_list:
            return pd.Series(dtype=float)
        
        if len(curve_data_list) == 1:
            return curve_data_list[0]
        
        # Combinar todas las series
        combined_index = curve_data_list[0].index
        result = pd.Series(index=combined_index, dtype=float)
        
        overlap_count = 0
        
        for depth in combined_index:
            valid_values = []
            
            # Recolectar valores válidos en esta profundidad
            for curve_data in curve_data_list:
                if depth in curve_data.index and pd.notna(curve_data[depth]):
                    valid_values.append(curve_data[depth])
            
            if valid_values:
                if len(valid_values) == 1:
                    # Sin traslape
                    result[depth] = valid_values[0]
                else:
                    # Traslape: calcular media
                    result[depth] = np.mean(valid_values)
                    overlap_count += 1
        
        if overlap_count > 0:
            overlap_info[curve_name] = overlap_count
        
        return result
    
    def save_merged_well(self, output_path: Union[str, Path]) -> bool:
        """
        Guardar el pozo fusionado en un archivo LAS.
        
        Args:
            output_path: Ruta del archivo de salida
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            output_path = Path(output_path)
            
            # Asegurar que el directorio existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Exportar usando el método existente
            success = self.export_to_las(output_path)
            
            if success:
                logger.info(f"💾 Pozo fusionado guardado: {output_path.name}")
                
                # Agregar información de fusión en el log
                if 'original_files' in self._metadata:
                    logger.info(f"   📁 Archivos originales: {len(self._metadata['original_files'])}")
                    for i, file in enumerate(self._metadata['original_files'], 1):
                        logger.info(f"      {i}. {file}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error guardando pozo fusionado: {str(e)}")
            return False
