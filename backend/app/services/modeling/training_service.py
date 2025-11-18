"""
Model training service - adapted from arauto/lib/train_ts_model.py
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import pickle
import base64
from typing import Optional, Dict, Any


class TrainingService:
    """Service for training SARIMAX models"""
    
    @staticmethod
    def train_sarimax(
        Y: pd.Series,
        p: int,
        d: int,
        q: int,
        P: int,
        D: int,
        Q: int,
        s: int,
        exog_variables: Optional[pd.DataFrame] = None,
        quiet: bool = True
    ) -> Dict[str, Any]:
        """
        Train a SARIMAX model
        
        Adapted from arauto/lib/train_ts_model.py
        
        Args:
            Y: Time series data
            p, d, q: Non-seasonal ARIMA parameters
            P, D, Q, s: Seasonal ARIMA parameters
            exog_variables: Exogenous variables
            quiet: Suppress output
            
        Returns:
            Dict with model results and metadata
        """
        # Validate parameters to avoid conflicts
        # Check for overlapping lags between seasonal and non-seasonal components
        if q > 0 and Q > 0 and s > 0:
            # Check if any non-seasonal MA lag conflicts with seasonal MA lags
            non_seasonal_lags = set(range(1, q + 1))
            seasonal_lags = set(range(s, (Q * s) + 1, s))
            overlap = non_seasonal_lags.intersection(seasonal_lags)
            if overlap:
                raise ValueError(
                    f"Invalid model: moving average lag(s) {overlap} are in both the seasonal and non-seasonal moving average components. "
                    f"Try reducing q from {q} to {min(q, s - 1)} or reducing Q from {Q}."
                )
        
        # Validate parameter ranges
        if p < 0 or q < 0 or P < 0 or Q < 0:
            raise ValueError("ARIMA parameters must be non-negative")
        if s <= 0:
            raise ValueError("Seasonality (s) must be positive")
        if d < 0 or D < 0:
            raise ValueError("Differencing parameters (d, D) must be non-negative")
        
        # Cap parameters to reasonable values relative to data length
        min_length = len(Y)
        if p >= min_length or q >= min_length:
            raise ValueError(f"AR/MA parameters (p={p}, q={q}) are too large for data length ({min_length}). Maximum allowed: {min_length - 1}")
        
        # Create model
        mod = sm.tsa.statespace.SARIMAX(
            Y,
            order=(p, d, q),
            exog=exog_variables,
            seasonal_order=(P, D, Q, s),
            enforce_invertibility=False
        )
        
        try:
            results = mod.fit()
        except np.linalg.LinAlgError:
            # Retry with approximate_diffuse initialization
            mod = sm.tsa.statespace.SARIMAX(
                Y,
                order=(p, d, q),
                exog=exog_variables,
                seasonal_order=(P, D, Q, s),
                enforce_invertibility=False,
                initialization='approximate_diffuse'
            )
            results = mod.fit()
        
        # Serialize model
        model_data = TrainingService._serialize_model(results)
        
        # Get summary
        summary = str(results.summary())
        
        # Extract metrics
        metrics = {
            "aic": float(results.aic),
            "bic": float(results.bic),
            "hqic": float(results.hqic),
        }
        
        return {
            "model_data": model_data,
            "summary": summary,
            "metrics": metrics,
            "parameters": {
                "order": (p, d, q),
                "seasonal_order": (P, D, Q, s),
            },
        }
    
    @staticmethod
    def _serialize_model(model) -> str:
        """Serialize model to base64 string"""
        pickled = pickle.dumps(model)
        return base64.b64encode(pickled).decode('utf-8')
    
    @staticmethod
    def deserialize_model(model_data: str):
        """Deserialize model from base64 string"""
        pickled = base64.b64decode(model_data.encode('utf-8'))
        return pickle.loads(pickled)

