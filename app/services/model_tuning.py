"""Model tuning and optimization services."""

import logging
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

logger = logging.getLogger(__name__)

class ModelOptimizationError(Exception):
    """Custom exception for model optimization errors."""
    pass

def optimize_hyperparameters(model, param_grid, X_train, y_train, cv=5):
    """
    Optimize model hyperparameters using grid search cross-validation.
    
    Args:
        model: The model to optimize
        param_grid: Dictionary with parameters names (string) as keys and lists of parameter settings to try
        X_train: Training data features
        y_train: Training data target
        cv: Number of cross-validation folds (default: 5)
        
    Returns:
        Tuple of (best_params, best_score)
    """
    try:
        grid_search = GridSearchCV(model, param_grid, cv=cv, scoring='neg_mean_squared_error')
        grid_search.fit(X_train, y_train)
        return grid_search.best_params_, abs(grid_search.best_score_)
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error(f"Error during hyperparameter optimization: {str(e)}")
        raise ModelOptimizationError(f"Failed to optimize hyperparameters: {str(e)}")

def evaluate_model_performance(model, X_test, y_test):
    """
    Evaluate model performance using multiple metrics.
    
    Args:
        model: Trained model
        X_test: Test data features
        y_test: Test data target
        
    Returns:
        Dictionary containing various performance metrics
    """
    try:
        y_pred = model.predict(X_test)
        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
        return metrics
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error(f"Error during model evaluation: {str(e)}")
        raise ModelOptimizationError(f"Failed to evaluate model: {str(e)}")

def train_model(model, X_train, y_train):
    """Train a model with the given training data."""
    try:
        model.fit(X_train, y_train)
        return model
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error(f"Error during model training: {str(e)}")
        raise ModelOptimizationError(f"Failed to train model: {str(e)}")

def save_model(model, model_path):
    """Save the trained model to disk."""
    try:
        joblib.dump(model, model_path)
    except (IOError, ValueError, TypeError) as e:
        logger.error(f"Error saving model to {model_path}: {str(e)}")
        raise ModelOptimizationError(f"Failed to save model: {str(e)}") 