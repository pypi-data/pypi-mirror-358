"""
Command Line Interface for Monsoon Crop Predictor
"""

import click
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys
import os

# Add the package to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.predictor import CropYieldPredictor
from ..core.data_loader import DataLoader
from ..core.validator import DataValidator
from ..utils.config import Config
from ..utils.exceptions import PredictionError, DataValidationError
from ..utils.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0", prog_name="crop-predictor")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--log-file", type=str, help="Log file path")
@click.pass_context
def cli(ctx, verbose, log_file):
    """Monsoon Crop Predictor - Advanced ML-based crop yield prediction system"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if log_file:
        setup_logging(log_file=log_file)

    if verbose:
        setup_logging(log_level="DEBUG")


@cli.command()
@click.option(
    "--crop",
    "-c",
    required=True,
    type=click.Choice(["RICE", "WHEAT", "MAIZE"], case_sensitive=False),
    help="Crop type for prediction",
)
@click.option(
    "--rainfall-data",
    "-r",
    type=click.Path(exists=True),
    help="Path to rainfall data CSV file",
)
@click.option("--annual", type=float, help="Annual rainfall in mm")
@click.option("--monsoon", type=float, help="Monsoon rainfall (Jun-Sep) in mm")
@click.option("--year", type=int, help="Year for prediction")
@click.option("--location", "-l", type=str, help="Location (State Name)")
@click.option("--output", "-o", type=click.Path(), help="Output file path (JSON/CSV)")
@click.option("--confidence", is_flag=True, help="Include confidence intervals")
@click.option("--interactive", is_flag=True, help="Interactive mode")
@click.pass_context
def predict(
    ctx,
    crop,
    rainfall_data,
    annual,
    monsoon,
    year,
    location,
    output,
    confidence,
    interactive,
):
    """Make crop yield predictions"""

    try:
        predictor = CropYieldPredictor()

        if interactive:
            result = _interactive_prediction(predictor, crop)
        elif rainfall_data:
            result = _predict_from_file(predictor, crop, rainfall_data, confidence)
        elif all([annual, monsoon, year]):
            input_data = {"Annual": annual, "Jun-Sep": monsoon, "Year": year}
            if location:
                input_data["State Name"] = location

            result = predictor.predict_single(
                input_data, crop, include_confidence=confidence
            )
        else:
            click.echo(
                "Error: Must provide either --rainfall-data file or --annual, --monsoon, --year values"
            )
            return

        # Output results
        if output:
            _save_results(result, output)
            click.echo(f"Results saved to {output}")
        else:
            _display_results(result)

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--type",
    "-t",
    "analysis_type",
    type=click.Choice(["monsoon", "trends", "patterns", "comprehensive"]),
    default="comprehensive",
    help="Type of analysis",
)
@click.option(
    "--data-file", "-d", type=click.Path(exists=True), help="Path to rainfall data file"
)
@click.option("--location", "-l", type=str, help="Location filter")
@click.option("--start-year", type=int, help="Start year for analysis")
@click.option("--end-year", type=int, help="End year for analysis")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def analyze(ctx, analysis_type, data_file, location, start_year, end_year, output):
    """Analyze monsoon patterns and rainfall trends"""

    try:
        predictor = CropYieldPredictor()
        data_loader = DataLoader()

        if data_file:
            # Load data from file
            rainfall_data = data_loader.load_csv_data(data_file)
        else:
            # Use sample data for demonstration
            click.echo("No data file provided. Using sample data for demonstration.")
            rainfall_data = _generate_sample_rainfall_data(start_year, end_year)

        # Filter years if specified
        years = None
        if start_year and end_year:
            years = list(range(start_year, end_year + 1))

        # Perform analysis
        analysis = predictor.analyze_monsoon_patterns(
            rainfall_data=rainfall_data, location=location, years=years
        )

        # Output results
        if output:
            _save_results(analysis, output)
            click.echo(f"Analysis results saved to {output}")
        else:
            _display_analysis_results(analysis)

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--annual", type=float, required=True, help="Annual rainfall in mm")
@click.option("--monsoon", type=float, required=True, help="Monsoon rainfall in mm")
@click.option("--year", type=int, required=True, help="Year for recommendation")
@click.option("--location", "-l", type=str, help="Location (State Name)")
@click.option("--crops", type=str, help="Comma-separated list of crops to consider")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def recommend(ctx, annual, monsoon, year, location, crops, output):
    """Get optimal crop recommendations"""

    try:
        predictor = CropYieldPredictor()

        input_data = {"Annual": annual, "Jun-Sep": monsoon, "Year": year}

        if location:
            input_data["State Name"] = location

        # Parse crops list
        crops_list = None
        if crops:
            crops_list = [crop.strip().upper() for crop in crops.split(",")]

        # Get recommendations
        recommendation = predictor.recommend_optimal_crop(
            input_data=input_data, crops=crops_list
        )

        # Output results
        if output:
            _save_results(recommendation, output)
            click.echo(f"Recommendations saved to {output}")
        else:
            _display_recommendation_results(recommendation)

    except Exception as e:
        logger.error(f"Recommendation failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--data-file",
    "-d",
    type=click.Path(exists=True),
    required=True,
    help="Path to data file for validation",
)
@click.option(
    "--crop",
    "-c",
    type=click.Choice(["RICE", "WHEAT", "MAIZE"], case_sensitive=False),
    help="Crop type for validation",
)
@click.option("--output", "-o", type=click.Path(), help="Output validation report path")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format",
)
@click.pass_context
def validate(ctx, data_file, crop, output, output_format):
    """Validate data files and generate quality reports"""

    try:
        data_loader = DataLoader()
        validator = DataValidator()

        # Load data
        data = data_loader.load_csv_data(data_file, validate=False)

        # Generate validation report
        report = validator.generate_validation_report(data, crop)

        # Output results
        if output:
            if output_format == "json":
                with open(output, "w") as f:
                    json.dump(report, f, indent=2, default=str)
            else:
                _save_validation_report_text(report, output)
            click.echo(f"Validation report saved to {output}")
        else:
            _display_validation_report(report)

    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--model-dir", type=click.Path(exists=True), help="Directory containing model files"
)
@click.pass_context
def info(ctx, model_dir):
    """Display information about loaded models and configuration"""

    try:
        config = Config()

        click.echo("Monsoon Crop Predictor Information")
        click.echo("=" * 40)
        click.echo(f"Version: 0.1.0")
        click.echo(f"Supported Crops: {', '.join(config.SUPPORTED_CROPS)}")
        click.echo(f"Model Directory: {model_dir or config.MODELS_DIR}")
        click.echo()

        # Check model availability
        predictor = CropYieldPredictor(model_dir=model_dir)
        click.echo("Model Status:")

        for crop in config.SUPPORTED_CROPS:
            try:
                predictor.load_model(crop)
                status = "✓ Available"
            except Exception as e:
                status = f"✗ Not available ({str(e)})"

            click.echo(f"  {crop}: {status}")

        click.echo()
        click.echo("Configuration:")
        click.echo(f"  Rainfall Features: {len(config.RAINFALL_FEATURES)}")
        click.echo(f"  Temporal Features: {len(config.TEMPORAL_FEATURES)}")

    except Exception as e:
        logger.error(f"Info command failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


def _interactive_prediction(predictor: CropYieldPredictor, crop: str) -> Dict[str, Any]:
    """Interactive prediction mode"""
    click.echo(f"Interactive prediction mode for {crop}")
    click.echo("=" * 40)

    # Collect input data
    annual = click.prompt("Annual rainfall (mm)", type=float)
    monsoon = click.prompt("Monsoon rainfall Jun-Sep (mm)", type=float)
    year = click.prompt("Year", type=int)

    location = click.prompt("State Name (optional)", default="", show_default=False)
    confidence = click.confirm("Include confidence intervals?", default=False)

    input_data = {"Annual": annual, "Jun-Sep": monsoon, "Year": year}

    if location:
        input_data["State Name"] = location

    return predictor.predict_single(input_data, crop, include_confidence=confidence)


def _predict_from_file(
    predictor: CropYieldPredictor, crop: str, file_path: str, confidence: bool
) -> List[Dict[str, Any]]:
    """Make predictions from data file"""
    data_loader = DataLoader()
    data = data_loader.load_csv_data(file_path)

    return predictor.predict_batch(
        input_data=data, crop=crop, include_confidence=confidence
    )


def _generate_sample_rainfall_data(
    start_year: Optional[int] = None, end_year: Optional[int] = None
) -> pd.DataFrame:
    """Generate sample rainfall data for demonstration"""
    import numpy as np

    start = start_year or 2000
    end = end_year or 2023

    years = list(range(start, end + 1))
    data = {
        "Year": years,
        "Annual": np.random.normal(1000, 200, len(years)),
        "Jun-Sep": np.random.normal(600, 150, len(years)),
        "Jan-Feb": np.random.normal(50, 20, len(years)),
        "Mar-May": np.random.normal(100, 30, len(years)),
        "Oct-Dec": np.random.normal(150, 50, len(years)),
    }

    return pd.DataFrame(data)


def _save_results(results: Any, output_path: str) -> None:
    """Save results to file"""
    output_path = Path(output_path)

    if output_path.suffix.lower() == ".json":
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
    elif output_path.suffix.lower() == ".csv" and isinstance(results, list):
        df = pd.DataFrame(results)
        df.to_csv(output_path, index=False)
    else:
        # Default to JSON
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)


def _display_results(result: Dict[str, Any]) -> None:
    """Display prediction results"""
    if isinstance(result, list):
        # Batch results
        click.echo(f"Batch Prediction Results ({len(result)} predictions)")
        click.echo("=" * 50)

        for i, r in enumerate(result[:5]):  # Show first 5
            click.echo(f"Prediction {i+1}:")
            click.echo(f"  Crop: {r['crop']}")
            click.echo(f"  Predicted Yield: {r['predicted_yield']:.2f} {r['unit']}")
            if "confidence_score" in r:
                click.echo(f"  Confidence: {r['confidence_score']:.2f}")
            click.echo()

        if len(result) > 5:
            click.echo(f"... and {len(result) - 5} more predictions")
    else:
        # Single result
        click.echo("Prediction Results")
        click.echo("=" * 20)
        click.echo(f"Crop: {result['crop']}")
        click.echo(f"Predicted Yield: {result['predicted_yield']:.2f} {result['unit']}")

        if "confidence_score" in result:
            click.echo(f"Confidence Score: {result['confidence_score']:.2f}")

        if "confidence_interval" in result:
            ci = result["confidence_interval"]
            click.echo(f"Confidence Interval: [{ci['lower']:.2f}, {ci['upper']:.2f}]")


def _display_analysis_results(analysis: Dict[str, Any]) -> None:
    """Display monsoon analysis results"""
    click.echo("Monsoon Analysis Results")
    click.echo("=" * 30)

    period = analysis["period"]
    click.echo(f"Analysis Period: {period['start_year']} - {period['end_year']}")

    if analysis["location"]:
        click.echo(f"Location: {analysis['location']}")

    click.echo()
    click.echo("Rainfall Statistics:")
    for season, stats in analysis["rainfall_statistics"].items():
        click.echo(f"  {season}:")
        click.echo(f"    Mean: {stats['mean']:.1f} mm")
        click.echo(f"    Std Dev: {stats['std']:.1f} mm")

    click.echo()
    patterns = analysis["monsoon_patterns"]
    if patterns:
        click.echo("Monsoon Patterns:")
        click.echo(
            f"  Average Intensity: {patterns.get('average_monsoon_intensity', 0):.2f}"
        )
        click.echo(f"  Strong Monsoon Years: {patterns.get('strong_monsoon_years', 0)}")
        click.echo(f"  Weak Monsoon Years: {patterns.get('weak_monsoon_years', 0)}")


def _display_recommendation_results(recommendation: Dict[str, Any]) -> None:
    """Display crop recommendation results"""
    click.echo("Crop Recommendation Results")
    click.echo("=" * 35)

    click.echo(f"Recommended Crop: {recommendation['recommended_crop']}")
    click.echo(f"Confidence: {recommendation['recommendation_confidence']:.2f}")
    click.echo()

    click.echo("Crop Rankings:")
    for rank_info in recommendation["ranking"]:
        click.echo(
            f"  {rank_info['rank']}. {rank_info['crop']}: {rank_info['predicted_yield']:.2f} kg/ha"
        )


def _display_validation_report(report: Dict[str, Any]) -> None:
    """Display validation report"""
    click.echo("Data Validation Report")
    click.echo("=" * 25)

    summary = report["summary"]
    click.echo(f"Overall Valid: {report['overall_assessment']['overall_valid']}")
    click.echo(f"Quality Score: {report['quality_validation']['quality_score']:.2f}")
    click.echo(f"Total Issues: {summary['total_issues']}")
    click.echo(f"Total Warnings: {summary['total_warnings']}")
    click.echo()

    if summary["all_issues"]:
        click.echo("Issues:")
        for issue in summary["all_issues"]:
            click.echo(f"  ✗ {issue}")
        click.echo()

    if summary["all_warnings"]:
        click.echo("Warnings:")
        for warning in summary["all_warnings"][:5]:  # Show first 5
            click.echo(f"  ⚠ {warning}")
        click.echo()

    click.echo(f"Recommendation: {summary['recommendation']}")


def _save_validation_report_text(report: Dict[str, Any], output_path: str) -> None:
    """Save validation report as text file"""
    with open(output_path, "w") as f:
        f.write("Data Validation Report\n")
        f.write("=" * 25 + "\n\n")

        f.write(f"Timestamp: {report['timestamp']}\n")
        f.write(
            f"Data Summary: {report['data_summary']['rows']} rows, {report['data_summary']['columns']} columns\n\n"
        )

        f.write("Overall Assessment:\n")
        for key, value in report["overall_assessment"].items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")

        summary = report["summary"]
        f.write("Summary:\n")
        f.write(f"  Total Issues: {summary['total_issues']}\n")
        f.write(f"  Total Warnings: {summary['total_warnings']}\n")
        f.write(f"  Recommendation: {summary['recommendation']}\n\n")

        if summary["all_issues"]:
            f.write("Issues:\n")
            for issue in summary["all_issues"]:
                f.write(f"  - {issue}\n")
            f.write("\n")

        if summary["all_warnings"]:
            f.write("Warnings:\n")
            for warning in summary["all_warnings"]:
                f.write(f"  - {warning}\n")


def validate_crop_input(*args, **kwargs):
    """Stub for validate_crop_input. Implement functionality as needed."""
    pass


if __name__ == "__main__":
    cli()
