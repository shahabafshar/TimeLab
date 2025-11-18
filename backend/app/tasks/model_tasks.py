"""
Celery tasks for model operations
"""
import pandas as pd
from app.tasks.celery_app import celery_app
from app.services.modeling.grid_search_service import GridSearchService


@celery_app.task(name="grid_search_task")
def grid_search_task(
    train_data_dict: dict,
    p_range: list,
    q_range: list,
    P_range: list,
    Q_range: list,
    d: int,
    D: int,
    s: int,
    exog_dict: dict = None
):
    """
    Async task for grid search
    
    Args:
        train_data_dict: Serialized time series data
        p_range, q_range, P_range, Q_range: Parameter ranges
        d, D, s: Fixed parameters
        exog_dict: Optional exogenous variables
        
    Returns:
        Best parameter tuple
    """
    # Deserialize data
    train_data = pd.Series(train_data_dict)
    train_data.index = pd.to_datetime(train_data.index)
    
    exog = None
    if exog_dict:
        exog = pd.DataFrame(exog_dict)
        exog.index = pd.to_datetime(exog.index)
    
    # Run grid search
    best_params = GridSearchService.grid_search_arima(
        train_data,
        exog,
        p_range,
        q_range,
        P_range,
        Q_range,
        d,
        D,
        s
    )
    
    return {
        "p": best_params[0],
        "d": best_params[1],
        "q": best_params[2],
        "P": best_params[3],
        "D": best_params[4],
        "Q": best_params[5],
        "s": best_params[6],
    }

