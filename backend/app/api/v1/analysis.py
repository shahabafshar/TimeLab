"""
Analysis API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dataset import Dataset
from app.schemas.analysis import (
    ACFPACFRequest,
    ACFPACFResponse,
    DecompositionRequest,
    DecompositionResponse
)
from app.services.analysis.acf_pacf_service import ACFPACFService
from app.services.analysis.decomposition_service import DecompositionService

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/acf-pacf", response_model=ACFPACFResponse)
async def calculate_acf_pacf(request: ACFPACFRequest, db: Session = Depends(get_db)):
    """Calculate ACF and PACF values"""
    try:
        timeseries = None
        
        # Option 1: Load from dataset (preferred)
        if request.dataset_id and request.date_column and request.target_column:
            # Get dataset
            dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")
            
            if not dataset.file_path:
                raise HTTPException(status_code=400, detail="Dataset file not found")
            
            # Load and transform data
            df = pd.read_csv(dataset.file_path)
            
            # Validate columns exist
            if request.date_column not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Date column '{request.date_column}' not found in dataset"
                )
            if request.target_column not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Target column '{request.target_column}' not found in dataset"
                )
            
            # Transform to time series
            df[request.date_column] = pd.to_datetime(df[request.date_column])
            df = df.set_index(request.date_column)
            timeseries = df[request.target_column].dropna()
            
            # Validate we have data
            if len(timeseries) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No valid data points found after processing"
                )
        
        # Option 2: Use provided timeseries_data
        elif request.timeseries_data:
            if len(request.timeseries_data) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="timeseries_data cannot be empty"
                )
            timeseries = pd.Series(request.timeseries_data)
            timeseries.index = pd.to_datetime(timeseries.index)
            timeseries = timeseries.dropna()
            
            if len(timeseries) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No valid data points found after processing"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either provide dataset_id+date_column+target_column or timeseries_data"
            )
        
        # Calculate ACF/PACF
        result = ACFPACFService.find_acf_pacf(timeseries, request.seasonality)
        
        return ACFPACFResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/decompose", response_model=DecompositionResponse)
async def decompose_series(request: DecompositionRequest):
    """Perform seasonal decomposition"""
    try:
        # Convert dict to Series
        timeseries = pd.Series(request.timeseries_data)
        timeseries.index = pd.to_datetime(timeseries.index)
        
        # Decompose
        result = DecompositionService.decompose_series(timeseries)
        
        return DecompositionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics")
async def get_statistics(timeseries_data: Dict[str, float]):
    """Get descriptive statistics"""
    try:
        series = pd.Series(timeseries_data)
        
        return {
            "mean": float(series.mean()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
            "median": float(series.median()),
            "count": int(len(series)),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

