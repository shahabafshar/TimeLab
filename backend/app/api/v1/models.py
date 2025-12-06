"""
Model API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

from app.core.database import get_db
from app.models.model import Model, ModelMetrics
from app.schemas.model import (
    ModelCreate,
    ModelResponse,
    TrainModelRequest,
    GridSearchRequest,
    PredictionRequest,
    ForecastRequest
)
from app.services.modeling.training_service import TrainingService
from app.services.modeling.grid_search_service import GridSearchService
from app.services.evaluation.prediction_service import PredictionService
from app.services.forecasting.forecast_service import ForecastService
from app.services.forecasting.code_generator import CodeGenerator
from app.tasks.model_tasks import grid_search_task

router = APIRouter(prefix="/models", tags=["models"])


@router.post("/train", response_model=ModelResponse)
async def train_model(
    request: TrainModelRequest,
    db: Session = Depends(get_db)
):
    """Train a SARIMAX model"""
    try:
        timeseries = None
        
        # Option 1: Load from dataset (preferred)
        if request.dataset_id and request.date_column and request.target_column:
            from app.models.dataset import Dataset
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
        
        # Prepare exogenous variables if provided
        exog = None
        if request.exog_variables:
            exog = pd.DataFrame(request.exog_variables)
            exog.index = pd.to_datetime(timeseries.index[:len(exog)])
        
        # Determine model type
        model_type = request.model_type or "SARIMAX"
        
        # Prepare parameters based on model type
        if model_type.upper() == "ARTFIMA":
            if not request.artfima_parameters:
                raise HTTPException(
                    status_code=400,
                    detail="artfima_parameters required when model_type is ARTFIMA"
                )
            artfima_params = request.artfima_parameters
            parameters = {
                "p": artfima_params.p,
                "d": artfima_params.d,
                "q": artfima_params.q,
                "glp": artfima_params.glp,
                "lambda": artfima_params.lambda_param,
                "fixd": artfima_params.fixd,
                "likAlg": "exact",
            }
        else:
            params = request.parameters
            parameters = {
                "p": params.p,
                "d": params.d,
                "q": params.q,
                "P": params.P,
                "D": params.D,
                "Q": params.Q,
                "s": params.s,
            }
        
        # Train model using factory method
        try:
            result = TrainingService.train_model(
                Y=timeseries,
                model_type=model_type,
                parameters=parameters,
                exog_variables=exog if model_type.upper() == "SARIMAX" else None,
                quiet=True
            )
        except ValueError as e:
            # Provide clear error messages for validation errors
            raise HTTPException(
                status_code=400,
                detail=f"Model training validation error: {str(e)}"
            )
        except Exception as e:
            # Log the full error for debugging
            import traceback
            error_detail = str(e)
            print(f"Model training error: {error_detail}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Model training failed: {error_detail}"
            )
        
        # Save model to database
        if model_type.upper() == "ARTFIMA":
            artfima_params = request.artfima_parameters
            # Use ESTIMATED parameters from result, not input parameters
            estimated_params = result.get("parameters", {})
            estimated_d = estimated_params.get("d", artfima_params.d)
            estimated_lambda = estimated_params.get("lambda", artfima_params.lambda_param)

            model = Model(
                name=f"{artfima_params.glp}({artfima_params.p},{estimated_d:.3f},{artfima_params.q})",
                type=artfima_params.glp,
                parameters={
                    "p": artfima_params.p,
                    "d": estimated_d,  # Use ESTIMATED d
                    "q": artfima_params.q,
                    "glp": artfima_params.glp,
                    "lambda": estimated_lambda,  # Use ESTIMATED lambda
                },
                model_data=result["model_data"],
                summary=result["summary"],
            )
        else:
            params = request.parameters
            model = Model(
                name=f"SARIMAX({params.p},{params.d},{params.q})x({params.P},{params.D},{params.Q},{params.s})",
                type="SARIMAX",
                parameters={
                    "p": params.p,
                    "d": params.d,
                    "q": params.q,
                    "P": params.P,
                    "D": params.D,
                    "Q": params.Q,
                    "s": params.s,
                },
                model_data=result["model_data"],
                summary=result["summary"],
            )
        
        db.add(model)
        db.commit()
        db.refresh(model)
        
        # Save metrics
        metrics = ModelMetrics(
            model_id=model.id,
            aic=result["metrics"]["aic"],
            bic=result["metrics"]["bic"],
            hqic=result["metrics"]["hqic"],
        )
        db.add(metrics)
        db.commit()
        
        return ModelResponse(
            id=model.id,
            name=model.name,
            type=model.type,
            parameters=model.parameters,
            metrics={
                "aic": metrics.aic,
                "bic": metrics.bic,
                "hqic": metrics.hqic,
            },
            created_at=model.created_at.isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/grid-search")
async def start_grid_search(request: GridSearchRequest):
    """Start async grid search"""
    try:
        # Start Celery task
        task = grid_search_task.delay(
            request.timeseries_data,
            request.p_range,
            request.q_range,
            request.P_range,
            request.Q_range,
            request.d,
            request.D,
            request.s,
            request.exog_variables,
        )
        
        return {
            "task_id": task.id,
            "status": "started",
            "message": "Grid search started. Use task_id to check status.",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: str, db: Session = Depends(get_db)):
    """Get model details"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    metrics = None
    if model.metrics:
        metrics = {
            "aic": model.metrics.aic,
            "bic": model.metrics.bic,
            "hqic": model.metrics.hqic,
            "rmse": model.metrics.rmse,
            "mae": model.metrics.mae,
            "mape": model.metrics.mape,
        }
    
    return ModelResponse(
        id=model.id,
        name=model.name,
        type=model.type,
        parameters=model.parameters,
        metrics=metrics,
        created_at=model.created_at.isoformat(),
    )


