"""
Preprocessing API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from app.core.database import get_db
from app.models.dataset import Dataset
from app.schemas.preprocessing import TransformRequest, StationarityTestRequest, StationarityTestResponse
from app.services.preprocessing.transformation_service import TransformationService
from app.services.preprocessing.stationarity_service import StationarityService

router = APIRouter(prefix="/preprocessing", tags=["preprocessing"])


@router.post("/transform")
async def transform_time_series(
    request: TransformRequest,
    db: Session = Depends(get_db)
):
    """Transform DataFrame to time-indexed Series"""
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data
    if not dataset.file_path:
        raise HTTPException(status_code=400, detail="Dataset file not found")
    
    df = pd.read_csv(dataset.file_path)
    
    # Transform
    try:
        transformed_df, metadata = TransformationService.transform_dataframe(
            df,
            request.date_column,
            request.frequency,
            request.target_column
        )
        
        return {
            "success": True,
            "metadata": metadata,
            "columns": list(transformed_df.columns),
            "row_count": len(transformed_df),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/test-stationarity", response_model=StationarityTestResponse)
async def test_stationarity(request: StationarityTestRequest, db: Session = Depends(get_db)):
    """Test time series stationarity"""
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
        
        # Test stationarity
        result = StationarityService.test_stationarity(
            timeseries,
            request.frequency,
            request.force_transformation,
            request.custom_transformation_size
        )
        
        return StationarityTestResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transformations")
async def list_transformations():
    """List available transformation methods"""
    return {
        "transformations": [
            "No transformation",
            "First Difference",
            "Log transformation",
            "Seasonal Difference",
            "Log First Difference",
            "Log Difference + Seasonal Difference",
            "Custom Difference",
        ]
    }

