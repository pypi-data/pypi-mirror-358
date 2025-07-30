"""
Integration tests for the Monsoon Crop Predictor package.
Tests integration between different components.
"""

import unittest
import tempfile
import os
import json
import pandas as pd
from unittest.mock import patch, MagicMock

from monsoon_crop_predictor import CropPredictor
from monsoon_crop_predictor.core.data_loader import DataLoader
from monsoon_crop_predictor.core.preprocessor import Preprocessor
from monsoon_crop_predictor.core.feature_engineer import FeatureEngineer
from monsoon_crop_predictor.core.validator import Validator
from monsoon_crop_predictor.models.ensemble import EnsembleManager
from monsoon_crop_predictor.utils.config import Config
from monsoon_crop_predictor.utils.exceptions import ValidationError, ModelNotFoundError


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete prediction pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.predictor = CropPredictor()

        # Sample valid data
        self.valid_data = {
            "crop": "rice",
            "state": "West Bengal",
            "district": "Bardhaman",
            "rainfall": 1200.5,
            "temperature": 28.3,
            "humidity": 75.0,
        }

        # Sample batch data
        self.batch_data = [
            {
                "crop": "rice",
                "state": "West Bengal",
                "district": "Bardhaman",
                "rainfall": 1200.5,
                "temperature": 28.3,
                "humidity": 75.0,
            },
            {
                "crop": "wheat",
                "state": "Punjab",
                "district": "Ludhiana",
                "rainfall": 400.2,
                "temperature": 22.1,
                "humidity": 65.0,
            },
        ]

    def test_end_to_end_prediction(self):
        """Test complete prediction pipeline."""
        try:
            result = self.predictor.predict(**self.valid_data)

            # Check result structure
            self.assertIsNotNone(result)
            self.assertIsInstance(result.yield_prediction, (int, float))
            self.assertIsInstance(result.confidence, (int, float))
            self.assertIsInstance(result.risk_level, str)

            # Check value ranges
            self.assertGreater(result.yield_prediction, 0)
            self.assertGreaterEqual(result.confidence, 0)
            self.assertLessEqual(result.confidence, 1)
            self.assertIn(result.risk_level, ["Low", "Medium", "High", "Critical"])

        except ModelNotFoundError:
            self.skipTest("Model files not available for testing")

    def test_batch_prediction_integration(self):
        """Test batch prediction functionality."""
        try:
            results = self.predictor.batch_predict(self.batch_data)

            # Check results
            self.assertEqual(len(results), len(self.batch_data))

            for result in results:
                self.assertIsNotNone(result)
                self.assertIsInstance(result.yield_prediction, (int, float))
                self.assertIsInstance(result.confidence, (int, float))
                self.assertIsInstance(result.risk_level, str)

        except ModelNotFoundError:
            self.skipTest("Model files not available for testing")

    def test_validation_integration(self):
        """Test validation integration with prediction."""
        # Test invalid crop
        invalid_data = self.valid_data.copy()
        invalid_data["crop"] = "invalid_crop"

        with self.assertRaises(ValidationError):
            self.predictor.predict(**invalid_data)

        # Test invalid state
        invalid_data = self.valid_data.copy()
        invalid_data["state"] = "Invalid State"

        with self.assertRaises(ValidationError):
            self.predictor.predict(**invalid_data)

        # Test invalid rainfall
        invalid_data = self.valid_data.copy()
        invalid_data["rainfall"] = -100

        with self.assertRaises(ValidationError):
            self.predictor.predict(**invalid_data)

    def test_configuration_integration(self):
        """Test custom configuration integration."""
        custom_config = Config(confidence_threshold=0.8, feature_importance=True)

        custom_predictor = CropPredictor(config=custom_config)

        try:
            result = custom_predictor.predict(**self.valid_data)
            self.assertIsNotNone(result)

        except ModelNotFoundError:
            self.skipTest("Model files not available for testing")

    def test_data_loading_integration(self):
        """Test data loading and preprocessing integration."""
        loader = DataLoader()
        preprocessor = Preprocessor()

        # Create sample data
        sample_data = pd.DataFrame([self.valid_data])

        # Test preprocessing
        processed_data = preprocessor.handle_missing_values(sample_data)
        self.assertIsInstance(processed_data, pd.DataFrame)
        self.assertEqual(len(processed_data), 1)

        # Test feature engineering
        engineer = FeatureEngineer()
        features = engineer.create_rainfall_features(sample_data)
        self.assertIsInstance(features, pd.DataFrame)

    def test_ensemble_integration(self):
        """Test ensemble model integration."""
        ensemble_manager = EnsembleManager()

        # Test ensemble creation (mocked)
        with patch("joblib.load") as mock_load:
            mock_model = MagicMock()
            mock_model.predict.return_value = [4.5]
            mock_load.return_value = mock_model

            # Test ensemble prediction
            sample_features = pd.DataFrame(
                [[1, 2, 3, 4, 5]], columns=["f1", "f2", "f3", "f4", "f5"]
            )

            prediction = ensemble_manager.predict_with_ensemble(
                models={"model1": mock_model},
                features=sample_features,
                weights={"model1": 1.0},
            )

            self.assertIsInstance(prediction, (int, float))


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API components."""

    def setUp(self):
        """Set up API test fixtures."""
        from monsoon_crop_predictor.api.endpoints import create_app

        self.app = create_app()
        self.client = (
            self.app.test_client() if hasattr(self.app, "test_client") else None
        )

    def test_api_creation(self):
        """Test API application creation."""
        from monsoon_crop_predictor.api.endpoints import create_app

        app = create_app()
        self.assertIsNotNone(app)

    def test_schema_validation(self):
        """Test API schema validation."""
        from monsoon_crop_predictor.api.schemas import PredictionRequest

        # Valid request
        valid_request = PredictionRequest(
            crop="rice",
            state="West Bengal",
            district="Bardhaman",
            rainfall=1200.5,
            temperature=28.3,
            humidity=75.0,
        )
        self.assertEqual(valid_request.crop, "rice")

        # Invalid crop should raise validation error
        with self.assertRaises(Exception):  # Pydantic validation error
            PredictionRequest(
                crop="invalid_crop",
                state="West Bengal",
                district="Bardhaman",
                rainfall=1200.5,
                temperature=28.3,
                humidity=75.0,
            )


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI components."""

    def test_cli_import(self):
        """Test CLI module import."""
        from monsoon_crop_predictor.cli.commands import cli

        self.assertIsNotNone(cli)

    def test_cli_validation_functions(self):
        """Test CLI validation functions."""
        from monsoon_crop_predictor.cli.commands import validate_crop_input

        # Valid input
        try:
            validate_crop_input("rice", "West Bengal", "Bardhaman", 1200, 28, 75)
        except Exception as e:
            self.fail(f"Valid input raised exception: {e}")

        # Invalid crop
        with self.assertRaises(ValueError):
            validate_crop_input(
                "invalid_crop", "West Bengal", "Bardhaman", 1200, 28, 75
            )


