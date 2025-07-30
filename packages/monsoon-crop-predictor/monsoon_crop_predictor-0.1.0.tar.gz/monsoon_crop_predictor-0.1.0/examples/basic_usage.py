"""
Basic Usage Example for Monsoon Crop Predictor

This example demonstrates the basic functionality of the crop yield prediction system.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add the package to path (for development use)
sys.path.insert(0, str(Path(__file__).parent.parent))

from monsoon_crop_predictor import CropYieldPredictor
from monsoon_crop_predictor.core.data_loader import DataLoader
from monsoon_crop_predictor.core.validator import DataValidator


def create_sample_data():
    """Create sample rainfall data for demonstration"""
    print("Creating sample rainfall data...")

    # Generate realistic sample data
    np.random.seed(42)
    n_samples = 100

    data = {
        "Year": np.random.randint(2010, 2024, n_samples),
        "Annual": np.random.normal(1000, 200, n_samples),
        "Jun-Sep": np.random.normal(600, 150, n_samples),
        "Jan-Feb": np.random.normal(50, 20, n_samples),
        "Mar-May": np.random.normal(100, 30, n_samples),
        "Oct-Dec": np.random.normal(150, 50, n_samples),
        "State Name": np.random.choice(["Punjab", "Haryana", "UP", "Bihar"], n_samples),
        "Dist Name": np.random.choice(
            ["District1", "District2", "District3"], n_samples
        ),
    }

    # Ensure positive rainfall values
    for col in ["Annual", "Jun-Sep", "Jan-Feb", "Mar-May", "Oct-Dec"]:
        data[col] = np.maximum(data[col], 0)

    df = pd.DataFrame(data)
    return df


def main():
    """Main demonstration function"""
    print("Monsoon Crop Predictor - Basic Usage Example")
    print("=" * 50)

    try:
        # 1. Initialize the predictor
        print("\n1. Initializing CropYieldPredictor...")
        predictor = CropYieldPredictor()
        print("✓ Predictor initialized successfully")

        # 2. Single prediction example
        print("\n2. Making a single prediction...")

        input_data = {
            "Annual": 1200,
            "Jun-Sep": 800,
            "Year": 2024,
            "Jan-Feb": 45,
            "Mar-May": 120,
            "Oct-Dec": 235,
            "State Name": "Punjab",
        }

        try:
            result = predictor.predict_single(
                input_data=input_data,
                crop="RICE",
                include_confidence=True,
                validate_input=True,
            )

            print(f"✓ Prediction successful!")
            print(f"  Crop: {result['crop']}")
            print(
                f"  Predicted Yield: {result['predicted_yield']:.2f} {result['unit']}"
            )

            if "confidence_score" in result:
                print(f"  Confidence Score: {result['confidence_score']:.2f}")

            if "confidence_interval" in result:
                ci = result["confidence_interval"]
                print(
                    f"  95% Confidence Interval: [{ci['lower']:.2f}, {ci['upper']:.2f}]"
                )

        except Exception as e:
            print(f"✗ Single prediction failed: {str(e)}")
            print("Note: This might be expected if model files are not available")

        # 3. Batch prediction example
        print("\n3. Creating sample data for batch prediction...")
        sample_data = create_sample_data()
        print(f"✓ Created sample dataset with {len(sample_data)} records")

        # 4. Data validation example
        print("\n4. Validating sample data...")
        validator = DataValidator()

        validation_report = validator.generate_validation_report(sample_data)

        print(f"✓ Validation completed")
        print(
            f"  Overall Valid: {validation_report['overall_assessment']['overall_valid']}"
        )
        print(
            f"  Quality Score: {validation_report['quality_validation']['quality_score']:.2f}"
        )
        print(f"  Issues Found: {validation_report['summary']['total_issues']}")
        print(f"  Warnings: {validation_report['summary']['total_warnings']}")

        # 5. Monsoon analysis example
        print("\n5. Analyzing monsoon patterns...")

        try:
            analysis = predictor.analyze_monsoon_patterns(
                rainfall_data=sample_data, location="Punjab"
            )

            print(f"✓ Monsoon analysis completed")
            print(
                f"  Analysis Period: {analysis['period']['start_year']} - {analysis['period']['end_year']}"
            )
            print(f"  Location: {analysis['location']}")

            if "rainfall_statistics" in analysis:
                annual_stats = analysis["rainfall_statistics"].get("Annual", {})
                if annual_stats:
                    print(
                        f"  Average Annual Rainfall: {annual_stats.get('mean', 0):.1f} mm"
                    )

        except Exception as e:
            print(f"✗ Monsoon analysis failed: {str(e)}")

        # 6. Crop recommendation example
        print("\n6. Getting crop recommendations...")

        try:
            recommendation = predictor.recommend_optimal_crop(input_data=input_data)

            print(f"✓ Crop recommendation completed")
            print(f"  Recommended Crop: {recommendation['recommended_crop']}")
            print(f"  Confidence: {recommendation['recommendation_confidence']:.2f}")

            print("  Ranking:")
            for rank_info in recommendation["ranking"][:3]:  # Top 3
                print(
                    f"    {rank_info['rank']}. {rank_info['crop']}: {rank_info['predicted_yield']:.2f} kg/ha"
                )

        except Exception as e:
            print(f"✗ Crop recommendation failed: {str(e)}")

        # 7. Risk assessment example
        print("\n7. Assessing agricultural risk...")

        try:
            risk_assessment = predictor.assess_agricultural_risk(
                input_data=input_data, crop="RICE"
            )

            print(f"✓ Risk assessment completed")
            print(f"  Risk Level: {risk_assessment['risk_level']}")
            print(
                f"  Overall Risk Score: {risk_assessment['risk_factors']['overall_risk']:.2f}"
            )
            print(f"  Confidence: {risk_assessment['confidence']:.2f}")

            if risk_assessment["recommendations"]:
                print("  Recommendations:")
                for rec in risk_assessment["recommendations"][:2]:  # Top 2
                    print(f"    • {rec}")

        except Exception as e:
            print(f"✗ Risk assessment failed: {str(e)}")

        print("\n" + "=" * 50)
        print("Example completed successfully!")
        print("\nNote: Some functions may fail if trained models are not available.")
        print("This is expected during development and testing.")

    except Exception as e:
        print(f"\nExample failed with error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
