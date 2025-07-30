"""
Unit tests for the core components of Monsoon Crop Predictor
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import sys

# Add the package to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from monsoon_crop_predictor.core.data_loader import DataLoader
from monsoon_crop_predictor.core.preprocessor import DataPreprocessor
from monsoon_crop_predictor.core.feature_engineer import FeatureEngineer
from monsoon_crop_predictor.core.validator import DataValidator
from monsoon_crop_predictor.utils.config import Config
from monsoon_crop_predictor.utils.exceptions import DataValidationError


class TestDataLoader(unittest.TestCase):
    """Test cases for DataLoader"""

    def setUp(self):
        self.loader = DataLoader()
        self.sample_data = pd.DataFrame(
            {
                "Year": [2020, 2021, 2022],
                "Annual": [1000, 1200, 950],
                "Jun-Sep": [600, 750, 580],
                "State Name": ["Punjab", "Punjab", "Haryana"],
                "Dist Name": ["Ludhiana", "Ludhiana", "Karnal"],
            }
        )

    def test_data_validation(self):
        """Test basic data validation"""
        # Should pass validation
        self.loader.validate_data(self.sample_data)

        # Should fail with empty data
        empty_data = pd.DataFrame()
        with self.assertRaises(DataValidationError):
            self.loader.validate_data(empty_data)

    def test_data_summary(self):
        """Test data summary generation"""
        summary = self.loader.get_data_summary(self.sample_data)

        self.assertIn("shape", summary)
        self.assertIn("columns", summary)
        self.assertIn("year_range", summary)
        self.assertEqual(summary["shape"], (3, 5))
        self.assertEqual(summary["year_range"]["min"], 2020)
        self.assertEqual(summary["year_range"]["max"], 2022)


class TestDataPreprocessor(unittest.TestCase):
    """Test cases for DataPreprocessor"""

    def setUp(self):
        self.preprocessor = DataPreprocessor()
        self.sample_data = pd.DataFrame(
            {
                "Year": [2020, 2021, 2022, 2023, 2024],
                "Annual": [1000, np.nan, 950, 1200, 800],
                "Jun-Sep": [600, 750, np.nan, 700, 500],
                "State Name": ["Punjab", "Punjab", "Haryana", "Punjab", "UP"],
                "RICE YIELD (Kg per ha)": [3000, 3200, 2800, 3400, 2600],
            }
        )

    def test_missing_value_handling(self):
        """Test missing value imputation"""
        # Test mean imputation
        result = self.preprocessor.handle_missing_values(
            self.sample_data, strategy="mean"
        )

        # Should have no missing values in numeric columns
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        self.assertEqual(result[numeric_cols].isnull().sum().sum(), 0)

    def test_geographical_normalization(self):
        """Test geographical name normalization"""
        result = self.preprocessor.normalize_geographical_names(self.sample_data)

        # State names should be uppercase
        self.assertTrue(all(state.isupper() for state in result["State Name"]))

    def test_temporal_splits(self):
        """Test temporal data splitting"""
        target_col = "RICE YIELD (Kg per ha)"
        splits = self.preprocessor.create_temporal_splits(self.sample_data, target_col)

        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols = splits

        # Check that splits sum to original data size
        total_size = len(X_train) + len(X_val) + len(X_test)
        self.assertEqual(total_size, len(self.sample_data))

        # Check that feature columns don't include target or identifier columns
        excluded_cols = [target_col, "Year", "State Name", "Dist Name"]
        for col in excluded_cols:
            if col in self.sample_data.columns:
                self.assertNotIn(col, feature_cols)


class TestFeatureEngineer(unittest.TestCase):
    """Test cases for FeatureEngineer"""

    def setUp(self):
        self.engineer = FeatureEngineer()
        self.sample_data = pd.DataFrame(
            {
                "Year": [2020, 2021, 2022],
                "Annual": [1000, 1200, 950],
                "Jan-Feb": [40, 50, 35],
                "Mar-May": [100, 120, 90],
                "Jun-Sep": [600, 750, 580],
                "Oct-Dec": [160, 180, 145],
                "State Name": ["Punjab", "Punjab", "Punjab"],
                "Dist Name": ["Ludhiana", "Ludhiana", "Ludhiana"],
            }
        )

    def test_rainfall_features(self):
        """Test rainfall feature creation"""
        result = self.engineer.create_rainfall_features(self.sample_data)

        # Check that new features are created
        expected_features = [
            "Seasonal_Variability",
            "Monsoon_Intensity",
            "Pre_Monsoon_Ratio",
            "Post_Monsoon_Ratio",
        ]

        for feature in expected_features:
            self.assertIn(feature, result.columns)
            # Check that values are reasonable (not all NaN)
            self.assertFalse(result[feature].isna().all())

    def test_temporal_features(self):
        """Test temporal feature creation"""
        result = self.engineer.create_temporal_features(self.sample_data)

        # Check that temporal features are created
        expected_features = ["Year_Sin", "Year_Cos", "Decade", "Climate_Cycle"]

        for feature in expected_features:
            self.assertIn(feature, result.columns)

    def test_feature_importance(self):
        """Test feature importance calculation"""
        # Add a simple target for testing
        data_with_target = self.sample_data.copy()
        data_with_target["target"] = [3000, 3200, 2800]

        # Create some features first
        engineered_data = self.engineer.create_rainfall_features(data_with_target)

        # Select numeric features and target
        numeric_cols = engineered_data.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols if col != "target"]

        if len(feature_cols) > 0:
            X = engineered_data[feature_cols]
            y = engineered_data["target"]

            importance = self.engineer.get_feature_importance(X, y)

            # Should return importance scores for all features
            self.assertEqual(len(importance), len(feature_cols))

            # Each feature should have importance scores
            for feature, scores in importance.items():
                self.assertIn("combined", scores)
                self.assertIsInstance(scores["combined"], (int, float))


class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator"""

    def setUp(self):
        self.validator = DataValidator()
        self.good_data = pd.DataFrame(
            {
                "Year": [2020, 2021, 2022],
                "Annual": [1000, 1200, 950],
                "Jun-Sep": [600, 750, 580],
                "State Name": ["Punjab", "Punjab", "Haryana"],
                "Dist Name": ["Ludhiana", "Ludhiana", "Karnal"],
            }
        )

        self.bad_data = pd.DataFrame(
            {
                "Year": [1999, 2021, 2040],  # Invalid years
                "Annual": [1000, -100, 6000],  # Invalid rainfall
                "Jun-Sep": [600, 750, 580],
                "State Name": ["Punjab", None, "Haryana"],  # Missing state
                "Dist Name": ["Ludhiana", "Ludhiana", "Karnal"],
            }
        )

    def test_schema_validation(self):
        """Test schema validation"""
        # Good data should pass
        result = self.validator.validate_schema(self.good_data)
        self.assertTrue(result["schema_valid"])

        # Empty data should fail
        empty_data = pd.DataFrame()
        result = self.validator.validate_schema(empty_data)
        self.assertFalse(result["schema_valid"])

    def test_data_quality_validation(self):
        """Test data quality validation"""
        # Good data should have high quality score
        result = self.validator.validate_data_quality(self.good_data)
        self.assertGreater(result["quality_score"], 0.7)

        # Bad data should have lower quality score
        result = self.validator.validate_data_quality(self.bad_data)
        self.assertLess(result["quality_score"], 0.7)

    def test_business_rules_validation(self):
        """Test business rules validation"""
        # Good data should pass most rules
        result = self.validator.validate_business_rules(self.good_data)
        self.assertGreater(result["rules_passed"], result["rules_failed"])

        # Bad data should fail some rules
        result = self.validator.validate_business_rules(self.bad_data)
        self.assertGreater(result["rules_failed"], 0)

    def test_prediction_input_validation(self):
        """Test prediction input validation"""
        # Valid input
        valid_input = {"Annual": 1200, "Jun-Sep": 800, "Year": 2024}

        result = self.validator.validate_prediction_input(valid_input, "RICE")
        self.assertTrue(result["valid"])

        # Invalid input - missing required field
        invalid_input = {
            "Annual": 1200
            # Missing Jun-Sep and Year
        }

        result = self.validator.validate_prediction_input(invalid_input, "RICE")
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["issues"]), 0)


