"""
Prediction service implementing various forecasting models.
"""
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
import torch
import torch.nn as nn
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_error, mean_squared_error
from ..models.prediction import TimeSeriesPoint, PredictionPoint

class LSTMPredictor(nn.Module):
    """LSTM model for time series prediction."""
    def __init__(self, input_size: int = 1, hidden_size: int = 50, num_layers: int = 2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class PredictionService:
    """Service for time series predictions using various models."""
    
    @staticmethod
    def prepare_data(data: List[TimeSeriesPoint]) -> pd.DataFrame:
        """Convert input data to pandas DataFrame."""
        df = pd.DataFrame([
            {"ds": point.date, "y": float(point.value)}
            for point in data
        ])
        return df
    
    @staticmethod
    def prophet_predict(
        data: pd.DataFrame,
        forecast_years: int,
        interval_width: float
    ) -> Tuple[List[PredictionPoint], Dict, Dict[str, float]]:
        """Make predictions using Prophet."""
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            interval_width=interval_width
        )
        model.fit(data)
        
        # Create future dates
        future = model.make_future_dataframe(
            periods=forecast_years * 365,
            freq='D'
        )
        forecast = model.predict(future)
        
        # Convert to response format
        predictions = [
            PredictionPoint(
                date=row.ds,
                value=row.yhat,
                lower_bound=row.yhat_lower,
                upper_bound=row.yhat_upper
            )
            for _, row in forecast.iloc[-forecast_years*365:].iterrows()
        ]
        
        # Calculate metrics
        metrics = {
            "mae": mean_absolute_error(data.y, forecast.yhat[:len(data)]),
            "rmse": np.sqrt(mean_squared_error(data.y, forecast.yhat[:len(data)]))
        }
        
        model_params = {
            "changepoint_prior_scale": model.changepoint_prior_scale,
            "seasonality_prior_scale": model.seasonality_prior_scale,
            "seasonality_mode": model.seasonality_mode
        }
        
        return predictions, model_params, metrics
    
    @staticmethod
    def arima_predict(
        data: pd.DataFrame,
        forecast_years: int,
        confidence: float
    ) -> Tuple[List[PredictionPoint], Dict, Dict[str, float]]:
        """Make predictions using ARIMA."""
        # Fit ARIMA model
        model = ARIMA(data.y, order=(1, 1, 1))
        results = model.fit()
        
        # Generate forecast
        forecast = results.get_forecast(
            steps=forecast_years * 365,
            alpha=1-confidence
        )
        
        # Create date range for predictions
        last_date = data.ds.iloc[-1]
        dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=forecast_years * 365,
            freq='D'
        )
        
        # Convert to response format
        predictions = [
            PredictionPoint(
                date=date,
                value=mean,
                lower_bound=lower,
                upper_bound=upper
            )
            for date, mean, lower, upper in zip(
                dates,
                forecast.predicted_mean,
                forecast.conf_int()[:, 0],
                forecast.conf_int()[:, 1]
            )
        ]
        
        # Calculate metrics
        fitted_values = results.get_prediction(start=0).predicted_mean
        metrics = {
            "mae": mean_absolute_error(data.y, fitted_values),
            "rmse": np.sqrt(mean_squared_error(data.y, fitted_values)),
            "aic": results.aic
        }
        
        model_params = {
            "order": results.model.order,
            "method": results.model.method
        }
        
        return predictions, model_params, metrics
    
    @staticmethod
    def lstm_predict(
        data: pd.DataFrame,
        forecast_years: int,
        confidence: float
    ) -> Tuple[List[PredictionPoint], Dict, Dict[str, float]]:
        """Make predictions using LSTM."""
        # Prepare data
        values = data.y.values.reshape(-1, 1)
        
        # Normalize data
        mean = values.mean()
        std = values.std()
        values = (values - mean) / std
        
        # Create sequences
        def create_sequences(data: np.ndarray, seq_length: int = 30):
            xs, ys = [], []
            for i in range(len(data) - seq_length):
                xs.append(data[i:(i + seq_length)])
                ys.append(data[i + seq_length])
            return np.array(xs), np.array(ys)
        
        X, y = create_sequences(values)
        X = torch.FloatTensor(X)
        y = torch.FloatTensor(y)
        
        # Train LSTM
        model = LSTMPredictor()
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters())
        
        n_epochs = 100
        for epoch in range(n_epochs):
            model.train()
            optimizer.zero_grad()
            y_pred = model(X)
            loss = criterion(y_pred, y)
            loss.backward()
            optimizer.step()
        
        # Generate predictions
        model.eval()
        predictions = []
        last_sequence = values[-30:].reshape(1, 30, 1)
        last_sequence = torch.FloatTensor(last_sequence)
        
        for _ in range(forecast_years * 365):
            with torch.no_grad():
                pred = model(last_sequence)
                last_sequence = torch.cat([
                    last_sequence[:, 1:, :],
                    pred.reshape(1, 1, 1)
                ], dim=1)
                
                # Denormalize
                value = float(pred * std + mean)
                # Simple uncertainty estimation
                std_dev = std * np.sqrt(loss.item())
                z_score = -torch.distributions.Normal(0, 1).icdf(torch.tensor((1-confidence)/2))
                
                predictions.append(PredictionPoint(
                    date=data.ds.iloc[-1] + timedelta(days=len(predictions) + 1),
                    value=value,
                    lower_bound=value - z_score * std_dev,
                    upper_bound=value + z_score * std_dev
                ))
        
        # Calculate metrics
        model.eval()
        with torch.no_grad():
            train_pred = model(X)
            train_pred = train_pred.numpy() * std + mean
            train_true = y.numpy() * std + mean
            
        metrics = {
            "mae": mean_absolute_error(train_true, train_pred),
            "rmse": np.sqrt(mean_squared_error(train_true, train_pred))
        }
        
        model_params = {
            "hidden_size": model.hidden_size,
            "num_layers": model.num_layers,
            "sequence_length": 30,
            "epochs": n_epochs
        }
        
        return predictions, model_params, metrics
    
    @classmethod
    def predict(
        cls,
        data: List[TimeSeriesPoint],
        model_type: str,
        forecast_years: int,
        confidence_interval: float
    ) -> Tuple[List[PredictionPoint], Dict, Dict[str, float]]:
        """Make predictions using the specified model."""
        df = cls.prepare_data(data)
        
        if model_type == "prophet":
            return cls.prophet_predict(df, forecast_years, confidence_interval)
        elif model_type == "arima":
            return cls.arima_predict(df, forecast_years, confidence_interval)
        elif model_type == "lstm":
            return cls.lstm_predict(df, forecast_years, confidence_interval)
        else:
            raise ValueError(f"Unknown model type: {model_type}") 