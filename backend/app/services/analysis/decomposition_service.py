"""
Seasonal decomposition service - adapted from arauto/lib/decompose_series.py
"""
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from typing import Dict, Any


class DecompositionService:
    """Service for seasonal decomposition"""
    
    @staticmethod
    def decompose_series(timeseries: pd.Series) -> Dict[str, Any]:
        """
        Decompose time series into trend, seasonal, and residual components
        
        Adapted from arauto/lib/decompose_series.py
        
        Args:
            timeseries: Time series to decompose
            
        Returns:
            Dict with decomposition components
        """
        try:
            decomposition = seasonal_decompose(timeseries)
            
            # Convert to dict format
            result = {
                "trend": decomposition.trend.dropna().to_dict(),
                "seasonal": decomposition.seasonal.dropna().to_dict(),
                "residual": decomposition.resid.dropna().to_dict(),
                "observed": decomposition.observed.dropna().to_dict(),
            }
            
            return result
            
        except AttributeError as e:
            raise ValueError(
                "DATE column is not in proper format. "
                "Ensure it's in a valid format for Pandas to_datetime function."
            ) from e

