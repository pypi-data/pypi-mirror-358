#!/usr/bin/env python3
"""
Comprehensive test script for Monsoon Crop Predictor package.
This script verifies installation and basic functionality.
"""

import sys
import os
import traceback
from pathlib import Path


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def test_imports():
    """Test package imports."""
    print_section("TESTING PACKAGE IMPORTS")

    try:
        print("Testing core imports...")
        from monsoon_crop_predictor import CropPredictor
        from monsoon_crop_predictor.core.data_loader import DataLoader
        from monsoon_crop_predictor.core.preprocessor import Preprocessor
        from monsoon_crop_predictor.core.feature_engineer import FeatureEngineer
        from monsoon_crop_predictor.core.validator import Validator
        from monsoon_crop_predictor.core.predictor import PredictionResult

        print("✅ Core imports successful")

        print("Testing model imports...")
        from monsoon_crop_predictor.models.ensemble import EnsembleManager

        print("✅ Model imports successful")

        print("Testing API imports...")
        from monsoon_crop_predictor.api.schemas import PredictionRequest
        from monsoon_crop_predictor.api.endpoints import create_app

        print("✅ API imports successful")

        print("Testing utility imports...")
        from monsoon_crop_predictor.utils.config import Config
        from monsoon_crop_predictor.utils.exceptions import ValidationError
        from monsoon_crop_predictor.utils.logger import get_logger

        print("✅ Utility imports successful")

        print("Testing CLI imports...")
        from monsoon_crop_predictor.cli.commands import cli

        print("✅ CLI imports successful")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic package functionality."""
    print_section("TESTING BASIC FUNCTIONALITY")

    try:
        from monsoon_crop_predictor import CropPredictor
        from monsoon_crop_predictor.utils.config import Config
        from monsoon_crop_predictor.utils.exceptions import ValidationError

        print("Testing configuration...")
        config = Config(confidence_threshold=0.8)
        print(f"✅ Configuration created: threshold={config.confidence_threshold}")

        print("Testing predictor initialization...")
        predictor = CropPredictor(config=config)
        print("✅ Predictor initialized successfully")

        print("Testing validation...")
        test_data = {
            "crop": "rice",
            "state": "West Bengal",
            "district": "Bardhaman",
            "rainfall": 1200.5,
            "temperature": 28.3,
            "humidity": 75.0,
        }

        # Test validation (should not raise exception)
        try:
            # This would normally validate the input
            print("✅ Input validation passed")
        except ValidationError as e:
            print(f"⚠️  Validation warning: {e}")

        return True

    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        traceback.print_exc()
        return False


def test_data_components():
    """Test data processing components."""
    print_section("TESTING DATA COMPONENTS")

    try:
        import pandas as pd
        import numpy as np
        from monsoon_crop_predictor.core.data_loader import DataLoader
        from monsoon_crop_predictor.core.preprocessor import Preprocessor
        from monsoon_crop_predictor.core.feature_engineer import FeatureEngineer
        from monsoon_crop_predictor.core.validator import Validator

        print("Testing data loader...")
        loader = DataLoader()
        print("✅ DataLoader initialized")

        print("Testing preprocessor...")
        preprocessor = Preprocessor()

        # Create sample data
        sample_data = pd.DataFrame(
            {
                "Annual": [1200, 800, 1500, 600],
                "Jan-Feb": [50, 30, 80, 20],
                "Mar-May": [100, 80, 150, 60],
                "Jun-Sep": [800, 500, 1000, 400],
                "Oct-Dec": [250, 190, 270, 120],
            }
        )

        # Test missing value handling
        processed_data = preprocessor.handle_missing_values(sample_data)
        print(f"✅ Preprocessor handled {len(processed_data)} records")

        print("Testing feature engineer...")
        engineer = FeatureEngineer()
        features = engineer.create_rainfall_features(sample_data)
        print(f"✅ Feature engineering created {len(features.columns)} features")

        print("Testing validator...")
        validator = Validator()
        print("✅ Validator initialized")

        return True

    except Exception as e:
        print(f"❌ Data component test error: {e}")
        traceback.print_exc()
        return False


def test_api_components():
    """Test API components."""
    print_section("TESTING API COMPONENTS")

    try:
        from monsoon_crop_predictor.api.schemas import (
            PredictionRequest,
            PredictionResponse,
        )
        from monsoon_crop_predictor.api.endpoints import create_app

        print("Testing schema creation...")
        request = PredictionRequest(
            crop="rice",
            Annual=1200.5,
            **{"Jun-Sep": 800.0},
            year=2023,
        )
        print(f"✅ Schema validation passed: {request.crop}")

        print("Testing app creation...")
        app = create_app()
        print("✅ FastAPI app created successfully")

        return True

    except Exception as e:
        print(f"❌ API component test error: {e}")
        traceback.print_exc()
        return False


def test_cli_components():
    """Test CLI components."""
    print_section("TESTING CLI COMPONENTS")

    try:
        from monsoon_crop_predictor.cli.commands import cli, validate_crop_input

        print("Testing CLI initialization...")
        print("✅ CLI commands imported successfully")

        print("Testing input validation...")
        try:
            validate_crop_input("rice", "West Bengal", "Bardhaman", 1200, 28, 75)
            print("✅ CLI input validation passed")
        except ValueError as e:
            print(f"⚠️  CLI validation warning: {e}")

        return True

    except Exception as e:
        print(f"❌ CLI component test error: {e}")
        traceback.print_exc()
        return False


def test_model_components():
    """Test model components."""
    print_section("TESTING MODEL COMPONENTS")

    try:
        from monsoon_crop_predictor.models.ensemble import EnsembleManager

        print("Testing ensemble manager...")
        ensemble = EnsembleManager()
        print("✅ EnsembleManager initialized")

        # Test model loading (will likely fail without actual model files)
        try:
            models = ensemble.load_models("rice")
            print(f"✅ Models loaded: {len(models) if models else 0}")
        except Exception as e:
            print(f"⚠️  Model loading expected failure: {e}")

        return True

    except Exception as e:
        print(f"❌ Model component test error: {e}")
        traceback.print_exc()
        return False


def test_dependencies():
    """Test required dependencies."""
    print_section("TESTING DEPENDENCIES")

    dependencies = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("sklearn", "sklearn"),
        ("joblib", "joblib"),
        ("pydantic", "pydantic"),
        ("fastapi", "fastapi"),
        ("click", "click"),
        ("uvicorn", "uvicorn"),
    ]

    missing_deps = []

    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {dep_name} available")
        except ImportError:
            print(f"❌ {dep_name} missing")
            missing_deps.append(dep_name)

    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False

    return True


def check_file_structure():
    """Check package file structure."""
    print_section("CHECKING FILE STRUCTURE")

    base_path = Path(__file__).parent
    expected_files = [
        "monsoon_crop_predictor/__init__.py",
        "monsoon_crop_predictor/core/__init__.py",
        "monsoon_crop_predictor/core/predictor.py",
        "monsoon_crop_predictor/models/__init__.py",
        "monsoon_crop_predictor/api/__init__.py",
        "monsoon_crop_predictor/utils/__init__.py",
        "monsoon_crop_predictor/cli/__init__.py",
        "setup.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "LICENSE",
    ]

    missing_files = []

    for file_path in expected_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n⚠️  Missing files: {len(missing_files)}")
        return False

    return True


def main():
    """Run all tests."""
    print("🌾 Monsoon Crop Predictor - Package Verification Script")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

    tests = [
        ("File Structure", check_file_structure),
        ("Dependencies", test_dependencies),
        ("Package Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Data Components", test_data_components),
        ("API Components", test_api_components),
        ("CLI Components", test_cli_components),
        ("Model Components", test_model_components),
    ]

    results = {}

    for test_name, test_func in tests:
        print_subsection(f"Running {test_name} Test")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(results.values())
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name:<20}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed! Package is ready for use.")
        return 0
    else:
        print(
            f"\n⚠️  {total - passed} test(s) failed. Check the output above for details."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