class TestFileOperations(unittest.TestCase):
    """Test file operations and data persistence."""

    def test_csv_operations(self):
        """Test CSV file operations."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_data = """crop,state,district,rainfall,temperature,humidity
rice,West Bengal,Bardhaman,1200.5,28.3,75.0
wheat,Punjab,Ludhiana,400.2,22.1,65.0"""
            f.write(csv_data)
            csv_file = f.name

        try:
            # Test loading CSV
            df = pd.read_csv(csv_file)
            self.assertEqual(len(df), 2)
            self.assertListEqual(
                list(df.columns),
                ["crop", "state", "district", "rainfall", "temperature", "humidity"],
            )

            # Test data conversion
            data_list = df.to_dict("records")
            self.assertEqual(len(data_list), 2)
            self.assertEqual(data_list[0]["crop"], "rice")

        finally:
            # Clean up
            os.unlink(csv_file)

    def test_json_operations(self):
        """Test JSON file operations."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = {
                "crop": "rice",
                "state": "West Bengal",
                "district": "Bardhaman",
                "rainfall": 1200.5,
                "temperature": 28.3,
                "humidity": 75.0,
            }
            json.dump(test_data, f)
            json_file = f.name

        try:
            # Test loading JSON
            with open(json_file, "r") as f:
                loaded_data = json.load(f)

            self.assertEqual(loaded_data["crop"], "rice")
            self.assertEqual(loaded_data["rainfall"], 1200.5)

        finally:
            # Clean up
            os.unlink(json_file)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across components."""

    def setUp(self):
        """Set up error handling tests."""
        self.predictor = CropPredictor()

    def test_graceful_error_handling(self):
        """Test graceful error handling in predictions."""
        # Test with various invalid inputs
        invalid_inputs = [
            {"crop": "invalid_crop"},
            {"crop": "rice", "state": "Invalid State"},
            {"crop": "rice", "state": "West Bengal", "rainfall": -100},
            {"crop": "rice", "state": "West Bengal", "temperature": 100},
            {"crop": "rice", "state": "West Bengal", "humidity": 150},
        ]

        for invalid_input in invalid_inputs:
            # Fill in missing required fields with valid values
            complete_input = {
                "crop": "rice",
                "state": "West Bengal",
                "district": "Bardhaman",
                "rainfall": 1200,
                "temperature": 28,
                "humidity": 75,
            }
            complete_input.update(invalid_input)

            with self.assertRaises((ValidationError, ValueError)):
                self.predictor.predict(**complete_input)

    def test_batch_error_handling(self):
        """Test error handling in batch predictions."""
        # Mix of valid and invalid data
        mixed_data = [
            {
                "crop": "rice",
                "state": "West Bengal",
                "district": "Bardhaman",
                "rainfall": 1200,
                "temperature": 28,
                "humidity": 75,
            },
            {
                "crop": "invalid_crop",  # Invalid
                "state": "West Bengal",
                "district": "Bardhaman",
                "rainfall": 1200,
                "temperature": 28,
                "humidity": 75,
            },
        ]

        # Should handle errors gracefully
        try:
            results = self.predictor.batch_predict(mixed_data)
            # Should get results for valid data only, or raise appropriate errors
        except (ValidationError, ModelNotFoundError):
            # Expected behavior for invalid data
            pass


if __name__ == "__main__":
    # Run integration tests
    unittest.main(verbosity=2)
