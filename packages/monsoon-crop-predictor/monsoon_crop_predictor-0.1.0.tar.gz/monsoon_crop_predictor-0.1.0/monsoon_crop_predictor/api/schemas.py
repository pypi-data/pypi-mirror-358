"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class PredictionRequest(BaseModel):
    """Schema for single prediction request"""

    crop: str = Field(..., description="Crop type (RICE, WHEAT, MAIZE)")
    annual_rainfall: float = Field(
        ..., alias="Annual", ge=0, le=5000, description="Annual rainfall in mm"
    )
    monsoon_rainfall: float = Field(
        ...,
        alias="Jun-Sep",
        ge=0,
        le=3000,
        description="Monsoon rainfall (Jun-Sep) in mm",
    )
    year: int = Field(..., ge=2000, le=2030, description="Year for prediction")

    pre_monsoon: Optional[float] = Field(
        None,
        alias="Jan-Feb",
        ge=0,
        le=1000,
        description="Pre-monsoon rainfall (Jan-Feb) in mm",
    )
    summer: Optional[float] = Field(
        None,
        alias="Mar-May",
        ge=0,
        le=1000,
        description="Summer rainfall (Mar-May) in mm",
    )
    post_monsoon: Optional[float] = Field(
        None,
        alias="Oct-Dec",
        ge=0,
        le=1000,
        description="Post-monsoon rainfall (Oct-Dec) in mm",
    )

    state_name: Optional[str] = Field(
        None, alias="State Name", description="State name"
    )
    district_name: Optional[str] = Field(
        None, alias="Dist Name", description="District name"
    )

    include_confidence: bool = Field(
        False, description="Include confidence intervals in response"
    )

    @validator("crop")
    def validate_crop(cls, v):
        allowed_crops = ["RICE", "WHEAT", "MAIZE"]
        if v.upper() not in allowed_crops:
            raise ValueError(f"Crop must be one of {allowed_crops}")
        return v.upper()

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "crop": "RICE",
                "Annual": 1200,
                "Jun-Sep": 800,
                "year": 2024,
                "Jan-Feb": 50,
                "Mar-May": 100,
                "Oct-Dec": 150,
                "State Name": "Punjab",
                "include_confidence": True,
            }
        }


class BatchPredictionRequest(BaseModel):
    """Schema for batch prediction request"""

    crop: str = Field(..., description="Crop type for all predictions")
    predictions: List[Dict[str, Any]] = Field(
        ..., description="List of prediction inputs"
    )
    include_confidence: bool = Field(False, description="Include confidence intervals")

    @validator("crop")
    def validate_crop(cls, v):
        allowed_crops = ["RICE", "WHEAT", "MAIZE"]
        if v.upper() not in allowed_crops:
            raise ValueError(f"Crop must be one of {allowed_crops}")
        return v.upper()


class PredictionResponse(BaseModel):
    """Schema for prediction response"""

    crop: str = Field(..., description="Crop type")
    predicted_yield: float = Field(..., description="Predicted yield in kg/ha")
    unit: str = Field("kg/ha", description="Unit of measurement")
    confidence_score: Optional[float] = Field(
        None, ge=0, le=1, description="Prediction confidence (0-1)"
    )
    confidence_interval: Optional[Dict[str, float]] = Field(
        None, description="Confidence interval bounds"
    )
    input_data: Dict[str, Any] = Field(
        ..., description="Input data used for prediction"
    )
    model_version: str = Field(..., description="Model version used")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Prediction timestamp"
    )


class BatchPredictionResponse(BaseModel):
    """Schema for batch prediction response"""

    crop: str = Field(..., description="Crop type")
    predictions: List[PredictionResponse] = Field(
        ..., description="List of prediction results"
    )
    summary: Dict[str, Any] = Field(..., description="Batch prediction summary")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Batch prediction timestamp"
    )


class MonsoonAnalysisRequest(BaseModel):
    """Schema for monsoon analysis request"""

    location: Optional[str] = Field(
        None, description="Location (state name) for analysis"
    )
    start_year: Optional[int] = Field(
        None, ge=1900, le=2030, description="Start year for analysis"
    )
    end_year: Optional[int] = Field(
        None, ge=1900, le=2030, description="End year for analysis"
    )
    analysis_type: str = Field(
        "comprehensive",
        description="Type of analysis (comprehensive, trends, patterns)",
    )

    @validator("end_year")
    def validate_year_range(cls, v, values):
        if (
            v is not None
            and "start_year" in values
            and values["start_year"] is not None
        ):
            if v <= values["start_year"]:
                raise ValueError("end_year must be greater than start_year")
        return v


class MonsoonAnalysisResponse(BaseModel):
    """Schema for monsoon analysis response"""

    period: Dict[str, int] = Field(..., description="Analysis period")
    location: Optional[str] = Field(None, description="Analysis location")
    rainfall_statistics: Dict[str, Dict[str, float]] = Field(
        ..., description="Rainfall statistics"
    )
    monsoon_patterns: Dict[str, Any] = Field(
        ..., description="Monsoon pattern analysis"
    )
    trends: Dict[str, Any] = Field(..., description="Rainfall trends")
    extreme_events: Dict[str, Any] = Field(..., description="Extreme weather events")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Analysis timestamp"
    )


