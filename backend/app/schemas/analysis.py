"""
Analysis schemas
"""
from pydantic import BaseModel
from typing import Dict, List, Any, Optional


class ACFPACFRequest(BaseModel):
    # Option 1: Direct timeseries data
    timeseries_data: Optional[Dict[str, float]] = None  # {date: value}
    # Option 2: Dataset parameters (preferred)
    dataset_id: Optional[str] = None
    date_column: Optional[str] = None
    target_column: Optional[str] = None
    seasonality: int


class ACFPACFResponse(BaseModel):
    acf: List[float]
    pacf: List[float]
    lags: List[int]
    confidence_interval: Dict[str, float]
    suggested_parameters: Dict[str, int]


class DecompositionRequest(BaseModel):
    timeseries_data: Dict[str, float]


class DecompositionResponse(BaseModel):
    trend: Dict[str, float]
    seasonal: Dict[str, float]
    residual: Dict[str, float]
    observed: Dict[str, float]

