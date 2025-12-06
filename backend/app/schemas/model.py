"""
Model schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List


class ModelParameters(BaseModel):
    p: int
    d: int
    q: int
    P: int
    D: int
    Q: int
    s: int


class ModelCreate(BaseModel):
    name: str
    type: str = "SARIMAX"
    parameters: ModelParameters
    project_id: Optional[str] = None


class ModelResponse(BaseModel):
    id: str
    name: str
    type: str
    parameters: Dict[str, Any]  # Changed from Dict[str, int] to allow strings (glp) and floats (d, lambda)
    metrics: Optional[Dict[str, Optional[float]]] = None  # Changed to allow None values for individual metrics
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


class ARTFIMAParameters(BaseModel):
    p: int
    d: float
    q: int
    glp: str  # "ARTFIMA", "ARFIMA", or "ARIMA"
    lambda_param: Optional[float] = None
    fixd: Optional[float] = None


class TrainModelRequest(BaseModel):
    # Option 1: Direct timeseries data
    timeseries_data: Optional[Dict[str, float]] = None  # {date: value}
    # Option 2: Dataset parameters (preferred)
    dataset_id: Optional[str] = None
    date_column: Optional[str] = None
    target_column: Optional[str] = None
    parameters: ModelParameters
    exog_variables: Optional[Dict[str, List[float]]] = None
    model_type: Optional[str] = "SARIMAX"  # "SARIMAX" or "ARTFIMA"
    artfima_parameters: Optional[ARTFIMAParameters] = None
    
    model_config = ConfigDict(protected_namespaces=())


class GridSearchRequest(BaseModel):
    timeseries_data: Dict[str, float]
    p_range: List[int]
    q_range: List[int]
    P_range: List[int]
    Q_range: List[int]
    d: int = 1
    D: int = 1
    s: int = 12
    exog_variables: Optional[Dict[str, List[float]]] = None


class PredictionRequest(BaseModel):
    model_id: str
    timeseries_data: Dict[str, float]
    seasonality: int
    transformation_type: str
    forecast: bool = False
    
    model_config = ConfigDict(protected_namespaces=())


class ForecastRequest(BaseModel):
    periods: int
    transformation_type: Optional[str] = "none"
    last_date: Optional[str] = None  # Last date in the historical data (e.g., "2023-12-01")
    frequency: Optional[str] = None  # Frequency: "Daily", "Weekly", "Monthly", "Quarterly", "Yearly"

    model_config = ConfigDict(protected_namespaces=())

