"""
Time series transformation service - adapted from arauto/lib/transform_time_series.py
"""
import pandas as pd
import numpy as np
from pandas import DatetimeIndex, date_range, merge
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm
from typing import Tuple, Dict, Any, Optional


class TransformationService:
    """Service for transforming DataFrames to time-indexed Series"""
    
    FREQUENCY_MAP = {
        'Hourly': 'H',
        'Daily': 'D',
        'Monthly': 'MS',
        'Quarterly': 'Q',
        'Yearly': 'Y'
    }
    
    @staticmethod
    def _test_time_series(ts: pd.Series) -> None:
        """
        Test that time series has valid datetime index
        
        Adapted from arauto/lib/transform_time_series.py
        """
        # Decomposing series to test datetime index
        seasonal_decompose(ts)
        
        # Training a simple model to test
        mod = sm.tsa.statespace.SARIMAX(ts, order=(0, 0, 1))
        results = mod.fit()
        
        # Check that forecast index is datetime
        forecast_index = results.forecast(10).index[0]
        if isinstance(forecast_index, (int, float)):
            raise TypeError('The forecasts index is not a datetime type')
    
    @staticmethod
    def transform_dataframe(
        df: pd.DataFrame,
        date_column: str,
        frequency: str,
        target_column: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Transform DataFrame to time-indexed Series
        
        Adapted from arauto/lib/transform_time_series.py
        
        Args:
            df: DataFrame to transform
            date_column: Column name to use as index
            frequency: Data frequency (Hourly, Daily, etc.)
            target_column: Target column name
            
        Returns:
            Tuple of (transformed DataFrame, metadata dict)
        """
        metadata = {
            "warnings": [],
            "errors": [],
        }
        
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Set date column as index
        df.set_index(date_column, inplace=True)
        df = df.dropna()
        
        try:
            # Try simple datetime conversion
            df.index = pd.to_datetime(df.index)
            TransformationService._test_time_series(df[target_column])
            metadata["method"] = "direct_conversion"
            
        except Exception:
            # Try frequency inference
            try:
                date_format = DatetimeIndex(df.index[-10:], freq='infer')
                df.index = df.asfreq(date_format.freq, fill_value=0)
                TransformationService._test_time_series(df[target_column])
                metadata["method"] = "frequency_inference"
                
            except ValueError:
                # Fill missing dates
                try:
                    fill_date_range = date_range(
                        df.index.min(),
                        df.index.max(),
                        freq=date_format.freq
                    )
                    df = merge(
                        fill_date_range.to_frame().drop(0, axis=1),
                        df,
                        how='left',
                        right_index=True,
                        left_index=True
                    )
                    
                    # Fill null values
                    null_values = df[df.loc[:, target_column].isnull()].index.values
                    if len(null_values) > 0:
                        metadata["warnings"].append(
                            f"Found null values at {null_values}. Filling with zeros."
                        )
                        df = df.fillna(0)
                    
                    TransformationService._test_time_series(df[target_column])
                    metadata["method"] = "fill_missing_dates"
                    
                except Exception:
                    # Use frequency from user input
                    try:
                        freq_str = TransformationService.FREQUENCY_MAP.get(frequency)
                        if not freq_str:
                            raise ValueError(f"Unknown frequency: {frequency}")
                        
                        metadata["warnings"].append(
                            "Could not infer date frequency. Using provided frequency."
                        )
                        df = df.asfreq(freq_str)
                        
                        # Fill null values
                        null_values = df[df.loc[:, target_column].isnull()].index.values
                        if len(null_values) > 0:
                            metadata["warnings"].append(
                                f"Found null values at {null_values}. Filling with zeros."
                            )
                            df = df.fillna(0)
                        
                        TransformationService._test_time_series(df[target_column])
                        metadata["method"] = "user_frequency"
                        
                    except Exception as e:
                        error_msg = (
                            "There was a problem converting the DATE column to a valid format. "
                            "Ensure there are no null values in the DATE column and that it is "
                            "in a valid format for Pandas to_datetime function."
                        )
                        metadata["errors"].append(error_msg)
                        raise TypeError(error_msg) from e
        
        return df, metadata

