"""
Configuration management for Monsoon Crop Predictor
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


class Config:
    """Configuration class for the Monsoon Crop Predictor package"""

    def __init__(self, confidence_threshold=0.7, **kwargs):
        """Initialize configuration with optional parameters"""
        self.confidence_threshold = confidence_threshold
        for key, value in kwargs.items():
            setattr(self, key, value)

    # Package root directory
    PACKAGE_ROOT = Path(__file__).parent.parent

    # Model paths
    MODELS_DIR = PACKAGE_ROOT / "models" / "best_advanced_models"

    # Supported crops
    SUPPORTED_CROPS = ["RICE", "WHEAT", "MAIZE"]

    # Target column mappings
    TARGET_COLUMNS = {
        "RICE": "RICE YIELD (Kg per ha)",
        "WHEAT": "WHEAT YIELD (Kg per ha)",
        "MAIZE": "MAIZE YIELD (Kg per ha)",
    }

    # Model file mappings
    MODEL_FILES = {
        "RICE": "rice_best_advanced_ensemble.pkl",
        "WHEAT": "wheat_best_advanced_ensemble.pkl",
        "MAIZE": "maize_best_advanced_ensemble.pkl",
    }

    # Feature groups for different analyses
    RAINFALL_FEATURES = [
        "Annual",
        "Jan-Feb",
        "Mar-May",
        "Jun-Sep",
        "Oct-Dec",
        "Seasonal_Variability",
        "Monsoon_Intensity",
        "Pre_Monsoon_Ratio",
        "Post_Monsoon_Ratio",
        "Monsoon_Concentration",
    ]

    TEMPORAL_FEATURES = [
        "Year",
        "Rainfall_Trend",
        "Rainfall_Lag_1",
        "Rainfall_Lag_2",
        "Yield_Trend",
        "Cycle_Component",
    ]

    # Data validation rules
    VALIDATION_RULES = {
        "min_year": 2000,
        "max_year": 2030,
        "min_rainfall": 0,
        "max_rainfall": 5000,
        "required_columns": ["Year", "Annual", "State Name", "Dist Name"],
    }

    # API configuration
    API_CONFIG = {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": False,
        "workers": 4,
        "timeout": 30,
    }

    # Logging configuration
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
            "file": {
                "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.FileHandler",
                "filename": "monsoon_crop_predictor.log",
                "mode": "a",
            },
        },
        "loggers": {
            "": {"handlers": ["default", "file"], "level": "INFO", "propagate": False}
        },
    }

    @classmethod
    def get_model_path(cls, crop: str) -> Path:
        """Get the path to the model file for a specific crop"""
        if crop.upper() not in cls.SUPPORTED_CROPS:
            raise ValueError(f"Unsupported crop: {crop}")

        model_file = cls.MODEL_FILES[crop.upper()]
        return cls.MODELS_DIR / model_file

    @classmethod
    def get_target_column(cls, crop: str) -> str:
        """Get the target column name for a specific crop"""
        if crop.upper() not in cls.SUPPORTED_CROPS:
            raise ValueError(f"Unsupported crop: {crop}")

        return cls.TARGET_COLUMNS[crop.upper()]

    @classmethod
    def validate_crop(cls, crop: str) -> str:
        """Validate and normalize crop name"""
        crop_upper = crop.upper()
        if crop_upper not in cls.SUPPORTED_CROPS:
            raise ValueError(
                f"Unsupported crop: {crop}. Supported crops: {cls.SUPPORTED_CROPS}"
            )
        return crop_upper

    @classmethod
    def load_custom_config(cls, config_path: str) -> Dict[str, Any]:
        """Load custom configuration from JSON file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, "r") as f:
            return json.load(f)

    @classmethod
    def get_feature_columns(
        cls, include_rainfall: bool = True, include_temporal: bool = True
    ) -> List[str]:
        """Get list of feature columns based on requirements"""
        features = []

        if include_rainfall:
            features.extend(cls.RAINFALL_FEATURES)

        if include_temporal:
            features.extend(cls.TEMPORAL_FEATURES)

        return features
