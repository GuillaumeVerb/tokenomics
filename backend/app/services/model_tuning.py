"""
Model tuning and optimization services.
"""
from typing import Dict, Any, List, Tuple
import optuna
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
import torch
import torch.nn as nn
from ..models.prediction import TimeSeriesPoint

class ModelTuner:
    """Automated model tuning using Optuna."""
    
    @staticmethod
    def tune_prophet(
        data: pd.DataFrame,
        n_trials: int = 50,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """Tune Prophet hyperparameters."""
        
        def objective(trial):
            params = {
                'changepoint_prior_scale': trial.suggest_loguniform('changepoint_prior_scale', 0.001, 0.5),
                'seasonality_prior_scale': trial.suggest_loguniform('seasonality_prior_scale', 0.01, 10),
                'seasonality_mode': trial.suggest_categorical('seasonality_mode', ['additive', 'multiplicative']),
                'changepoint_range': trial.suggest_uniform('changepoint_range', 0.8, 0.95)
            }
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            errors = []
            
            for train_idx, val_idx in tscv.split(data):
                train_df = data.iloc[train_idx]
                val_df = data.iloc[val_idx]
                
                model = Prophet(**params)
                model.fit(train_df)
                
                forecast = model.predict(val_df[['ds']])
                error = mean_squared_error(val_df['y'], forecast['yhat'], squared=False)
                errors.append(error)
            
            return np.mean(errors)
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials)
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': n_trials,
            'cv_folds': cv_folds
        }
    
    @staticmethod
    def tune_arima(
        data: pd.DataFrame,
        n_trials: int = 50,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """Tune ARIMA hyperparameters."""
        
        def objective(trial):
            params = {
                'p': trial.suggest_int('p', 0, 5),
                'd': trial.suggest_int('d', 0, 2),
                'q': trial.suggest_int('q', 0, 5)
            }
            
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            errors = []
            
            for train_idx, val_idx in tscv.split(data):
                try:
                    train_data = data.iloc[train_idx]['y']
                    val_data = data.iloc[val_idx]['y']
                    
                    model = ARIMA(train_data, order=(params['p'], params['d'], params['q']))
                    results = model.fit()
                    
                    forecast = results.forecast(steps=len(val_data))
                    error = mean_squared_error(val_data, forecast, squared=False)
                    errors.append(error)
                except:
                    return float('inf')
            
            return np.mean(errors)
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials)
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': n_trials,
            'cv_folds': cv_folds
        }
    
    @staticmethod
    def tune_lstm(
        data: pd.DataFrame,
        n_trials: int = 50,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """Tune LSTM hyperparameters."""
        
        def objective(trial):
            params = {
                'hidden_size': trial.suggest_int('hidden_size', 10, 200),
                'num_layers': trial.suggest_int('num_layers', 1, 4),
                'dropout': trial.suggest_uniform('dropout', 0.0, 0.5),
                'learning_rate': trial.suggest_loguniform('learning_rate', 1e-4, 1e-2),
                'sequence_length': trial.suggest_int('sequence_length', 10, 60)
            }
            
            # Prepare sequences
            values = data['y'].values
            sequences = []
            targets = []
            
            for i in range(len(values) - params['sequence_length']):
                sequences.append(values[i:(i + params['sequence_length'])])
                targets.append(values[i + params['sequence_length']])
            
            sequences = torch.FloatTensor(sequences)
            targets = torch.FloatTensor(targets)
            
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            errors = []
            
            for train_idx, val_idx in tscv.split(sequences):
                try:
                    X_train = sequences[train_idx]
                    y_train = targets[train_idx]
                    X_val = sequences[val_idx]
                    y_val = targets[val_idx]
                    
                    model = nn.LSTM(
                        input_size=1,
                        hidden_size=params['hidden_size'],
                        num_layers=params['num_layers'],
                        dropout=params['dropout'],
                        batch_first=True
                    )
                    fc = nn.Linear(params['hidden_size'], 1)
                    optimizer = torch.optim.Adam([*model.parameters(), *fc.parameters()], 
                                              lr=params['learning_rate'])
                    criterion = nn.MSELoss()
                    
                    # Training
                    n_epochs = 50
                    for _ in range(n_epochs):
                        model.train()
                        optimizer.zero_grad()
                        
                        out, _ = model(X_train.unsqueeze(-1))
                        out = fc(out[:, -1, :])
                        loss = criterion(out.squeeze(), y_train)
                        
                        loss.backward()
                        optimizer.step()
                    
                    # Validation
                    model.eval()
                    with torch.no_grad():
                        out, _ = model(X_val.unsqueeze(-1))
                        out = fc(out[:, -1, :])
                        error = mean_squared_error(y_val, out.squeeze(), squared=False)
                        errors.append(error)
                except:
                    return float('inf')
            
            return np.mean(errors)
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials)
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': n_trials,
            'cv_folds': cv_folds
        }
    
    @classmethod
    def tune_model(
        cls,
        data: List[TimeSeriesPoint],
        model_type: str,
        n_trials: int = 50,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """Tune hyperparameters for the specified model."""
        df = pd.DataFrame([
            {"ds": point.date, "y": float(point.value)}
            for point in data
        ])
        
        if model_type == "prophet":
            return cls.tune_prophet(df, n_trials, cv_folds)
        elif model_type == "arima":
            return cls.tune_arima(df, n_trials, cv_folds)
        elif model_type == "lstm":
            return cls.tune_lstm(df, n_trials, cv_folds)
        else:
            raise ValueError(f"Unknown model type: {model_type}") 