"""
Custom exceptions for Monsoon Crop Predictor
"""


class PredictionError(Exception):
    """Raised when prediction fails"""

    pass


class DataValidationError(Exception):
    """Raised when data validation fails"""

    pass


class ModelLoadError(Exception):
    """Raised when model loading fails"""

    pass


class UnsupportedCropError(Exception):
    """Raised when an unsupported crop is specified"""

    pass


class InsufficientDataError(Exception):
    """Raised when insufficient data is provided for prediction"""

    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid"""

    pass


class FeatureEngineeringError(Exception):
    """Raised when feature engineering fails"""

    pass


class APIError(Exception):
    """Raised when API operations fail"""

    pass


class ValidationError(Exception):
    """Stub for ValidationError. Implement functionality as needed."""

    pass
