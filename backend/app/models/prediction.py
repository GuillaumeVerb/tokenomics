"""
Time series prediction models for token supply forecasting.
"""
from typing import List, Dict, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class TimeSeriesPoint(BaseModel):
    """Data point for time series prediction."""
    date: datetime = Field(..., description="Date of the observation")
    value: Decimal = Field(..., gt=0, description="Token supply value")

class PredictionRequest(BaseModel):
    """Request model for time series prediction."""
    historical_data: List[TimeSeriesPoint] = Field(
        ..., 
        min_items=10,
        description="Historical data points (date, value)"
    )
    forecast_years: int = Field(
        5, 
        ge=1, 
        le=10,
        description="Number of years to forecast"
    )
    model_type: Literal["prophet", "arima", "lstm"] = Field(
        "prophet",
        description="Type of prediction model to use"
    )
    confidence_interval: float = Field(
        0.95,
        gt=0,
        lt=1,
        description="Confidence interval for predictions (0-1)"
    )

class PredictionPoint(BaseModel):
    """Predicted data point with confidence intervals."""
    date: datetime = Field(..., description="Forecasted date")
    value: float = Field(..., description="Predicted value (yhat)")
    lower_bound: float = Field(..., description="Lower bound of prediction interval")
    upper_bound: float = Field(..., description="Upper bound of prediction interval")

class PredictionResponse(BaseModel):
    """Response model for time series prediction."""
    forecast: List[PredictionPoint] = Field(..., description="Forecasted points")
    model_type: str = Field(..., description="Model used for prediction")
    model_params: Dict = Field(..., description="Model parameters used")
    metrics: Dict[str, float] = Field(..., description="Model performance metrics") 