class TestConfig(unittest.TestCase):
    """Test cases for Config"""

    def setUp(self):
        self.config = Config()

    def test_supported_crops(self):
        """Test supported crops configuration"""
        self.assertIn("RICE", self.config.SUPPORTED_CROPS)
        self.assertIn("WHEAT", self.config.SUPPORTED_CROPS)
        self.assertIn("MAIZE", self.config.SUPPORTED_CROPS)

    def test_crop_validation(self):
        """Test crop validation"""
        # Valid crops should be normalized to uppercase
        self.assertEqual(self.config.validate_crop("rice"), "RICE")
        self.assertEqual(self.config.validate_crop("WHEAT"), "WHEAT")

        # Invalid crops should raise error
        with self.assertRaises(ValueError):
            self.config.validate_crop("INVALID_CROP")

    def test_target_columns(self):
        """Test target column mapping"""
        for crop in self.config.SUPPORTED_CROPS:
            target_col = self.config.get_target_column(crop)
            self.assertIsInstance(target_col, str)
            self.assertIn("YIELD", target_col.upper())

    def test_feature_columns(self):
        """Test feature column configuration"""
        rainfall_features = self.config.get_feature_columns(
            include_rainfall=True, include_temporal=False
        )
        self.assertGreater(len(rainfall_features), 0)

        temporal_features = self.config.get_feature_columns(
            include_rainfall=False, include_temporal=True
        )
        self.assertGreater(len(temporal_features), 0)


if __name__ == "__main__":
    # Create a test suite
    test_classes = [
        TestDataLoader,
        TestDataPreprocessor,
        TestFeatureEngineer,
        TestDataValidator,
        TestConfig,
    ]

    suite = unittest.TestSuite()

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
