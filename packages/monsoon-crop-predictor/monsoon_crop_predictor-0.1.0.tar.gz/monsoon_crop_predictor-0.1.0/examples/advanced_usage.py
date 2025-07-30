"""
Advanced usage examples for the Monsoon Crop Predictor package.
This script demonstrates advanced features and use cases.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
import json
import asyncio
import aiohttp

from monsoon_crop_predictor import CropPredictor
from monsoon_crop_predictor.utils.exceptions import ValidationError, ModelError
from monsoon_crop_predictor.utils.config import Config
from monsoon_crop_predictor.utils.logger import get_logger, setup_logging

# Setup logging
setup_logging(level="INFO")
logger = get_logger("advanced_examples")


class AdvancedAnalyzer:
    """Advanced analysis and visualization tools."""

    def __init__(self):
        self.predictor = CropPredictor()

    def scenario_analysis(
        self, base_params: Dict[str, Any], scenarios: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Perform scenario analysis with different parameter variations.

        Args:
            base_params: Base parameters for prediction
            scenarios: Dictionary of scenario names and parameter changes

        Returns:
            DataFrame with scenario analysis results
        """
        results = []

        for scenario_name, changes in scenarios.items():
            params = base_params.copy()
            params.update(changes)

            try:
                result = self.predictor.predict(**params)
                results.append(
                    {
                        "scenario": scenario_name,
                        "yield_prediction": result.yield_prediction,
                        "confidence": result.confidence,
                        "risk_level": result.risk_level,
                        **changes,
                    }
                )
            except Exception as e:
                logger.error(f"Error in scenario {scenario_name}: {e}")
                continue

        return pd.DataFrame(results)

    def sensitivity_analysis(
        self, base_params: Dict[str, Any], parameter: str, range_values: List[float]
    ) -> pd.DataFrame:
        """
        Perform sensitivity analysis for a specific parameter.

        Args:
            base_params: Base parameters for prediction
            parameter: Parameter to vary
            range_values: List of values to test

        Returns:
            DataFrame with sensitivity analysis results
        """
        results = []

        for value in range_values:
            params = base_params.copy()
            params[parameter] = value

            try:
                result = self.predictor.predict(**params)
                results.append(
                    {
                        parameter: value,
                        "yield_prediction": result.yield_prediction,
                        "confidence": result.confidence,
                        "risk_level": result.risk_level,
                    }
                )
            except Exception as e:
                logger.error(f"Error with {parameter}={value}: {e}")
                continue

        return pd.DataFrame(results)

    def plot_sensitivity_analysis(self, sensitivity_df: pd.DataFrame, parameter: str):
        """Plot sensitivity analysis results."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Yield prediction vs parameter
        ax1.plot(
            sensitivity_df[parameter],
            sensitivity_df["yield_prediction"],
            marker="o",
            linewidth=2,
            markersize=6,
        )
        ax1.set_xlabel(parameter.replace("_", " ").title())
        ax1.set_ylabel("Predicted Yield (tonnes/hectare)")
        ax1.set_title(f'Yield Sensitivity to {parameter.replace("_", " ").title()}')
        ax1.grid(True, alpha=0.3)

        # Confidence vs parameter
        ax2.plot(
            sensitivity_df[parameter],
            sensitivity_df["confidence"],
            marker="s",
            color="orange",
            linewidth=2,
            markersize=6,
        )
        ax2.set_xlabel(parameter.replace("_", " ").title())
        ax2.set_ylabel("Prediction Confidence")
        ax2.set_title(
            f'Confidence Sensitivity to {parameter.replace("_", " ").title()}'
        )
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def regional_comparison(
        self,
        crop: str,
        states_districts: List[Dict[str, str]],
        weather_params: Dict[str, float],
    ) -> pd.DataFrame:
        """
        Compare predictions across different regions.

        Args:
            crop: Crop type
            states_districts: List of {'state': '', 'district': ''} dictionaries
            weather_params: Common weather parameters

        Returns:
            DataFrame with regional comparison results
        """
        results = []

        for location in states_districts:
            params = {
                "crop": crop,
                "state": location["state"],
                "district": location["district"],
                **weather_params,
            }

            try:
                result = self.predictor.predict(**params)
                results.append(
                    {
                        "state": location["state"],
                        "district": location["district"],
                        "yield_prediction": result.yield_prediction,
                        "confidence": result.confidence,
                        "risk_level": result.risk_level,
                    }
                )
            except Exception as e:
                logger.error(f"Error for {location}: {e}")
                continue

        return pd.DataFrame(results)


def demonstrate_advanced_features():
    """Demonstrate advanced features of the package."""

    logger.info("Starting advanced features demonstration")

    # Initialize analyzer
    analyzer = AdvancedAnalyzer()

    # 1. Scenario Analysis
    print("=== Scenario Analysis ===")
    base_params = {
        "crop": "rice",
        "state": "West Bengal",
        "district": "Bardhaman",
        "rainfall": 1200,
        "temperature": 28,
        "humidity": 75,
    }

    scenarios = {
        "Normal": {},
        "Drought": {"rainfall": 600, "humidity": 50},
        "Flood": {"rainfall": 2000, "humidity": 90},
        "Heat Wave": {"temperature": 35, "humidity": 60},
        "Cold Wave": {"temperature": 20, "humidity": 80},
        "Optimal": {"rainfall": 1400, "temperature": 26, "humidity": 78},
    }

    scenario_results = analyzer.scenario_analysis(base_params, scenarios)
    print(scenario_results)

    # 2. Sensitivity Analysis
    print("\n=== Sensitivity Analysis ===")
    rainfall_values = np.linspace(400, 2000, 20)
    rainfall_sensitivity = analyzer.sensitivity_analysis(
        base_params, "rainfall", rainfall_values
    )

    if len(rainfall_sensitivity) > 0:
        analyzer.plot_sensitivity_analysis(rainfall_sensitivity, "rainfall")

    # 3. Regional Comparison
    print("\n=== Regional Comparison ===")
    regions = [
        {"state": "West Bengal", "district": "Bardhaman"},
        {"state": "Punjab", "district": "Ludhiana"},
        {"state": "Tamil Nadu", "district": "Thanjavur"},
        {"state": "Andhra Pradesh", "district": "Krishna"},
        {"state": "Maharashtra", "district": "Pune"},
    ]

    weather_params = {"rainfall": 1200, "temperature": 28, "humidity": 75}

    regional_results = analyzer.regional_comparison("rice", regions, weather_params)
    print(regional_results)

    # 4. Batch Processing with Error Handling
    print("\n=== Robust Batch Processing ===")

    # Create test data with some invalid entries
    test_data = [
        {
            "crop": "rice",
            "state": "West Bengal",
            "district": "Bardhaman",
            "rainfall": 1200,
            "temperature": 28,
            "humidity": 75,
        },
        {
            "crop": "wheat",
            "state": "Punjab",
            "district": "Ludhiana",
            "rainfall": 400,
            "temperature": 22,
            "humidity": 65,
        },
        {
            "crop": "invalid_crop",
            "state": "Invalid State",
            "district": "Invalid District",
            "rainfall": -100,
            "temperature": 100,
            "humidity": 150,
        },  # Invalid data
        {
            "crop": "maize",
            "state": "Maharashtra",
            "district": "Pune",
            "rainfall": 800,
            "temperature": 25,
            "humidity": 70,
        },
    ]

    valid_results = []
    errors = []

    for i, data in enumerate(test_data):
        try:
            result = analyzer.predictor.predict(**data)
            valid_results.append(
                {"index": i, "input_data": data, "result": result.dict()}
            )
        except Exception as e:
            errors.append({"index": i, "input_data": data, "error": str(e)})

    print(f"Valid predictions: {len(valid_results)}")
    print(f"Errors: {len(errors)}")

    for error in errors:
        print(f"Error at index {error['index']}: {error['error']}")


async def demonstrate_async_api_usage():
    """Demonstrate asynchronous API usage."""

    logger.info("Demonstrating async API usage")

    api_url = "http://localhost:8000"

    # Test data for multiple predictions
    predictions = [
        {
            "crop": "rice",
            "state": "West Bengal",
            "district": "Bardhaman",
            "rainfall": 1200,
            "temperature": 28,
            "humidity": 75,
        },
        {
            "crop": "wheat",
            "state": "Punjab",
            "district": "Ludhiana",
            "rainfall": 400,
            "temperature": 22,
            "humidity": 65,
        },
        {
            "crop": "maize",
            "state": "Maharashtra",
            "district": "Pune",
            "rainfall": 800,
            "temperature": 25,
            "humidity": 70,
        },
    ]

    async def make_prediction(session, prediction_data):
        """Make a single prediction via API."""
        try:
            async with session.post(
                f"{api_url}/predict",
                json=prediction_data,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"success": True, "data": result, "input": prediction_data}
                else:
                    error = await response.text()
                    return {"success": False, "error": error, "input": prediction_data}
        except Exception as e:
            return {"success": False, "error": str(e), "input": prediction_data}

    async def batch_api_predictions():
        """Make multiple predictions concurrently."""
        async with aiohttp.ClientSession() as session:
            # First check if API is available
            try:
                async with session.get(f"{api_url}/health") as response:
                    if response.status != 200:
                        print(
                            "API server is not available. Please start it with: monsoon-crop api"
                        )
                        return
            except:
                print(
                    "API server is not available. Please start it with: monsoon-crop api"
                )
                return

            # Make concurrent predictions
            tasks = [make_prediction(session, pred) for pred in predictions]
            results = await asyncio.gather(*tasks)

            # Process results
            successful = [r for r in results if r["success"]]
            failed = [r for r in results if not r["success"]]

            print(f"Successful predictions: {len(successful)}")
            print(f"Failed predictions: {len(failed)}")

            for result in successful:
                input_data = result["input"]
                prediction = result["data"]
                print(
                    f"{input_data['crop']} in {input_data['district']}: "
                    f"{prediction['yield_prediction']:.2f} tonnes/hectare"
                )

            for result in failed:
                input_data = result["input"]
                print(
                    f"Failed for {input_data['crop']} in {input_data['district']}: "
                    f"{result['error']}"
                )

    await batch_api_predictions()


def demonstrate_custom_configuration():
    """Demonstrate custom configuration usage."""

    logger.info("Demonstrating custom configuration")

    # Create custom configuration
    custom_config = Config(
        confidence_threshold=0.8,
        feature_importance=True,
        ensemble_weights={"random_forest": 0.3, "xgboost": 0.4, "lightgbm": 0.3},
    )

    # Initialize predictor with custom config
    custom_predictor = CropPredictor(config=custom_config)

    # Make prediction
    result = custom_predictor.predict(
        crop="rice",
        state="West Bengal",
        district="Bardhaman",
        rainfall=1200,
        temperature=28,
        humidity=75,
    )

    print("Prediction with custom configuration:")
    print(f"Yield: {result.yield_prediction:.2f} tonnes/hectare")
    print(f"Confidence: {result.confidence:.2f}")

    if hasattr(result, "feature_importance"):
        print("Feature importance:")
        for feature, importance in result.feature_importance.items():
            print(f"  {feature}: {importance:.3f}")


def main():
    """Main function to run all demonstrations."""

    print("Monsoon Crop Predictor - Advanced Examples")
    print("=" * 50)

    try:
        # Run demonstrations
        demonstrate_advanced_features()

        print("\n" + "=" * 50)
        demonstrate_custom_configuration()

        print("\n" + "=" * 50)
        print("For async API demonstration, make sure the API server is running:")
        print("monsoon-crop api")
        print("Then uncomment the following line:")
        # asyncio.run(demonstrate_async_api_usage())

    except Exception as e:
        logger.error(f"Error in demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
