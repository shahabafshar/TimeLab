"""
Preprocessing schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, Tuple


class TransformRequest(BaseModel):
    dataset_id: str
    date_column: str
    frequency: str
    target_column: str


class StationarityTestRequest(BaseModel):
    # Option 1: Direct timeseries data
    timeseries_data: Optional[Dict[str, float]] = None  # {date: value}
    # Option 2: Dataset parameters (preferred)
    dataset_id: Optional[str] = None
    date_column: Optional[str] = None
    target_column: Optional[str] = None
    frequency: str
    force_transformation: Optional[str] = None
    custom_transformation_size: Optional[Tuple[int, int]] = None


class StationarityTestResponse(BaseModel):
    is_stationary: bool
    test_statistic: float
    p_value: float
    critical_values: Dict[str, float]
    transformation: Dict[str, Any]
    seasonality: int
    warnings: list[str]

