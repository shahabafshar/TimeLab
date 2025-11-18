"""
Stationarity testing service - adapted from arauto/lib/test_stationary.py
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from app.services.preprocessing.transformer import TimeSeriesTransformer


class StationarityService:
    """Service for testing time series stationarity"""
    
    @staticmethod
    def test_stationarity(
        timeseries: pd.Series,
        data_frequency: str,
        force_transformation: Optional[str] = None,
        custom_transformation_size: Optional[Tuple[int, int]] = None
    ) -> Dict[str, Any]:
        """
        Test stationarity and find best transformation
        
        Adapted from arauto/lib/test_stationary.py
        
        Args:
            timeseries: Time series to test
            data_frequency: Frequency of the data
            force_transformation: Force a specific transformation
            custom_transformation_size: Custom (d, D) values
            
        Returns:
            Dict with test results and transformation info
        """
        transformer = TimeSeriesTransformer(timeseries, data_frequency)
        
        if force_transformation and force_transformation != 'Choose the best one':
            best_transformation = StationarityService._apply_forced_transformation(
                transformer,
                force_transformation,
                custom_transformation_size
            )
        else:
            # Test all transformations and find best
            best_transformation = StationarityService._find_best_transformation(transformer)
        
        # Extract results
        dftest, transformed_series, label, d, D, transform_func, code, seasonality = best_transformation
        
        # Prepare result
        result = {
            "is_stationary": label is not None,
            "test_statistic": float(dftest[0]),
            "p_value": float(dftest[1]),
            "lags_used": int(dftest[2]),
            "observations": int(dftest[3]),
            "critical_values": {
                "1%": float(dftest[4]['1%']),
                "5%": float(dftest[4]['5%']),
                "10%": float(dftest[4]['10%']),
            },
            "transformation": {
                "type": label or "None",
                "d": d,
                "D": D,
                "code": code,
            },
            "seasonality": seasonality,
            "transformed_data": transformed_series.to_dict(),
            "warnings": [],
        }
        
        # Add warning if not statistically significant
        if not result["is_stationary"]:
            result["warnings"].append(
                f"Transformation '{label or 'None'}' is not statistically significant. "
                f"Test statistic: {result['test_statistic']:.3f}, "
                f"Critical value (1%): {result['critical_values']['1%']:.3f}"
            )
        
        return result
    
    @staticmethod
    def _apply_forced_transformation(
        transformer: TimeSeriesTransformer,
        transformation: str,
        custom_size: Optional[Tuple[int, int]]
    ) -> Tuple:
        """Apply a forced transformation"""
        transformation_map = {
            'No transformation': transformer.test_absolute_data,
            'First Difference': transformer.test_first_difference,
            'Log transformation': transformer.test_log_transformation,
            'Seasonal Difference': transformer.test_seasonal_difference,
            'Log First Difference': transformer.test_log_difference,
            'Log Difference + Seasonal Difference': transformer.test_seasonal_log_difference,
            'Custom Difference': lambda: transformer.test_custom_difference(custom_size) if custom_size else None,
        }
        
        if transformation not in transformation_map:
            raise ValueError(f"Unknown transformation: {transformation}")
        
        func = transformation_map[transformation]
        if func is None:
            raise ValueError("Custom transformation requires custom_transformation_size")
        
        return func()
    
    @staticmethod
    def _find_best_transformation(transformer: TimeSeriesTransformer) -> Tuple:
        """Test all transformations and find the best one"""
        transformations = []
        
        # Test each transformation, catching any errors
        try:
            transformations.append(transformer.test_absolute_data())
        except Exception:
            pass
        
        try:
            transformations.append(transformer.test_first_difference())
        except Exception:
            pass
        
        try:
            transformations.append(transformer.test_log_difference())
        except Exception:
            pass
        
        try:
            transformations.append(transformer.test_log_transformation())
        except Exception:
            pass
        
        try:
            transformations.append(transformer.test_seasonal_difference())
        except Exception:
            pass
        
        try:
            transformations.append(transformer.test_seasonal_log_difference())
        except Exception:
            pass
        
        if len(transformations) == 0:
            raise ValueError("All transformations failed. Check your data.")
        
        # Start with first successful transformation as baseline
        best = transformations[0]
        
        # Find transformation with lowest test statistic that is significant
        for trans in transformations[1:]:
            dftest = trans[0]
            label = trans[2]
            # Lower test statistic is better, and must be significant
            # Also check that dftest[0] is not infinity
            if (label is not None and 
                dftest[0] != float('inf') and 
                best[0][0] != float('inf') and
                dftest[0] < best[0][0]):
                best = trans
        
        return best

