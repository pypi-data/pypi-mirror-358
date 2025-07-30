"""
FastAPI endpoints for Monsoon Crop Predictor
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import time
import logging
from datetime import datetime

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
from .middleware import setup_middleware, get_rate_limiter
from ..core.predictor import CropYieldPredictor
from ..core.data_loader import DataLoader
from ..utils.config import Config
from ..utils.exceptions import (
    PredictionError,
    DataValidationError,
    ModelLoadError,
    UnsupportedCropError,
    InsufficientDataError,
)
from ..utils.logger import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Monsoon Crop Predictor API",
    description="Advanced ML-based crop yield prediction system using monsoon and rainfall data",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup middleware
setup_middleware(app)

# Global variables
predictor: Optional[CropYieldPredictor] = None
data_loader: Optional[DataLoader] = None
config = Config()
start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global predictor, data_loader

    logger.info("Starting Monsoon Crop Predictor API")

    try:
        # Initialize predictor and load models
        predictor = CropYieldPredictor()
        predictor.load_all_models()

        # Initialize data loader
        data_loader = DataLoader()

        logger.info("API startup completed successfully")

    except Exception as e:
        logger.error(f"Failed to start API: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Monsoon Crop Predictor API")


def get_predictor() -> CropYieldPredictor:
    """Dependency to get predictor instance"""
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Predictor service not available",
        )
    return predictor


def get_data_loader() -> DataLoader:
    """Dependency to get data loader instance"""
    if data_loader is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data loader service not available",
        )
    return data_loader


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        uptime = time.time() - start_time
        models_loaded = list(predictor.models.keys()) if predictor else []

        return HealthCheckResponse(
            status="healthy",
            version="0.1.0",
            models_loaded=models_loaded,
            uptime=uptime,
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/predict_yield", response_model=PredictionResponse)
async def predict_yield(
    request: PredictionRequest,
    predictor: CropYieldPredictor = Depends(get_predictor),
    rate_limiter=Depends(get_rate_limiter),
):
    """Make a single crop yield prediction"""
    try:
        logger.info(f"Prediction request for {request.crop}")

        # Convert request to dict
        input_data = request.dict(by_alias=True)

        # Make prediction
        result = predictor.predict_single(
            input_data=input_data,
            crop=request.crop,
            include_confidence=request.include_confidence,
            validate_input=True,
        )

        # Convert to response format
        response_data = {
            "crop": result["crop"],
            "predicted_yield": result["predicted_yield"],
            "unit": result["unit"],
            "input_data": result["input_data"],
            "model_version": result["model_version"],
        }

        if request.include_confidence and "confidence_score" in result:
            response_data["confidence_score"] = result["confidence_score"]
            response_data["confidence_interval"] = result.get("confidence_interval")

        return PredictionResponse(**response_data)

    except (PredictionError, DataValidationError, UnsupportedCropError) as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/batch_predict", response_model=BatchPredictionResponse)
async def batch_predict(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    predictor: CropYieldPredictor = Depends(get_predictor),
    rate_limiter=Depends(get_rate_limiter),
):
    """Make batch crop yield predictions"""
    try:
        logger.info(
            f"Batch prediction request for {request.crop}, {len(request.predictions)} samples"
        )

        # Make batch predictions
        results = predictor.predict_batch(
            input_data=request.predictions,
            crop=request.crop,
            include_confidence=request.include_confidence,
            validate_input=True,
        )

        # Convert results to response format
        prediction_responses = []
        for result in results:
            response_data = {
                "crop": result["crop"],
                "predicted_yield": result["predicted_yield"],
                "unit": result["unit"],
                "input_data": result["input_data"],
                "model_version": result["model_version"],
            }

            if request.include_confidence:
                response_data["confidence_score"] = result.get("confidence_score")
                response_data["confidence_interval"] = result.get("confidence_interval")

            prediction_responses.append(PredictionResponse(**response_data))

        # Calculate summary statistics
        yields = [r.predicted_yield for r in prediction_responses]
        summary = {
            "total_predictions": len(prediction_responses),
            "mean_yield": float(np.mean(yields)),
            "std_yield": float(np.std(yields)),
            "min_yield": float(np.min(yields)),
            "max_yield": float(np.max(yields)),
        }

        return BatchPredictionResponse(
            crop=request.crop, predictions=prediction_responses, summary=summary
        )

    except (PredictionError, DataValidationError, UnsupportedCropError) as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in batch prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/monsoon_analysis", response_model=MonsoonAnalysisResponse)
async def monsoon_analysis(
    request: MonsoonAnalysisRequest,
    predictor: CropYieldPredictor = Depends(get_predictor),
    data_loader: DataLoader = Depends(get_data_loader),
):
    """Analyze monsoon patterns"""
    try:
        logger.info(f"Monsoon analysis request for {request.location}")

        # Load sample rainfall data for analysis
        # In production, this would load from a database or file system
        sample_data = {
            "Year": list(range(request.start_year or 2000, request.end_year or 2024)),
            "Annual": np.random.normal(
                1000, 200, request.end_year or 2024 - (request.start_year or 2000)
            ),
            "Jun-Sep": np.random.normal(
                600, 150, request.end_year or 2024 - (request.start_year or 2000)
            ),
        }

        if request.location:
            sample_data["State Name"] = [request.location] * len(sample_data["Year"])

        rainfall_data = pd.DataFrame(sample_data)

        # Perform analysis
        analysis = predictor.analyze_monsoon_patterns(
            rainfall_data=rainfall_data,
            location=request.location,
            years=list(range(request.start_year or 2000, request.end_year or 2024)),
        )

        return MonsoonAnalysisResponse(**analysis)

    except (InsufficientDataError, DataValidationError) as e:
        logger.error(f"Monsoon analysis error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in monsoon analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/crop_recommendations", response_model=CropRecommendationResponse)
async def crop_recommendations(
    request: CropRecommendationRequest,
    predictor: CropYieldPredictor = Depends(get_predictor),
):
    """Get optimal crop recommendations"""
    try:
        logger.info("Crop recommendation request")

        # Convert request to dict
        input_data = request.dict(by_alias=True)

        # Get recommendations
        recommendation = predictor.recommend_optimal_crop(
            input_data=input_data, crops=request.crops_to_consider
        )

        return CropRecommendationResponse(**recommendation)

    except (PredictionError, DataValidationError) as e:
        logger.error(f"Crop recommendation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in crop recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/risk_assessment", response_model=RiskAssessmentResponse)
async def risk_assessment(
    request: RiskAssessmentRequest,
    predictor: CropYieldPredictor = Depends(get_predictor),
):
    """Assess agricultural risk"""
    try:
        logger.info(f"Risk assessment request for {request.crop}")

        # Convert request to dict
        input_data = request.dict(by_alias=True)

        # Perform risk assessment
        assessment = predictor.assess_agricultural_risk(
            input_data=input_data, crop=request.crop
        )

        return RiskAssessmentResponse(**assessment)

    except (PredictionError, DataValidationError, UnsupportedCropError) as e:
        logger.error(f"Risk assessment error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/historical_data", response_model=HistoricalDataResponse)
async def get_historical_data(
    data_type: str,
    location: Optional[str] = None,
    crop: Optional[str] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    limit: int = 1000,
    data_loader: DataLoader = Depends(get_data_loader),
):
    """Retrieve historical data"""
    try:
        logger.info(f"Historical data request: {data_type}")

        # In production, this would query actual historical databases
        # For now, return sample data
        sample_records = []
        for i in range(min(limit, 100)):  # Limit sample data
            record = {
                "Year": 2020 + (i % 5),
                "Annual": 1000 + i * 10,
                "Jun-Sep": 600 + i * 5,
                "State Name": location or "Sample State",
                "data_type": data_type,
            }

            if crop and data_type in ["yield", "combined"]:
                record[f"{crop.upper()} YIELD (Kg per ha)"] = 3000 + i * 50

            sample_records.append(record)

        metadata = {
            "source": "Sample data",
            "filters_applied": {
                "location": location,
                "crop": crop,
                "start_year": start_year,
                "end_year": end_year,
            },
            "total_available": len(sample_records),
        }

        return HistoricalDataResponse(
            data_type=data_type,
            records_count=len(sample_records),
            data=sample_records,
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Historical data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_type="HTTPException",
            message=exc.detail,
            details={"status_code": exc.status_code},
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            details={"exception_type": type(exc).__name__},
        ).dict(),
    )


def create_app():
    """Stub for create_app. Implement functionality as needed."""
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=config.API_CONFIG["host"],
        port=config.API_CONFIG["port"],
        workers=config.API_CONFIG["workers"],
        timeout_keep_alive=config.API_CONFIG["timeout"],
    )
