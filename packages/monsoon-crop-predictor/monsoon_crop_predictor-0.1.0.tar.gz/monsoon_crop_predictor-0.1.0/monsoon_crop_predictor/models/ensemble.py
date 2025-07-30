"""
Ensemble model utilities for Monsoon Crop Predictor
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from sklearn.ensemble import VotingRegressor, StackingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
import pickle
from pathlib import Path

from ..utils.config import Config
from ..utils.exceptions import ModelLoadError, PredictionError
from ..utils.logger import LoggerMixin


class EnsembleManager:
    """Stub for EnsembleManager. Implement functionality as needed."""

    def load_models(self, crop_type):
        """Stub method for loading models."""
        return []


class EnsemblePredictor(LoggerMixin):
    """
    Advanced ensemble methods for crop yield prediction
    """

    def __init__(self):
        """Initialize EnsemblePredictor"""
        self.config = Config()
        self.base_models = {}
        self.ensemble_models = {}
        self.model_weights = {}
        self.logger.info("EnsemblePredictor initialized")

    def create_voting_ensemble(
        self,
        models: Dict[str, Any],
        X_train: pd.DataFrame,
        y_train: pd.Series,
        voting: str = "soft",
        weights: Optional[List[float]] = None,
    ) -> VotingRegressor:
        """
        Create a voting ensemble from multiple models

        Args:
            models: Dictionary of model name -> model object
            X_train: Training features
            y_train: Training targets
            voting: Voting method ('soft' for weighted average)
            weights: Optional weights for each model

        Returns:
            Fitted VotingRegressor
        """
        self.logger.info(f"Creating voting ensemble with {len(models)} models")

        # Prepare estimators list
        estimators = [(name, model) for name, model in models.items()]

        # Create voting regressor
        ensemble = VotingRegressor(estimators=estimators, weights=weights)

        # Fit ensemble
        ensemble.fit(X_train, y_train)

        self.logger.info("Voting ensemble created and fitted")
        return ensemble

    def create_stacking_ensemble(
        self,
        models: Dict[str, Any],
        X_train: pd.DataFrame,
        y_train: pd.Series,
        meta_learner: Optional[Any] = None,
        cv: int = 5,
    ) -> StackingRegressor:
        """
        Create a stacking ensemble with meta-learner

        Args:
            models: Dictionary of base models
            X_train: Training features
            y_train: Training targets
            meta_learner: Meta-learner model (default: LinearRegression)
            cv: Cross-validation folds for stacking

        Returns:
            Fitted StackingRegressor
        """
        self.logger.info(f"Creating stacking ensemble with {len(models)} base models")

        if meta_learner is None:
            meta_learner = LinearRegression()

        # Prepare estimators
        estimators = [(name, model) for name, model in models.items()]

        # Create stacking regressor
        ensemble = StackingRegressor(
            estimators=estimators, final_estimator=meta_learner, cv=cv, n_jobs=-1
        )

        # Fit ensemble
        ensemble.fit(X_train, y_train)

        self.logger.info("Stacking ensemble created and fitted")
        return ensemble

    def calculate_dynamic_weights(
        self,
        models: Dict[str, Any],
        X_val: pd.DataFrame,
        y_val: pd.Series,
        metric: str = "rmse",
    ) -> Dict[str, float]:
        """
        Calculate dynamic weights for ensemble based on validation performance

        Args:
            models: Dictionary of trained models
            X_val: Validation features
            y_val: Validation targets
            metric: Metric for weight calculation ('rmse', 'mae', 'r2')

        Returns:
            Dictionary of model weights
        """
        self.logger.info("Calculating dynamic weights based on validation performance")

        model_scores = {}

        # Calculate scores for each model
        for name, model in models.items():
            try:
                predictions = model.predict(X_val)

                if metric == "rmse":
                    score = np.sqrt(np.mean((y_val - predictions) ** 2))
                    # Lower RMSE is better, so invert for weighting
                    model_scores[name] = 1.0 / (1.0 + score)
                elif metric == "mae":
                    score = np.mean(np.abs(y_val - predictions))
                    model_scores[name] = 1.0 / (1.0 + score)
                elif metric == "r2":
                    from sklearn.metrics import r2_score

                    score = r2_score(y_val, predictions)
                    # Higher R2 is better
                    model_scores[name] = max(0, score)

            except Exception as e:
                self.logger.warning(f"Could not calculate score for {name}: {str(e)}")
                model_scores[name] = 0.1  # Small default weight

        # Normalize weights to sum to 1
        total_score = sum(model_scores.values())
        if total_score > 0:
            weights = {
                name: score / total_score for name, score in model_scores.items()
            }
        else:
            # Equal weights if all models failed
            weights = {name: 1.0 / len(models) for name in models.keys()}

        self.logger.info(f"Dynamic weights calculated: {weights}")
        return weights

    def adaptive_ensemble_predict(
        self,
        models: Dict[str, Any],
        X: pd.DataFrame,
        weights: Optional[Dict[str, float]] = None,
        uncertainty_estimation: bool = False,
    ) -> Union[np.ndarray, tuple]:
        """
        Make predictions using adaptive ensemble approach

        Args:
            models: Dictionary of trained models
            X: Features for prediction
            weights: Optional model weights
            uncertainty_estimation: Whether to return prediction uncertainty

        Returns:
            Predictions array, optionally with uncertainty estimates
        """
        self.logger.info("Making adaptive ensemble predictions")

        if weights is None:
            weights = {name: 1.0 / len(models) for name in models.keys()}

        all_predictions = []
        valid_weights = []

        # Get predictions from each model
        for name, model in models.items():
            try:
                predictions = model.predict(X)
                all_predictions.append(predictions)
                valid_weights.append(weights.get(name, 0))
            except Exception as e:
                self.logger.warning(f"Model {name} failed to predict: {str(e)}")

        if not all_predictions:
            raise PredictionError("No models could make predictions")

        # Convert to numpy arrays
        all_predictions = np.array(all_predictions)
        valid_weights = np.array(valid_weights)

        # Normalize weights
        if valid_weights.sum() > 0:
            valid_weights = valid_weights / valid_weights.sum()
        else:
            valid_weights = np.ones(len(all_predictions)) / len(all_predictions)

        # Weighted ensemble prediction
        ensemble_predictions = np.average(
            all_predictions, axis=0, weights=valid_weights
        )

        if uncertainty_estimation:
            # Calculate prediction uncertainty as weighted standard deviation
            prediction_std = np.sqrt(
                np.average(
                    (all_predictions - ensemble_predictions) ** 2,
                    axis=0,
                    weights=valid_weights,
                )
            )
            return ensemble_predictions, prediction_std

        return ensemble_predictions

    def cross_validation_ensemble(
        self, models: Dict[str, Any], X: pd.DataFrame, y: pd.Series, cv: int = 5
    ) -> Dict[str, Any]:
        """
        Evaluate ensemble using cross-validation

        Args:
            models: Dictionary of models to evaluate
            X: Features
            y: Targets
            cv: Number of cross-validation folds

        Returns:
            Dictionary containing CV results
        """
        self.logger.info("Running cross-validation ensemble evaluation")

        cv_results = {}

        # Evaluate individual models
        for name, model in models.items():
            try:
                scores = cross_val_score(
                    model, X, y, cv=cv, scoring="neg_mean_squared_error", n_jobs=-1
                )
                cv_results[name] = {
                    "rmse_mean": np.sqrt(-scores.mean()),
                    "rmse_std": np.sqrt(scores.std()),
                    "scores": scores.tolist(),
                }
            except Exception as e:
                self.logger.warning(f"CV failed for {name}: {str(e)}")
                cv_results[name] = {
                    "rmse_mean": float("inf"),
                    "rmse_std": float("inf"),
                    "scores": [],
                }

        # Create and evaluate voting ensemble
        try:
            voting_ensemble = VotingRegressor(
                [(name, model) for name, model in models.items()]
            )
            voting_scores = cross_val_score(
                voting_ensemble,
                X,
                y,
                cv=cv,
                scoring="neg_mean_squared_error",
                n_jobs=-1,
            )
            cv_results["VotingEnsemble"] = {
                "rmse_mean": np.sqrt(-voting_scores.mean()),
                "rmse_std": np.sqrt(voting_scores.std()),
                "scores": voting_scores.tolist(),
            }
        except Exception as e:
            self.logger.warning(f"Voting ensemble CV failed: {str(e)}")

        # Create and evaluate stacking ensemble
        try:
            stacking_ensemble = StackingRegressor(
                [(name, model) for name, model in models.items()],
                final_estimator=LinearRegression(),
                cv=3,  # Use fewer folds for inner CV
            )
            stacking_scores = cross_val_score(
                stacking_ensemble,
                X,
                y,
                cv=cv,
                scoring="neg_mean_squared_error",
                n_jobs=-1,
            )
            cv_results["StackingEnsemble"] = {
                "rmse_mean": np.sqrt(-stacking_scores.mean()),
                "rmse_std": np.sqrt(stacking_scores.std()),
                "scores": stacking_scores.tolist(),
            }
        except Exception as e:
            self.logger.warning(f"Stacking ensemble CV failed: {str(e)}")

        self.logger.info("Cross-validation ensemble evaluation completed")
        return cv_results

    def save_ensemble(
        self,
        ensemble_model: Any,
        model_path: Union[str, Path],
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Save ensemble model to disk

        Args:
            ensemble_model: Trained ensemble model
            model_path: Path to save the model
            metadata: Optional metadata to save with model
        """
        model_path = Path(model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            "model": ensemble_model,
            "type": "ensemble",
            "metadata": metadata or {},
        }

        try:
            with open(model_path, "wb") as f:
                pickle.dump(model_data, f)

            self.logger.info(f"Ensemble model saved to {model_path}")

        except Exception as e:
            raise ModelLoadError(f"Failed to save ensemble model: {str(e)}")

    def load_ensemble(self, model_path: Union[str, Path]) -> tuple:
        """
        Load ensemble model from disk

        Args:
            model_path: Path to the saved model

        Returns:
            Tuple of (model, metadata)
        """
        model_path = Path(model_path)

        if not model_path.exists():
            raise ModelLoadError(f"Model file not found: {model_path}")

        try:
            with open(model_path, "rb") as f:
                model_data = pickle.load(f)

            if isinstance(model_data, dict):
                model = model_data.get("model")
                metadata = model_data.get("metadata", {})
            else:
                model = model_data
                metadata = {}

            self.logger.info(f"Ensemble model loaded from {model_path}")
            return model, metadata

        except Exception as e:
            raise ModelLoadError(f"Failed to load ensemble model: {str(e)}")

    def optimize_ensemble_weights(
        self,
        models: Dict[str, Any],
        X_val: pd.DataFrame,
        y_val: pd.Series,
        method: str = "gradient_descent",
        iterations: int = 100,
    ) -> Dict[str, float]:
        """
        Optimize ensemble weights using specified method

        Args:
            models: Dictionary of trained models
            X_val: Validation features
            y_val: Validation targets
            method: Optimization method ('gradient_descent', 'grid_search')
            iterations: Number of optimization iterations

        Returns:
            Optimized weights dictionary
        """
        self.logger.info(f"Optimizing ensemble weights using {method}")

        if method == "gradient_descent":
            return self._optimize_weights_gd(models, X_val, y_val, iterations)
        elif method == "grid_search":
            return self._optimize_weights_grid(models, X_val, y_val)
        else:
            raise ValueError(f"Unsupported optimization method: {method}")

    def _optimize_weights_gd(
        self,
        models: Dict[str, Any],
        X_val: pd.DataFrame,
        y_val: pd.Series,
        iterations: int,
    ) -> Dict[str, float]:
        """Optimize weights using gradient descent"""
        # Get predictions from all models
        predictions = {}
        for name, model in models.items():
            try:
                predictions[name] = model.predict(X_val)
            except Exception as e:
                self.logger.warning(f"Model {name} failed: {str(e)}")

        if not predictions:
            raise PredictionError("No model predictions available for optimization")

        # Initialize weights
        n_models = len(predictions)
        weights = np.ones(n_models) / n_models
        learning_rate = 0.01

        model_names = list(predictions.keys())
        pred_matrix = np.column_stack([predictions[name] for name in model_names])

        # Gradient descent optimization
        for i in range(iterations):
            # Current ensemble prediction
            ensemble_pred = np.dot(pred_matrix, weights)

            # Calculate loss (MSE)
            loss = np.mean((y_val - ensemble_pred) ** 2)

            # Calculate gradients
            gradients = np.zeros(n_models)
            for j in range(n_models):
                gradients[j] = -2 * np.mean((y_val - ensemble_pred) * pred_matrix[:, j])

            # Update weights
            weights -= learning_rate * gradients

            # Project weights to simplex (sum to 1, non-negative)
            weights = np.maximum(weights, 0)
            if weights.sum() > 0:
                weights /= weights.sum()
            else:
                weights = np.ones(n_models) / n_models

        # Return as dictionary
        optimized_weights = {
            name: float(weights[i]) for i, name in enumerate(model_names)
        }

        self.logger.info(f"Optimized weights: {optimized_weights}")
        return optimized_weights

    def _optimize_weights_grid(
        self, models: Dict[str, Any], X_val: pd.DataFrame, y_val: pd.Series
    ) -> Dict[str, float]:
        """Optimize weights using grid search"""
        # Simplified grid search for up to 3 models
        model_names = list(models.keys())

        if len(model_names) > 3:
            # Use equal weights for too many models
            return {name: 1.0 / len(model_names) for name in model_names}

        # Get predictions
        predictions = {}
        for name, model in models.items():
            predictions[name] = model.predict(X_val)

        best_weights = None
        best_loss = float("inf")

        # Grid search over weight combinations
        if len(model_names) == 2:
            for w1 in np.arange(0, 1.1, 0.1):
                w2 = 1 - w1
                weights = [w1, w2]

                ensemble_pred = sum(
                    w * predictions[name] for w, name in zip(weights, model_names)
                )
                loss = np.mean((y_val - ensemble_pred) ** 2)

                if loss < best_loss:
                    best_loss = loss
                    best_weights = weights

        elif len(model_names) == 3:
            for w1 in np.arange(0, 1.1, 0.2):
                for w2 in np.arange(0, 1.1 - w1, 0.2):
                    w3 = 1 - w1 - w2
                    if w3 >= 0:
                        weights = [w1, w2, w3]

                        ensemble_pred = sum(
                            w * predictions[name]
                            for w, name in zip(weights, model_names)
                        )
                        loss = np.mean((y_val - ensemble_pred) ** 2)

                        if loss < best_loss:
                            best_loss = loss
                            best_weights = weights

        if best_weights is None:
            best_weights = [1.0 / len(model_names)] * len(model_names)

        return {name: float(weight) for name, weight in zip(model_names, best_weights)}
