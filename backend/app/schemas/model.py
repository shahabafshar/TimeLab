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
    parameters: Dict[str, int]
    metrics: Optional[Dict[str, float]] = None
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


class TrainModelRequest(BaseModel):
    # Option 1: Direct timeseries data
    timeseries_data: Optional[Dict[str, float]] = None  # {date: value}
    # Option 2: Dataset parameters (preferred)
    dataset_id: Optional[str] = None
    date_column: Optional[str] = None
    target_column: Optional[str] = None
    parameters: ModelParameters
    exog_variables: Optional[Dict[str, List[float]]] = None


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
    
    model_config = ConfigDict(protected_namespaces=())