@router.post("/{model_id}/predict")
async def predict(
    model_id: str,
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """Generate predictions"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        # Deserialize model
        fitted_model = TrainingService.deserialize_model(model.model_data)
        
        # Convert data
        timeseries = pd.Series(request.timeseries_data)
        timeseries.index = pd.to_datetime(timeseries.index)
        
        # Get transformation function
        transform_func = (
            np.log1p if request.transformation_type == "log" else lambda x: x
        )
        inverse_func = (
            np.expm1 if request.transformation_type == "log" else lambda x: x
        )
        
        # Generate predictions
        result = PredictionService.predict_set(
            timeseries,
            "value",
            request.seasonality,
            inverse_func,
            fitted_model,
            forecast=request.forecast
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{model_id}/forecast")
async def forecast(
    model_id: str,
    request: ForecastRequest,
    db: Session = Depends(get_db)
):
    """Generate forecasts"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        # Deserialize model
        fitted_model = TrainingService.deserialize_model(model.model_data)
        
        # Get transformation function based on transformation type
        # Pass transformation type as string instead of function for better reliability
        transformation_type = request.transformation_type.lower() if request.transformation_type else "none"
        
        # Generate forecasts
        result = ForecastService.generate_forecast(
            fitted_model,
            request.periods,
            transformation_type=transformation_type,
            last_date=request.last_date,
            frequency=request.frequency
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        # Log full traceback for debugging
        print(f"Forecast error: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=error_detail)


@router.get("/{model_id}/code")
def get_code(model_id: str, db: Session = Depends(get_db)):
    """Get generated code for model"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Generate code (simplified - would need more context)
    code = CodeGenerator.generate_code(
        filename="dataset.csv",
        ds_column="date",
        y="value",
        test_stationarity_code="# Stationarity test code",
        test_set_size=12,
        seasonality=model.parameters.get("s", 12),
        p=model.parameters["p"],
        d=model.parameters["d"],
        q=model.parameters["q"],
        P=model.parameters["P"],
        D=model.parameters["D"],
        Q=model.parameters["Q"],
        s=model.parameters["s"],
    )
    
    return {"code": code}