class CropRecommendationRequest(BaseModel):
    """Schema for crop recommendation request"""

    annual_rainfall: float = Field(
        ..., alias="Annual", ge=0, le=5000, description="Annual rainfall in mm"
    )
    monsoon_rainfall: float = Field(
        ..., alias="Jun-Sep", ge=0, le=3000, description="Monsoon rainfall in mm"
    )
    year: int = Field(..., ge=2000, le=2030, description="Year for recommendation")

    pre_monsoon: Optional[float] = Field(
        None, alias="Jan-Feb", ge=0, le=1000, description="Pre-monsoon rainfall in mm"
    )
    summer: Optional[float] = Field(
        None, alias="Mar-May", ge=0, le=1000, description="Summer rainfall in mm"
    )
    post_monsoon: Optional[float] = Field(
        None, alias="Oct-Dec", ge=0, le=1000, description="Post-monsoon rainfall in mm"
    )

    state_name: Optional[str] = Field(
        None, alias="State Name", description="State name"
    )
    district_name: Optional[str] = Field(
        None, alias="Dist Name", description="District name"
    )

    crops_to_consider: Optional[List[str]] = Field(
        None, description="Specific crops to consider"
    )

    class Config:
        allow_population_by_field_name = True


class CropRecommendationResponse(BaseModel):
    """Schema for crop recommendation response"""

    recommended_crop: str = Field(..., description="Recommended crop")
    recommendation_confidence: float = Field(
        ..., ge=0, le=1, description="Recommendation confidence"
    )

    ranking: List[Dict[str, Any]] = Field(
        ..., description="Crop ranking with predicted yields"
    )
    predictions: Dict[str, PredictionResponse] = Field(
        ..., description="Detailed predictions for each crop"
    )
    input_conditions: Dict[str, Any] = Field(..., description="Input conditions used")

    timestamp: datetime = Field(
        default_factory=datetime.now, description="Recommendation timestamp"
    )


class RiskAssessmentRequest(BaseModel):
    """Schema for agricultural risk assessment request"""

    crop: str = Field(..., description="Crop type for risk assessment")
    annual_rainfall: float = Field(
        ..., alias="Annual", ge=0, le=5000, description="Annual rainfall in mm"
    )
    monsoon_rainfall: float = Field(
        ..., alias="Jun-Sep", ge=0, le=3000, description="Monsoon rainfall in mm"
    )
    year: int = Field(..., ge=2000, le=2030, description="Year for assessment")

    pre_monsoon: Optional[float] = Field(
        None, alias="Jan-Feb", ge=0, le=1000, description="Pre-monsoon rainfall in mm"
    )
    summer: Optional[float] = Field(
        None, alias="Mar-May", ge=0, le=1000, description="Summer rainfall in mm"
    )
    post_monsoon: Optional[float] = Field(
        None, alias="Oct-Dec", ge=0, le=1000, description="Post-monsoon rainfall in mm"
    )

    state_name: Optional[str] = Field(
        None, alias="State Name", description="State name"
    )
    district_name: Optional[str] = Field(
        None, alias="Dist Name", description="District name"
    )

    @validator("crop")
    def validate_crop(cls, v):
        allowed_crops = ["RICE", "WHEAT", "MAIZE"]
        if v.upper() not in allowed_crops:
            raise ValueError(f"Crop must be one of {allowed_crops}")
        return v.upper()

    class Config:
        allow_population_by_field_name = True


class RiskAssessmentResponse(BaseModel):
    """Schema for risk assessment response"""

    crop: str = Field(..., description="Assessed crop")
    predicted_yield: float = Field(..., description="Predicted yield in kg/ha")

    risk_factors: Dict[str, float] = Field(..., description="Individual risk factors")
    risk_level: str = Field(..., description="Overall risk level (Low/Medium/High)")
    recommendations: List[str] = Field(
        ..., description="Risk mitigation recommendations"
    )

    confidence: float = Field(..., ge=0, le=1, description="Assessment confidence")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Assessment timestamp"
    )


class HistoricalDataRequest(BaseModel):
    """Schema for historical data request"""

    data_type: str = Field(..., description="Type of data (rainfall, yield, combined)")
    location: Optional[str] = Field(None, description="Location filter")
    crop: Optional[str] = Field(None, description="Crop filter")
    start_year: Optional[int] = Field(None, ge=1900, le=2030, description="Start year")
    end_year: Optional[int] = Field(None, ge=1900, le=2030, description="End year")
    limit: Optional[int] = Field(
        1000, ge=1, le=10000, description="Maximum records to return"
    )

    @validator("data_type")
    def validate_data_type(cls, v):
        allowed_types = ["rainfall", "yield", "combined"]
        if v.lower() not in allowed_types:
            raise ValueError(f"data_type must be one of {allowed_types}")
        return v.lower()


class HistoricalDataResponse(BaseModel):
    """Schema for historical data response"""

    data_type: str = Field(..., description="Type of returned data")
    records_count: int = Field(..., description="Number of records returned")
    data: List[Dict[str, Any]] = Field(..., description="Historical data records")
    metadata: Dict[str, Any] = Field(..., description="Data metadata")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )


class ErrorResponse(BaseModel):
    """Schema for error responses"""

    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )


class HealthCheckResponse(BaseModel):
    """Schema for health check response"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    models_loaded: List[str] = Field(..., description="List of loaded models")
    uptime: float = Field(..., description="Service uptime in seconds")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Health check timestamp"
    )
