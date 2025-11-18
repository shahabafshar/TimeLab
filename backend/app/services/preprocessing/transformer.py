"""
Time series transformer for stationarity testing
Adapted from arauto/lib/transformation_function.py
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from typing import Tuple, Callable, Optional


class TimeSeriesTransformer:
    """
    Transformer for testing different stationarity transformations
    Adapted from arauto/lib/transformation_function.py
    """
    
    SEASONALITY_DICT = {
        'Hourly': 24,
        'Daily': 7,
        'Monthly': 12,
        'Quarterly': 4,
        'Yearly': 5
    }
    
    def __init__(self, original_timeseries: pd.Series, data_frequency: str):
        self.seasonality = self.SEASONALITY_DICT.get(data_frequency, 12)
        self.original_timeseries = original_timeseries.dropna()
        
        # Validate we have data
        if len(self.original_timeseries) == 0:
            raise ValueError("Time series cannot be empty")
        if len(self.original_timeseries) < 3:
            raise ValueError(f"Time series must have at least 3 data points, got {len(self.original_timeseries)}")
        
        self.transformed_time_series = self.original_timeseries
        self.test_stationarity_code = None
        self.transformation_function: Callable = lambda x: x
        self.label: Optional[str] = None
        self.d = 0
        self.D = 0
    
    def test_absolute_data(self) -> Tuple:
        """Test original data without transformation"""
        self.dftest = adfuller(self.original_timeseries, autolag='AIC')
        self.test_stationarity_code = "dftest = adfuller(df, autolag='AIC')"
        self.label = 'Absolute' if self.dftest[0] < self.dftest[4]['1%'] else None
        self.d = 0
        self.D = 0
        
        return (
            self.dftest,
            self.transformed_time_series,
            self.label,
            self.d,
            self.D,
            self.transformation_function,
            self.test_stationarity_code,
            self.seasonality
        )
    
    def test_first_difference(self) -> Tuple:
        """Test with first difference"""
        self.transformed_time_series = self.original_timeseries.diff().dropna()
        if len(self.transformed_time_series) < 3:
            # Return a failed test if not enough data
            self.dftest = (float('inf'), 1.0, 0, 0, {'1%': 0, '5%': 0, '10%': 0})
            self.label = None
            self.d = 1
            self.D = 0
            return (
                self.dftest,
                self.transformed_time_series,
                self.label,
                self.d,
                self.D,
                self.transformation_function,
                self.test_stationarity_code,
                self.seasonality
            )
        self.dftest = adfuller(self.transformed_time_series, autolag='AIC')
        self.test_stationarity_code = "dftest = adfuller(df.diff().dropna(), autolag='AIC')"
        self.label = 'Difference' if self.dftest[0] < self.dftest[4]['1%'] else None
        self.d = 1
        self.D = 0
        
        return (
            self.dftest,
            self.transformed_time_series,
            self.label,
            self.d,
            self.D,
            self.transformation_function,
            self.test_stationarity_code,
            self.seasonality
        )
    
    def test_log_transformation(self) -> Tuple:
        """Test with log transformation"""
        self.transformed_time_series = np.log1p(self.original_timeseries)
        self.dftest = adfuller(self.transformed_time_series, autolag='AIC')
        self.transformation_function = np.log1p
        self.test_stationarity_code = "df = np.log1p(df)\ndftest = adfuller(np.log1p(df), autolag='AIC')"
        self.label = 'Log transformation' if self.dftest[0] < self.dftest[4]['1%'] else None
        self.d = 0
        self.D = 0
        
        return (
            self.dftest,
            self.transformed_time_series,
            self.label,
            self.d,
            self.D,
            self.transformation_function,
            self.test_stationarity_code,
            self.seasonality
        )
    
    def test_seasonal_difference(self) -> Tuple:
        """Test with seasonal difference"""
        self.transformed_time_series = self.original_timeseries.diff(self.seasonality).dropna()
        if len(self.transformed_time_series) < 3:
            # Return a failed test if not enough data
            self.dftest = (float('inf'), 1.0, 0, 0, {'1%': 0, '5%': 0, '10%': 0})
            self.label = None
            self.d = 0
            self.D = 1
            return (
                self.dftest,
                self.transformed_time_series,
                self.label,
                self.d,
                self.D,
                self.transformation_function,
                self.test_stationarity_code,
                self.seasonality
            )
        self.dftest = adfuller(self.transformed_time_series, autolag='AIC')
        self.transformation_function = lambda x: x
        self.test_stationarity_code = f"dftest = adfuller(df.diff({self.seasonality}).dropna(), autolag='AIC')"
        self.label = 'Seasonality Difference' if self.dftest[0] < self.dftest[4]['1%'] else None
        self.d = 0
        self.D = 1
        
        return (
            self.dftest,
            self.transformed_time_series,
            self.label,
            self.d,
            self.D,
            self.transformation_function,
            self.test_stationarity_code,
            self.seasonality
        )
    
    def test_log_difference(self) -> Tuple:
        """Test with log first difference"""
        self.transformed_time_series = np.log1p(self.original_timeseries).diff().dropna()
        self.dftest = adfuller(self.transformed_time_series, autolag='AIC')
        self.transformation_function = np.log1p
        self.test_stationarity_code = "df = np.log1p(df)\ndftest = adfuller(df.diff().dropna(), autolag='AIC')"
        self.label = 'Log Difference' if self.dftest[0] < self.dftest[4]['1%'] else None
        self.d = 1
        self.D = 0
        
        return (
            self.dftest,
            self.transformed_time_series,
            self.label,
            self.d,
            self.D,
            self.transformation_function,
            self.test_stationarity_code,
            self.seasonality
        )
    
    def test_seasonal_log_difference(self) -> Tuple:
        """Test with log difference + seasonal difference"""
        self.transformed_time_series = (
            np.log1p(self.original_timeseries)
            .diff()
            .diff(self.seasonality)
            .dropna()
        )
        if len(self.transformed_time_series) < 3:
            # Return a failed test if not enough data
            self.dftest = (float('inf'), 1.0, 0, 0, {'1%': 0, '5%': 0, '10%': 0})
            self.label = None
            self.d = 1
            self.D = 1
            return (
                self.dftest,
                self.transformed_time_series,
                self.label,
                self.d,
                self.D,
                self.transformation_function,
                self.test_stationarity_code,
                self.seasonality
            )
        self.dftest = adfuller(self.transformed_time_series, autolag='AIC')
        self.transformation_function = np.log1p
        self.test_stationarity_code = (
            f"df = np.log1p(df)\n"
            f"dftest = adfuller(df.diff().diff({self.seasonality}).dropna(), autolag='AIC')"
        )
        self.label = 'Log Difference + Seasonal Difference' if self.dftest[0] < self.dftest[4]['1%'] else None
        self.d = 1
        self.D = 1
        
        return (
            self.dftest,
            self.transformed_time_series,
            self.label,
            self.d,
            self.D,
            self.transformation_function,
            self.test_stationarity_code,
            self.seasonality
        )
    
    def test_custom_difference(self, custom_transformation_size: Tuple[int, int]) -> Tuple:
        """Test with custom difference"""
        self.d = custom_transformation_size[0]
        self.D = custom_transformation_size[1]
        
        self.transformed_time_series = (
            self.original_timeseries
            .diff(self.d)
            .diff(self.seasonality * self.D)
            .dropna()
        )
        self.dftest = adfuller(self.transformed_time_series, autolag='AIC')
        self.transformation_function = lambda x: x
        self.test_stationarity_code = (
            f"dftest = adfuller(df.diff({self.d}).diff({self.D}).dropna(), autolag='AIC')"
        )
        self.label = 'Custom Difference' if self.dftest[0] < self.dftest[4]['1%'] else None
        
        return (
            self.dftest,
            self.transformed_time_series,
            self.label,
            self.d,
            self.D,
            self.transformation_function,
            self.test_stationarity_code,
            self.seasonality
        )

