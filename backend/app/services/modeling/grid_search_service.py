"""
Grid search service - adapted from arauto/lib/grid_search_arima.py
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Optional, Tuple, List


class GridSearchService:
    """Service for hyperparameter optimization via grid search"""
    
    @staticmethod
    def grid_search_arima(
        train_data: pd.Series,
        exog: Optional[pd.DataFrame],
        p_range: List[int],
        q_range: List[int],
        P_range: List[int],
        Q_range: List[int],
        d: int = 1,
        D: int = 1,
        s: int = 12
    ) -> Tuple[int, int, int, int, int, int, int]:
        """
        Grid search for SARIMAX models
        
        Adapted from arauto/lib/grid_search_arima.py
        
        Args:
            train_data: Training time series
            exog: Exogenous variables
            p_range, q_range, P_range, Q_range: Parameter ranges to search
            d, D, s: Fixed parameters
            
        Returns:
            Best parameter tuple (p, d, q, P, D, Q, s)
        """
        best_model_aic = np.Inf
        best_model_bic = np.Inf
        best_model_hqic = np.Inf
        best_model_order = (0, d, 0, 0, D, 0, s)
        current_best_model = None
        
        for p_ in p_range:
            for q_ in q_range:
                for P_ in P_range:
                    for Q_ in Q_range:
                        try:
                            no_of_lower_metrics = 0
                            
                            model = sm.tsa.statespace.SARIMAX(
                                endog=train_data,
                                order=(p_, d, q_),
                                exog=exog,
                                seasonal_order=(P_, D, Q_, s),
                                enforce_invertibility=False
                            ).fit()
                            
                            # Check if this model improves metrics
                            if model.aic <= best_model_aic:
                                no_of_lower_metrics += 1
                            if model.bic <= best_model_bic:
                                no_of_lower_metrics += 1
                            if model.hqic <= best_model_hqic:
                                no_of_lower_metrics += 1
                            
                            # Update best if at least 2 metrics improved
                            if no_of_lower_metrics >= 2:
                                best_model_aic = np.round(model.aic, 0)
                                best_model_bic = np.round(model.bic, 0)
                                best_model_hqic = np.round(model.hqic, 0)
                                best_model_order = (p_, d, q_, P_, D, Q_, s)
                                current_best_model = model
                                
                        except Exception:
                            # Skip invalid parameter combinations
                            pass
        
        return best_model_order

