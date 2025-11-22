"""
Forecast service - adapted from arauto/lib/plot_forecast.py
"""
import pandas as pd
import numpy as np
from typing import Callable, Dict, Any, Optional


class ForecastService:
    """Service for generating forecasts"""
    
    @staticmethod
    def generate_forecast(
        model,
        periods: int,
        transformation_type: str = "none",
        exog_variables: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Generate out-of-sample forecasts with confidence intervals
        
        Adapted from arauto/lib/plot_forecast.py
        
        Args:
            model: Fitted model
            periods: Number of periods to forecast
            transformation_type: Type of transformation ("log" or "none")
            exog_variables: Future exogenous variables (if available)
            
        Returns:
            Dict with forecasts and confidence intervals
        """
        # Check if this is an ARTFIMA model
        # Try to import ARTFIMAResult - handle import errors gracefully
        try:
            from artfima_python.artfima import ARTFIMAResult
            is_artfima = isinstance(model, ARTFIMAResult)
        except (ImportError, AttributeError):
            # Check by class name as fallback
            is_artfima = model.__class__.__name__ == 'ARTFIMAResult'
        is_log_transform = transformation_type.lower() == "log"
        
        try:
            if is_artfima:
                # ARTFIMA model - use its forecast method
                forecast_result = model.forecast(n_ahead=periods)
                forecasts = forecast_result['Forecasts']
                forecast_sd = forecast_result['SDForecasts']
                
                # Convert to pandas Series
                forecasts = pd.Series(forecasts)
                
                # Create confidence intervals (95% CI: ±1.96 * SD)
                z_score = 1.96  # 95% confidence interval
                ci_lower = forecasts - z_score * forecast_sd
                ci_upper = forecasts + z_score * forecast_sd
                confidence_interval = pd.DataFrame({
                    'ci_lower': ci_lower,
                    'ci_upper': ci_upper
                })
                
                # Apply transformation if needed
                if is_log_transform:
                    forecasts = np.expm1(forecasts)
                    confidence_interval = np.expm1(confidence_interval)
            else:
                # SARIMAX model - use standard forecast method
                if is_log_transform:
                    forecasts = np.expm1(model.forecast(periods, exog=exog_variables))
                    forecast_obj = model.get_forecast(periods, exog=exog_variables)
                    confidence_interval = np.expm1(forecast_obj.conf_int())
                else:
                    forecasts = model.forecast(periods, exog=exog_variables)
                    forecast_obj = model.get_forecast(periods, exog=exog_variables)
                    confidence_interval = forecast_obj.conf_int()
        except Exception as e:
            raise ValueError(f"Failed to generate forecast: {str(e)}")
        
        # Rename confidence interval columns
        confidence_interval.columns = ['ci_lower', 'ci_upper']
        
        # Convert forecasts to Series if it's not already
        if not isinstance(forecasts, pd.Series):
            forecasts = pd.Series(forecasts)
        
        # Ensure we have a proper index (DatetimeIndex or RangeIndex)
        if not isinstance(forecasts.index, pd.DatetimeIndex):
            # If index is not datetime, create a range index
            forecasts.index = pd.RangeIndex(start=0, stop=len(forecasts))
        
        # Convert index to string dates
        if isinstance(forecasts.index, pd.DatetimeIndex):
            forecast_dates = forecasts.index.strftime('%Y-%m-%d').tolist()
        else:
            # If not datetime, create date strings from the last known date + periods
            # This is a fallback - ideally the model should have datetime index
            forecast_dates = [f"Period_{i+1}" for i in range(len(forecasts))]
        
        # Ensure confidence interval index matches
        if isinstance(confidence_interval.index, pd.DatetimeIndex):
            ci_dates = confidence_interval.index.strftime('%Y-%m-%d').tolist()
        else:
            ci_dates = forecast_dates
        
        # Prepare result
        return {
            "forecasts": {
                "dates": forecast_dates,
                "values": forecasts.tolist(),
            },
            "confidence_intervals": {
                "dates": ci_dates,
                "lower": confidence_interval['ci_lower'].tolist(),
                "upper": confidence_interval['ci_upper'].tolist(),
            },
        }
