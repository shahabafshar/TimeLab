"""
Metrics calculation service - adapted from arauto/lib/mean_abs_pct_error.py
"""
import numpy as np
import pandas as pd
from math import sqrt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Union


class MetricsService:
    """Service for calculating evaluation metrics"""
    
    @staticmethod
    def mean_abs_pct_error(
        actual_values: Union[pd.Series, np.ndarray, list],
        forecast_values: Union[pd.Series, np.ndarray, list]
    ) -> float:
        """
        Calculate Mean Absolute Percentage Error (MAPE)
        
        Adapted from arauto/lib/mean_abs_pct_error.py
        
        Args:
            actual_values: True values
            forecast_values: Predicted values
            
        Returns:
            MAPE value as percentage
        """
        if isinstance(actual_values, pd.Series):
            actual = actual_values
        else:
            actual = pd.Series(actual_values)
            
        if isinstance(forecast_values, pd.Series):
            forecast = forecast_values
        else:
            forecast = pd.Series(forecast_values)
        
        err = 0
        for i in range(len(forecast)):
            if actual.iloc[i] != 0:  # Avoid division by zero
                err += np.abs(actual.iloc[i] - forecast.iloc[i]) / abs(actual.iloc[i])
        
        return err * 100 / len(forecast)
    
    @staticmethod
    def calculate_all_metrics(
        actual: Union[pd.Series, np.ndarray, list],
        predicted: Union[pd.Series, np.ndarray, list]
    ) -> dict:
        """
        Calculate all evaluation metrics
        
        Returns:
            Dict with RMSE, MAE, MAPE
        """
        if isinstance(actual, pd.Series):
            actual_series = actual
        else:
            actual_series = pd.Series(actual)
            
        if isinstance(predicted, pd.Series):
            pred_series = predicted
        else:
            pred_series = pd.Series(predicted)
        
        rmse = sqrt(mean_squared_error(actual_series, pred_series))
        mae = mean_absolute_error(actual_series, pred_series)
        mape = MetricsService.mean_abs_pct_error(actual_series, pred_series)
        
        return {
            "rmse": float(rmse),
            "mae": float(mae),
            "mape": float(mape),
        }

