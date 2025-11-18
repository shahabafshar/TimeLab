"""
Dataset API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.schemas.dataset import DatasetResponse, DatasetUploadResponse, LoadSampleRequest
from app.services.data.import_service import DataImportService
from app.models.dataset import Dataset
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/datasets", tags=["datasets"])


class SampleDatasetInfo(BaseModel):
    filename: str
    name: str
    description: str
    frequency: str
    rows: int
    columns: list[str]


@router.get("/samples", response_model=List[SampleDatasetInfo])
def list_sample_datasets():
    """
    List all available sample datasets
    """
    samples_dir = Path(settings.SAMPLES_DIR)
    if not samples_dir.exists():
        return []
    
    samples = []
    sample_info = {
        "air_passengers.csv": {
            "name": "Air Passengers",
            "description": "Monthly totals of international airline passengers (1949-1960)",
            "frequency": "Monthly",
            "columns": ["date", "passengers"]
        },
        "co2_levels.csv": {
            "name": "CO2 Levels",
            "description": "Monthly atmospheric CO2 concentrations at Mauna Loa Observatory",
            "frequency": "Monthly",
            "columns": ["date", "co2"]
        },
        "sunspots.csv": {
            "name": "Sunspots",
            "description": "Monthly mean total sunspot numbers (1749-2023)",
            "frequency": "Monthly",
            "columns": ["date", "sunspots"]
        },
        "retail_sales.csv": {
            "name": "Retail Sales",
            "description": "Monthly retail sales in the US (1992-2023)",
            "frequency": "Monthly",
            "columns": ["date", "sales"]
        },
        "temperature.csv": {
            "name": "Temperature",
            "description": "Global average temperature anomalies (1880-2023)",
            "frequency": "Monthly",
            "columns": ["date", "temperature"]
        },
        "stock_aapl.csv": {
            "name": "Stock Price - AAPL",
            "description": "Apple Inc. (AAPL) daily closing stock prices (2010-2023)",
            "frequency": "Daily",
            "columns": ["date", "close"]
        },
        "electricity.csv": {
            "name": "Electricity Consumption",
            "description": "Monthly electricity consumption in a region (2000-2023)",
            "frequency": "Monthly",
            "columns": ["date", "consumption"]
        },
        "gdp_growth.csv": {
            "name": "GDP Growth",
            "description": "Quarterly GDP growth rate (1960-2023)",
            "frequency": "Quarterly",
            "columns": ["date", "gdp_growth"]
        },
    }
    
    for csv_file in samples_dir.glob("*.csv"):
        if csv_file.name in sample_info:
            info = sample_info[csv_file.name]
            # Count rows
            try:
                import pandas as pd
                df = pd.read_csv(csv_file)
                rows = len(df)
            except:
                rows = 0
            
            samples.append(SampleDatasetInfo(
                filename=csv_file.name,
                name=info["name"],
                description=info["description"],
                frequency=info["frequency"],
                rows=rows,
                columns=info["columns"]
            ))
    
    return samples


@router.post("/samples/load", response_model=DatasetUploadResponse)
async def load_sample_dataset(
    request: LoadSampleRequest,
    db: Session = Depends(get_db)
):
    """
    Load a sample dataset into the system
    """
    samples_dir = Path(settings.SAMPLES_DIR)
    file_path = samples_dir / request.filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Sample dataset '{request.filename}' not found"
        )
    
    try:
        # Parse file
        df, metadata = DataImportService.parse_file(str(file_path))
        
        # Validate dataframe
        validation = DataImportService.validate_dataframe(df)
        
        # Create dataset record
        dataset = Dataset(
            name=f"Sample: {request.filename.replace('.csv', '').replace('_', ' ').title()}",
            filename=request.filename,
            columns=metadata["columns"],
            row_count=metadata["row_count"],
            file_path=str(file_path),
            meta_data={**metadata, "is_sample": True},
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        return DatasetUploadResponse(
            dataset=DatasetResponse.model_validate(dataset),
            validation=validation,
            message=f"Sample dataset '{request.filename}' loaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a dataset file
    
    Supports CSV, TXT, XLS, XLSX formats
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.csv', '.txt', '.xls', '.xlsx']:
        raise HTTPException(
            status_code=400,
            detail=f"File format {file_ext} not supported. Supported formats: CSV, TXT, XLS, XLSX"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Save uploaded file
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Parse file
        df, metadata = DataImportService.parse_file(str(file_path))
        
        # Validate dataframe
        validation = DataImportService.validate_dataframe(df)
        
        # Create dataset record
        dataset = Dataset(
            name=metadata["filename"],
            filename=metadata["filename"],
            columns=metadata["columns"],
            row_count=metadata["row_count"],
            file_path=str(file_path),
            meta_data=metadata,  # Use meta_data (metadata is reserved by SQLAlchemy)
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        return DatasetUploadResponse(
            dataset=DatasetResponse.model_validate(dataset),
            validation=validation,
            message="Dataset uploaded successfully"
        )
        
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    """List all datasets"""
    datasets = db.query(Dataset).all()
    return [DatasetResponse.model_validate(ds) for ds in datasets]


@router.get("/{dataset_id}/data")
async def get_dataset_data(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the raw data from a dataset file
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not dataset.file_path or not Path(dataset.file_path).exists():
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    try:
        with open(dataset.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading dataset file: {str(e)}")


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get a specific dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DatasetResponse.model_validate(dataset)


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Delete a dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Delete file if it exists
    if dataset.file_path and os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    
    db.delete(dataset)
    db.commit()
    
    return {"message": "Dataset deleted successfully"}

