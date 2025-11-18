"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import datasets, preprocessing, analysis, models, projects

app = FastAPI(
    title="TimeLab API",
    description="Time series forecasting and analysis API",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(datasets.router, prefix=settings.API_V1_STR)
app.include_router(preprocessing.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(models.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "TimeLab API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
