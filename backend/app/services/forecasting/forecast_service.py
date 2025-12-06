"""
Forecast service - adapted from arauto/lib/plot_forecast.py
"""
import pandas as pd
import numpy as np
from typing import Callable, Dict, Any, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ForecastService:
    """Service for generating forecasts"""

    @staticmethod
    def _generate_forecast_dates(
        last_date: Optional[str],
        frequency: Optional[str],
        periods: int
    ) -> list:
        """
        Generate forecast dates based on the last historical date and frequency.

        Args:
            last_date: Last date in historical data (e.g., "2023-12-01")
            frequency: Data frequency ("Daily", "Weekly", "Monthly", "Quarterly", "Yearly")
            periods: Number of forecast periods

        Returns:
            List of date strings in YYYY-MM-DD format
        """
        if not last_date or not frequency:
            # Fallback to Period_X format
            return [f"Period_{i+1}" for i in range(periods)]

        try:
            # Parse the last date
            base_date = pd.to_datetime(last_date)

            # Determine the date increment based on frequency
            freq_map = {
                "daily": relativedelta(days=1),
                "weekly": relativedelta(weeks=1),
                "monthly": relativedelta(months=1),
                "quarterly": relativedelta(months=3),
                "yearly": relativedelta(years=1),
                # Also support lowercase variations
                "d": relativedelta(days=1),
                "w": relativedelta(weeks=1),
                "m": relativedelta(months=1),
                "q": relativedelta(months=3),
                "y": relativedelta(years=1),
            }

            increment = freq_map.get(frequency.lower())
            if increment is None:
                # Default to monthly if frequency not recognized
                increment = relativedelta(months=1)

            # Generate forecast dates
            forecast_dates = []
            current_date = base_date
            for i in range(periods):
                current_date = current_date + increment
                forecast_dates.append(current_date.strftime('%Y-%m-%d'))

            return forecast_dates

        except Exception as e:
            # Fallback to Period_X format on any error
            print(f"Warning: Could not generate forecast dates: {e}")
            return [f"Period_{i+1}" for i in range(periods)]

    @staticmethod
    def generate_forecast(
        model,
        periods: int,
        transformation_type: str = "none",
        exog_variables: Optional[pd.DataFrame] = None,
        last_date: Optional[str] = None,
        frequency: Optional[str] = None
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

        # Generate forecast dates
        # Priority: 1) Use DatetimeIndex from model, 2) Generate from last_date + frequency, 3) Fallback to Period_X
        if isinstance(forecasts.index, pd.DatetimeIndex):
            forecast_dates = forecasts.index.strftime('%Y-%m-%d').tolist()
        elif last_date and frequency:
            # Generate dates from last_date and frequency
            forecast_dates = ForecastService._generate_forecast_dates(last_date, frequency, periods)
        else:
            # Fallback to Period_X format
            forecast_dates = [f"Period_{i+1}" for i in range(len(forecasts))]

        # CI dates match forecast dates
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
