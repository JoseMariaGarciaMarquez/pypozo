"""
Módulo de completado neuronal de pozos y curvas.
"""


import numpy as np
import pandas as pd
from typing import List, Optional

class NeuralCompletion:
    """
    Clase para analizar y completar una curva faltante en un pozo usando relaciones multivariadas y redes neuronales.
    """
    def __init__(self, well):
        self.well = well  # Debe tener .data (DataFrame) y .name

    def analyze_curve_relations(self, target_curve: str, input_curves: Optional[List[str]] = None):
        """
        Analiza la relación entre la curva objetivo y las demás curvas disponibles.
        Devuelve un dict con correlaciones, rangos y estadísticas útiles para el modelado.
        Solo incluye curvas realmente presentes en el DataFrame.
        """
        df = self.well.data
        if target_curve not in df.columns:
            raise ValueError(f"Curva objetivo '{target_curve}' no encontrada en el pozo.")
        # Filtrar input_curves a solo las que existen
        if input_curves is None:
            input_curves = [col for col in df.columns if col != target_curve]
        else:
            input_curves = [col for col in input_curves if col in df.columns and col != target_curve]
        # Solo usar filas donde target_curve y todas las input_curves no sean NaN
        if not input_curves:
            # No hay curvas de entrada válidas
            return {
                'correlations': {},
                'target_stats': {},
                'input_stats': {},
                'depth_range': None
            }
        valid = df[[target_curve] + input_curves].dropna()
        stats = {}
        # Correlaciones lineales
        if not valid.empty:
            corr = valid.corr()[target_curve].drop(target_curve)
            stats['correlations'] = corr.to_dict()
            # Estadísticas básicas
            stats['target_stats'] = valid[target_curve].describe().to_dict()
            stats['input_stats'] = {col: valid[col].describe().to_dict() for col in input_curves}
        else:
            stats['correlations'] = {}
            stats['target_stats'] = {}
            stats['input_stats'] = {}
        # Rango de profundidad (si existe columna 'DEPTH' o similar)
        for depth_col in ['DEPTH', 'Depth', 'depth', 'MD']:
            if depth_col in df.columns:
                stats['depth_range'] = (df[depth_col].min(), df[depth_col].max())
                break
        else:
            stats['depth_range'] = None
        return stats

    def get_training_data(self, target_curve: str, input_curves: Optional[List[str]] = None):
        """
        Prepara los datos de entrenamiento para la red neuronal: X = input_curves, y = target_curve.
        Solo usa filas donde target_curve y todas las input_curves están presentes.
        """
        df = self.well.data
        # Filtrar input_curves a solo las que existen en el DataFrame
        if input_curves is None:
            input_curves = [col for col in df.columns if col != target_curve]
        else:
            input_curves = [col for col in input_curves if col in df.columns]
        # Si no hay input_curves válidas, retornar arrays vacíos
        if not input_curves:
            return np.array([]), np.array([])
        valid = df[[target_curve] + input_curves].dropna()
        X = valid[input_curves].values
        y = valid[target_curve].values
        return X, y

    def get_prediction_data(self, target_curve: str, input_curves: Optional[List[str]] = None):
        """
        Prepara los datos donde la curva objetivo está ausente pero las input_curves están presentes.
        Devuelve X_pred (para predecir) y los índices en el DataFrame original.
        """
        df = self.well.data
        # Filtrar input_curves a solo las que existen en el DataFrame
        if input_curves is None:
            input_curves = [col for col in df.columns if col != target_curve]
        else:
            input_curves = [col for col in input_curves if col in df.columns]
        # Si no hay input_curves válidas, retornar arrays vacíos
        if not input_curves:
            return np.array([]), []
        mask_missing = df[target_curve].isna()
        mask_inputs = df[input_curves].notna().all(axis=1)
        mask = mask_missing & mask_inputs
        # Convertir a DataFrame de pandas si no lo es
        if not isinstance(df, pd.DataFrame):
            df_pd = df.to_pandas() if hasattr(df, 'to_pandas') else pd.DataFrame(df)
        else:
            df_pd = df
        X_pred = df_pd.loc[mask, input_curves].values
        idx = df_pd.index[mask]
        return X_pred, idx

    def complete(self, target_curve: str, input_curves: Optional[List[str]] = None, model_type: str = 'mlp', epochs: int = 100, verbose: bool = False, force: bool = False):
        """
        Completa la curva objetivo usando un modelo robusto según la cantidad de datos.
        Si hay pocos datos, usa regresión lineal o Ridge y avisa a la UI.
        Si force=True, permite completar aunque haya pocos datos.
        Devuelve un dict con métricas, cantidad de valores completados y flag de pocos datos.
        """
        from sklearn.neural_network import MLPRegressor
        from sklearn.linear_model import Ridge, LinearRegression
        from sklearn.metrics import mean_squared_error, r2_score
        X_train, y_train = self.get_training_data(target_curve, input_curves)
        X_pred, idx_pred = self.get_prediction_data(target_curve, input_curves)
        if len(X_pred) == 0:
            return {"completed": 0, "train_r2": None, "train_rmse": None, "few_data": False}
        FEW_DATA_THRESHOLD = 30
        few_data = len(X_train) < FEW_DATA_THRESHOLD
        if few_data and not force:
            # No entrenar, solo avisar a la UI
            return {"completed": 0, "train_r2": None, "train_rmse": None, "few_data": True, "n_train": len(X_train)}
        # Elegir modelo según cantidad de datos
        if few_data:
            # Modelo simple y robusto
            if len(X_train) >= 5:
                model = Ridge(alpha=1.0)
            else:
                model = LinearRegression()
        else:
            model = MLPRegressor(hidden_layer_sizes=(32, 32), max_iter=epochs, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_pred)
        # Métricas de entrenamiento
        y_train_pred = model.predict(X_train)
        train_r2 = r2_score(y_train, y_train_pred)
        train_rmse = mean_squared_error(y_train, y_train_pred, squared=False)
        # Rellenar los valores faltantes usando la API de WellDataFrame
        # Obtener la curva original como pd.Series
        curve_series = self.well.data[target_curve].copy()
        # idx_pred puede ser un Index; convertir a lista si es necesario
        if hasattr(idx_pred, 'tolist'):
            idx_pred = idx_pred.tolist()
        # Asignar los valores predichos solo en los índices faltantes
        for i, idx in enumerate(idx_pred):
            curve_series[idx] = y_pred[i]
        # Reasignar la curva completa al pozo
        self.well.data[target_curve] = curve_series
        if verbose:
            print(f"Completados {len(y_pred)} valores en '{target_curve}'. R2 entrenamiento: {train_r2:.3f}, RMSE: {train_rmse:.3f}")
        return {"completed": len(y_pred), "train_r2": train_r2, "train_rmse": train_rmse, "few_data": few_data, "n_train": len(X_train)}
