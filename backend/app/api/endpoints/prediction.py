"""
Prediction endpoints for supply forecasting.
"""
from fastapi import APIRouter, HTTPException
from ...models.prediction import PredictionRequest, PredictionResponse
from ...services.prediction import PredictionService

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_supply(request: PredictionRequest):
    """
    Predict future token supply using various models.
    
    This endpoint accepts historical supply data and returns predictions using the specified model.
    Supported models are:
    - Prophet (Facebook's time series forecasting tool)
    - ARIMA (Classical statistical forecasting)
    - LSTM (Deep learning based forecasting)
    
    The response includes predictions with confidence intervals and model performance metrics.
    
    Example request:
    ```json
    {
        "historical_data": [
            {
                "date": "2023-01-01T00:00:00Z",
                "value": 1000000
            },
            {
                "date": "2023-02-01T00:00:00Z",
                "value": 1100000
            }
        ],
        "forecast_years": 5,
        "model_type": "prophet",
        "confidence_interval": 0.95
    }
    ```
    
    Returns:
    ```json
    {
        "forecast": [
            {
                "date": "2023-03-01T00:00:00Z",
                "value": 1200000,
                "lower_bound": 1150000,
                "upper_bound": 1250000
            }
        ],
        "model_type": "prophet",
        "model_params": {
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 10.0,
            "seasonality_mode": "multiplicative"
        },
        "metrics": {
            "mae": 1000.0,
            "rmse": 1200.0
        }
    }
    ```
    """
    try:
        predictions, model_params, metrics = PredictionService.predict(
            data=request.historical_data,
            model_type=request.model_type,
            forecast_years=request.forecast_years,
            confidence_interval=request.confidence_interval
        )
        
        return PredictionResponse(
            forecast=predictions,
            model_type=request.model_type,
            model_params=model_params,
            metrics=metrics
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        ) 