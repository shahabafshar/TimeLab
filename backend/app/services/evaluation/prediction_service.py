"""
Prediction service - adapted from arauto/lib/predict_set.py
"""
import numpy as np
import pandas as pd
from typing import Callable, Optional, Dict, Any
from app.services.evaluation.metrics_service import MetricsService


class PredictionService:
    """Service for generating predictions and calculating metrics"""
    
    @staticmethod
    def predict_set(
        timeseries: pd.Series,
        target_column: str,
        seasonality: int,
        transformation_function: Callable,
        model,
        exog_variables: Optional[pd.DataFrame] = None,
        forecast: bool = False
    ) -> Dict[str, Any]:
        """
        Generate predictions and calculate metrics
        
        Adapted from arauto/lib/predict_set.py
        
        Args:
            timeseries: Time series data
            target_column: Name of target column
            seasonality: Seasonal frequency
            transformation_function: Function to apply inverse transformation
            model: Fitted model
            exog_variables: Exogenous variables
            forecast: Whether to forecast (True) or predict (False)
            
        Returns:
            Dict with predictions and metrics
        """
        # Convert to DataFrame
        df = timeseries.to_frame()
        df[target_column] = transformation_function(df[target_column])
        
        # Generate predictions
        if forecast:
            predictions = transformation_function(
                model.forecast(len(df), exog=exog_variables)
            )
        else:
            predictions = transformation_function(model.predict())
        
        df['predicted'] = predictions
        
        # Get last seasonality*3 periods for evaluation
        eval_periods = seasonality * 3
        actual_eval = df[target_column].iloc[-eval_periods:]
        predicted_eval = df['predicted'].iloc[-eval_periods:]
        
        # Calculate metrics
        metrics = MetricsService.calculate_all_metrics(actual_eval, predicted_eval)
        
        # Add model metrics
        metrics.update({
            "aic": float(model.aic),
            "bic": float(model.bic),
            "hqic": float(model.hqic),
        })
        
        # Prepare prediction data
        prediction_data = {
            "dates": df.index[-eval_periods:].astype(str).tolist(),
            "actual": actual_eval.tolist(),
            "predicted": predicted_eval.tolist(),
        }
        
        return {
            "predictions": prediction_data,
            "metrics": metrics,
        }

