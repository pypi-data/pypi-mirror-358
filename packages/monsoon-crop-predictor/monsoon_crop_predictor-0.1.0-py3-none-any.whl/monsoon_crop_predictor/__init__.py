"""
Monsoon Crop Predictor - Advanced ML-based Crop Yield Prediction System

A comprehensive package for predicting crop yields based on monsoon patterns,
rainfall data, and agricultural parameters using advanced machine learning models.
"""

__version__ = "0.1.0"
__author__ = "Subrat Dash"
__email__ = "subratdash2022@gmail.com"
__description__ = (
    "ML-based crop yield prediction system using monsoon and rainfall data"
)

from .core.predictor import CropYieldPredictor
from .core.data_loader import DataLoader
from .core.preprocessor import DataPreprocessor
from .core.feature_engineer import FeatureEngineer
from .utils.config import Config
from .utils.exceptions import PredictionError, DataValidationError


class CropPredictor:
    """Stub for CropPredictor. Implement functionality as needed."""

    def __init__(self, config=None):
        """Initialize CropPredictor with optional config"""
        self.config = config


__all__ = [
    "CropYieldPredictor",
    "DataLoader",
    "DataPreprocessor",
    "FeatureEngineer",
    "Config",
    "PredictionError",
    "DataValidationError",
    "CropPredictor",
]
