"""API package initialization"""

from .schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    MonsoonAnalysisRequest,
    MonsoonAnalysisResponse,
    CropRecommendationRequest,
    CropRecommendationResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    HistoricalDataRequest,
    HistoricalDataResponse,
    ErrorResponse,
    HealthCheckResponse,
)

# Note: endpoints and middleware imports require optional dependencies
# They will be available when FastAPI and related packages are installed

__all__ = [
    "PredictionRequest",
    "PredictionResponse",
    "BatchPredictionRequest",
    "BatchPredictionResponse",
    "MonsoonAnalysisRequest",
    "MonsoonAnalysisResponse",
    "CropRecommendationRequest",
    "CropRecommendationResponse",
    "RiskAssessmentRequest",
    "RiskAssessmentResponse",
    "HistoricalDataRequest",
    "HistoricalDataResponse",
    "ErrorResponse",
    "HealthCheckResponse",
]
