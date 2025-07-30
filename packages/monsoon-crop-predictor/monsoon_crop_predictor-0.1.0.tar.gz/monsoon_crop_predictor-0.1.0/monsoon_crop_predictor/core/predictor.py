"""
Main prediction engine for Monsoon Crop Predictor
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import warnings

warnings.filterwarnings("ignore")

from ..core.data_loader import DataLoader
from ..core.preprocessor import DataPreprocessor
from ..core.feature_engineer import FeatureEngineer
from ..core.validator import DataValidator
from ..utils.config import Config
from ..utils.exceptions import (
    PredictionError,
    ModelLoadError,
    DataValidationError,
    UnsupportedCropError,
    InsufficientDataError,
)
from ..utils.logger import LoggerMixin


class PredictionResult:
    """Stub for PredictionResult. Implement functionality as needed."""

    pass


class CropYieldPredictor(LoggerMixin):
    """
    Main prediction engine for crop yield forecasting
    """

    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize the predictor

        Args:
            model_dir: Optional custom directory containing model files
        """
        self.config = Config()
        self.model_dir = Path(model_dir) if model_dir else self.config.MODELS_DIR

        # Initialize components
        self.data_loader = DataLoader()
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.validator = DataValidator()

        # Model storage
        self.models = {}
        self.feature_columns = {}
        self.scalers = {}

        self.logger.info("CropYieldPredictor initialized")

    def load_model(self, crop: str) -> None:
        """
        Load the trained model for a specific crop

        Args:
            crop: Crop name (RICE, WHEAT, MAIZE)

        Raises:
            UnsupportedCropError: If crop is not supported
            ModelLoadError: If model loading fails
        """
        crop = self.config.validate_crop(crop)

        if crop in self.models:
            self.logger.info(f"Model for {crop} already loaded")
            return

        model_path = self.config.get_model_path(crop)

        if not model_path.exists():
            raise ModelLoadError(f"Model file not found: {model_path}")

        try:
            self.logger.info(f"Loading model for {crop} from {model_path}")

            with open(model_path, "rb") as f:
                model_data = pickle.load(f)

            # Handle different model storage formats
            if isinstance(model_data, dict):
                self.models[crop] = model_data.get("model") or model_data.get(
                    "ensemble"
                )
                self.feature_columns[crop] = model_data.get("feature_columns", [])
                self.scalers[crop] = model_data.get("scaler")
            else:
                # Assume it's just the model
                self.models[crop] = model_data
                self.feature_columns[crop] = []

            self.logger.info(f"Successfully loaded model for {crop}")

        except Exception as e:
            raise ModelLoadError(f"Failed to load model for {crop}: {str(e)}")

    def load_all_models(self) -> None:
        """Load all available crop models"""
        self.logger.info("Loading all available models")

        for crop in self.config.SUPPORTED_CROPS:
            try:
                self.load_model(crop)
            except ModelLoadError as e:
                self.logger.warning(f"Could not load model for {crop}: {str(e)}")

    def predict_single(
        self,
        input_data: Dict[str, Any],
        crop: str,
        include_confidence: bool = False,
        validate_input: bool = True,
    ) -> Dict[str, Any]:
        """
        Make a single crop yield prediction

        Args:
            input_data: Dictionary containing prediction features
            crop: Crop type (RICE, WHEAT, MAIZE)
            include_confidence: Whether to include prediction confidence
            validate_input: Whether to validate input data

        Returns:
            Dictionary containing prediction results

        Raises:
            PredictionError: If prediction fails
            DataValidationError: If input validation fails
        """
        self.logger.info(f"Making single prediction for {crop}")

        try:
            # Validate crop
            crop = self.config.validate_crop(crop)

            # Load model if not already loaded
            if crop not in self.models:
                self.load_model(crop)

            # Validate input if requested
            if validate_input:
                validation_result = self.validator.validate_prediction_input(
                    input_data, crop
                )
                if not validation_result["valid"]:
                    raise DataValidationError(
                        f"Input validation failed: {validation_result['issues']}"
                    )
                processed_data = validation_result["processed_data"]
            else:
                processed_data = input_data.copy()

            # Convert to DataFrame for processing
            df = pd.DataFrame([processed_data])

            # Feature engineering
            df_engineered = self._engineer_features_for_prediction(df)

            # Prepare features for model
            X = self._prepare_features_for_model(df_engineered, crop)

            # Make prediction
            model = self.models[crop]
            prediction = model.predict(X)[0]

            # Prepare result
            result = {
                "crop": crop,
                "predicted_yield": float(prediction),
                "unit": "kg/ha",
                "input_data": processed_data,
                "model_version": getattr(model, "version", "unknown"),
            }

            # Add confidence interval if requested
            if include_confidence:
                result.update(self._calculate_confidence_interval(X, crop, prediction))

            self.logger.info(f"Prediction completed: {prediction:.2f} kg/ha")
            return result

        except Exception as e:
            error_msg = f"Prediction failed for {crop}: {str(e)}"
            self.logger.error(error_msg)
            raise PredictionError(error_msg)

    def predict_batch(
        self,
        input_data: Union[pd.DataFrame, List[Dict]],
        crop: str,
        include_confidence: bool = False,
        validate_input: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Make batch predictions for multiple inputs

        Args:
            input_data: DataFrame or list of dictionaries containing prediction features
            crop: Crop type
            include_confidence: Whether to include prediction confidence
            validate_input: Whether to validate input data

        Returns:
            List of prediction result dictionaries
        """
        self.logger.info(f"Making batch predictions for {crop}")

        try:
            # Convert input to DataFrame if needed
            if isinstance(input_data, list):
                df = pd.DataFrame(input_data)
            else:
                df = input_data.copy()

            # Validate crop
            crop = self.config.validate_crop(crop)

            # Load model if not already loaded
            if crop not in self.models:
                self.load_model(crop)

            # Validate input if requested
            if validate_input:
                validation_report = self.validator.generate_validation_report(df, crop)
                if not validation_report["overall_assessment"]["overall_valid"]:
                    raise DataValidationError(f"Batch input validation failed")

            # Feature engineering
            df_engineered = self._engineer_features_for_prediction(df)

            # Prepare features for model
            X = self._prepare_features_for_model(df_engineered, crop)

            # Make predictions
            model = self.models[crop]
            predictions = model.predict(X)

            # Prepare results
            results = []
            for i, prediction in enumerate(predictions):
                result = {
                    "index": i,
                    "crop": crop,
                    "predicted_yield": float(prediction),
                    "unit": "kg/ha",
                    "input_data": df.iloc[i].to_dict(),
                    "model_version": getattr(model, "version", "unknown"),
                }

                if include_confidence:
                    result.update(
                        self._calculate_confidence_interval(
                            X.iloc[[i]], crop, prediction
                        )
                    )

                results.append(result)

            self.logger.info(f"Batch predictions completed for {len(results)} samples")
            return results

        except Exception as e:
            error_msg = f"Batch prediction failed for {crop}: {str(e)}"
            self.logger.error(error_msg)
            raise PredictionError(error_msg)

    def analyze_monsoon_patterns(
        self,
        rainfall_data: pd.DataFrame,
        location: Optional[str] = None,
        years: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze monsoon patterns from rainfall data

        Args:
            rainfall_data: DataFrame containing rainfall information
            location: Optional location filter (State Name)
            years: Optional list of years to analyze

        Returns:
            Dictionary containing monsoon analysis results
        """
        self.logger.info("Analyzing monsoon patterns")

        try:
            # Filter data if location or years specified
            filtered_data = rainfall_data.copy()

            if location and "State Name" in filtered_data.columns:
                filtered_data = filtered_data[
                    filtered_data["State Name"].str.upper() == location.upper()
                ]

            if years and "Year" in filtered_data.columns:
                filtered_data = filtered_data[filtered_data["Year"].isin(years)]

            if filtered_data.empty:
                raise InsufficientDataError("No data available for specified filters")

            # Create rainfall features for analysis
            analyzed_data = self.feature_engineer.create_rainfall_features(
                filtered_data
            )

            # Calculate monsoon statistics
            analysis = {
                "period": {
                    "start_year": int(filtered_data["Year"].min()),
                    "end_year": int(filtered_data["Year"].max()),
                    "total_years": len(filtered_data["Year"].unique()),
                },
                "location": location,
                "rainfall_statistics": self._calculate_rainfall_statistics(
                    analyzed_data
                ),
                "monsoon_patterns": self._analyze_monsoon_patterns(analyzed_data),
                "trends": self._calculate_rainfall_trends(analyzed_data),
                "extreme_events": self._identify_extreme_events(analyzed_data),
            }

            self.logger.info("Monsoon pattern analysis completed")
            return analysis

        except Exception as e:
            error_msg = f"Monsoon analysis failed: {str(e)}"
            self.logger.error(error_msg)
            raise PredictionError(error_msg)

    def recommend_optimal_crop(
        self, input_data: Dict[str, Any], crops: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Recommend optimal crop based on predicted yields

        Args:
            input_data: Dictionary containing prediction features
            crops: Optional list of crops to consider (default: all supported)

        Returns:
            Dictionary containing crop recommendations
        """
        self.logger.info("Generating crop recommendations")

        if crops is None:
            crops = self.config.SUPPORTED_CROPS

        try:
            predictions = {}

            # Get predictions for each crop
            for crop in crops:
                try:
                    result = self.predict_single(
                        input_data, crop, include_confidence=True, validate_input=False
                    )
                    predictions[crop] = result
                except Exception as e:
                    self.logger.warning(f"Could not predict for {crop}: {str(e)}")

            if not predictions:
                raise PredictionError("No valid predictions could be made")

            # Rank crops by predicted yield
            ranked_crops = sorted(
                predictions.items(), key=lambda x: x[1]["predicted_yield"], reverse=True
            )

            recommendation = {
                "input_conditions": input_data,
                "predictions": predictions,
                "ranking": [
                    {
                        "rank": i + 1,
                        "crop": crop,
                        "predicted_yield": predictions[crop]["predicted_yield"],
                        "confidence_interval": predictions[crop].get(
                            "confidence_interval"
                        ),
                    }
                    for i, (crop, _) in enumerate(ranked_crops)
                ],
                "recommended_crop": ranked_crops[0][0],
                "recommendation_confidence": self._calculate_recommendation_confidence(
                    predictions
                ),
            }

            self.logger.info(f"Recommended crop: {recommendation['recommended_crop']}")
            return recommendation

        except Exception as e:
            error_msg = f"Crop recommendation failed: {str(e)}"
            self.logger.error(error_msg)
            raise PredictionError(error_msg)

    def assess_agricultural_risk(
        self, input_data: Dict[str, Any], crop: str
    ) -> Dict[str, Any]:
        """
        Assess agricultural risk based on weather and yield predictions

        Args:
            input_data: Dictionary containing prediction features
            crop: Crop type for risk assessment

        Returns:
            Dictionary containing risk assessment
        """
        self.logger.info(f"Assessing agricultural risk for {crop}")

        try:
            # Get prediction with confidence
            prediction_result = self.predict_single(
                input_data, crop, include_confidence=True, validate_input=True
            )

            # Calculate various risk factors
            rainfall_risk = self._assess_rainfall_risk(input_data)
            yield_risk = self._assess_yield_risk(prediction_result)
            temporal_risk = self._assess_temporal_risk(input_data)

            # Combine risk factors
            overall_risk = (rainfall_risk + yield_risk + temporal_risk) / 3

            risk_assessment = {
                "crop": crop,
                "predicted_yield": prediction_result["predicted_yield"],
                "risk_factors": {
                    "rainfall_risk": rainfall_risk,
                    "yield_risk": yield_risk,
                    "temporal_risk": temporal_risk,
                    "overall_risk": overall_risk,
                },
                "risk_level": self._categorize_risk_level(overall_risk),
                "recommendations": self._generate_risk_recommendations(
                    overall_risk, input_data, crop
                ),
                "confidence": prediction_result.get("confidence_score", 0.5),
            }

            self.logger.info(
                f"Risk assessment completed. Overall risk: {overall_risk:.2f}"
            )
            return risk_assessment

        except Exception as e:
            error_msg = f"Risk assessment failed for {crop}: {str(e)}"
            self.logger.error(error_msg)
            raise PredictionError(error_msg)

    def _engineer_features_for_prediction(self, data: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for prediction"""
        # Create basic rainfall features
        data = self.feature_engineer.create_rainfall_features(data)

        # Create temporal features if Year is present
        if "Year" in data.columns:
            data = self.feature_engineer.create_temporal_features(data)

        return data

    def _prepare_features_for_model(
        self, data: pd.DataFrame, crop: str
    ) -> pd.DataFrame:
        """Prepare features for model prediction"""
        feature_cols = self.feature_columns.get(crop, [])

        if not feature_cols:
            # Use all numeric columns except excluded ones
            exclude_cols = ["Year", "State Name", "Dist Name"] + list(
                self.config.TARGET_COLUMNS.values()
            )
            feature_cols = [
                col
                for col in data.select_dtypes(include=[np.number]).columns
                if col not in exclude_cols
            ]

        # Select available features
        available_features = [col for col in feature_cols if col in data.columns]

        if not available_features:
            raise PredictionError("No suitable features found for prediction")

        X = data[available_features]

        # Apply scaling if available
        if crop in self.scalers and self.scalers[crop] is not None:
            X = pd.DataFrame(
                self.scalers[crop].transform(X), columns=X.columns, index=X.index
            )

        return X

    def _calculate_confidence_interval(
        self, X: pd.DataFrame, crop: str, prediction: float
    ) -> Dict[str, Any]:
        """Calculate prediction confidence interval"""
        # This is a simplified confidence calculation
        # In practice, you might use model-specific methods

        model = self.models[crop]
        confidence_score = 0.8  # Default confidence

        # Calculate prediction interval (simplified)
        prediction_std = prediction * 0.15  # Assume 15% standard deviation

        return {
            "confidence_score": confidence_score,
            "confidence_interval": {
                "lower": max(0, prediction - 1.96 * prediction_std),
                "upper": prediction + 1.96 * prediction_std,
                "width": 2 * 1.96 * prediction_std,
            },
        }

    def _calculate_rainfall_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive rainfall statistics"""
        rainfall_cols = ["Annual", "Jan-Feb", "Mar-May", "Jun-Sep", "Oct-Dec"]
        available_cols = [col for col in rainfall_cols if col in data.columns]

        stats = {}
        for col in available_cols:
            stats[col] = {
                "mean": float(data[col].mean()),
                "median": float(data[col].median()),
                "std": float(data[col].std()),
                "min": float(data[col].min()),
                "max": float(data[col].max()),
                "cv": float(
                    data[col].std() / data[col].mean() * 100
                ),  # Coefficient of variation
            }

        return stats

    def _analyze_monsoon_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze monsoon patterns"""
        if "Monsoon_Intensity" not in data.columns:
            return {}

        return {
            "average_monsoon_intensity": float(data["Monsoon_Intensity"].mean()),
            "monsoon_variability": float(data["Monsoon_Intensity"].std()),
            "strong_monsoon_years": len(data[data["Monsoon_Intensity"] > 0.7]),
            "weak_monsoon_years": len(data[data["Monsoon_Intensity"] < 0.4]),
            "monsoon_concentration": float(
                data.get("Monsoon_Concentration", pd.Series([0])).mean()
            ),
        }

    def _calculate_rainfall_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate rainfall trends over time"""
        if "Year" not in data.columns or "Annual" not in data.columns:
            return {}

        # Simple linear trend
        years = data["Year"].values
        rainfall = data["Annual"].values

        if len(years) > 1:
            slope = np.polyfit(years, rainfall, 1)[0]
            return {
                "annual_trend": float(slope),
                "trend_direction": "increasing" if slope > 0 else "decreasing",
                "trend_significance": "moderate" if abs(slope) > 1 else "weak",
            }

        return {}

    def _identify_extreme_events(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identify extreme weather events"""
        if "Annual" not in data.columns:
            return {}

        annual_rainfall = data["Annual"]
        q25 = annual_rainfall.quantile(0.25)
        q75 = annual_rainfall.quantile(0.75)

        drought_years = (
            data[annual_rainfall < q25]["Year"].tolist()
            if "Year" in data.columns
            else []
        )
        flood_years = (
            data[annual_rainfall > q75]["Year"].tolist()
            if "Year" in data.columns
            else []
        )

        return {
            "drought_threshold": float(q25),
            "flood_threshold": float(q75),
            "drought_years": [int(year) for year in drought_years],
            "flood_years": [int(year) for year in flood_years],
            "extreme_events_frequency": len(drought_years) + len(flood_years),
        }

    def _calculate_recommendation_confidence(
        self, predictions: Dict[str, Dict]
    ) -> float:
        """Calculate confidence in crop recommendation"""
        if len(predictions) < 2:
            return 0.5

        yields = [pred["predicted_yield"] for pred in predictions.values()]
        best_yield = max(yields)
        second_best = sorted(yields, reverse=True)[1]

        # Confidence based on yield difference
        yield_difference = (best_yield - second_best) / second_best
        confidence = min(1.0, 0.5 + yield_difference)

        return confidence

    def _assess_rainfall_risk(self, input_data: Dict[str, Any]) -> float:
        """Assess risk based on rainfall patterns"""
        annual = input_data.get("Annual", 1000)
        monsoon = input_data.get("Jun-Sep", 600)

        # Risk factors
        drought_risk = 1.0 if annual < 600 else max(0, (800 - annual) / 200)
        flood_risk = 1.0 if annual > 2000 else max(0, (annual - 1800) / 200)
        monsoon_risk = abs(monsoon / annual - 0.6) if annual > 0 else 0.5

        return min(1.0, max(drought_risk, flood_risk) + monsoon_risk * 0.5)

    def _assess_yield_risk(self, prediction_result: Dict[str, Any]) -> float:
        """Assess risk based on yield prediction"""
        predicted_yield = prediction_result["predicted_yield"]
        confidence_interval = prediction_result.get("confidence_interval", {})

        # Risk based on yield level and prediction uncertainty
        yield_risk = 0.5 if predicted_yield > 3000 else (4000 - predicted_yield) / 4000

        uncertainty_risk = 0
        if confidence_interval:
            interval_width = confidence_interval.get("width", 0)
            uncertainty_risk = min(0.5, interval_width / predicted_yield)

        return min(1.0, yield_risk + uncertainty_risk)

    def _assess_temporal_risk(self, input_data: Dict[str, Any]) -> float:
        """Assess risk based on temporal factors"""
        year = input_data.get("Year", 2020)

        # Simple temporal risk based on year
        # In practice, this would consider climate change trends, etc.
        base_year = 2020
        years_diff = abs(year - base_year)

        return min(0.3, years_diff * 0.01)  # Max 30% risk, 1% per year difference

    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize overall risk level"""
        if risk_score < 0.3:
            return "Low"
        elif risk_score < 0.6:
            return "Medium"
        else:
            return "High"

    def _generate_risk_recommendations(
        self, risk_score: float, input_data: Dict[str, Any], crop: str
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        if risk_score > 0.6:
            recommendations.append(
                "Consider crop insurance due to high risk conditions"
            )
            recommendations.append("Implement water conservation measures")

        annual_rainfall = input_data.get("Annual", 1000)
        if annual_rainfall < 700:
            recommendations.append("Consider drought-resistant varieties")
            recommendations.append("Plan for supplementary irrigation")
        elif annual_rainfall > 1800:
            recommendations.append("Ensure proper drainage systems")
            recommendations.append("Monitor for pest and disease outbreaks")

        if crop == "RICE" and input_data.get("Jun-Sep", 0) < 400:
            recommendations.append("Rice may not be suitable with low monsoon rainfall")

        if not recommendations:
            recommendations.append("Conditions appear favorable for cultivation")

        return recommendations
