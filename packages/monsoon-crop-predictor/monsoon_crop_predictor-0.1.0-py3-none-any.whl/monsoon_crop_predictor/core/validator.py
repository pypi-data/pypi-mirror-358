"""
Data validation utilities for Monsoon Crop Predictor
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings
from ..utils.config import Config
from ..utils.exceptions import DataValidationError
from ..utils.logger import LoggerMixin


class DataValidator(LoggerMixin):
    """
    Comprehensive data validation for crop yield prediction
    """

    def __init__(self):
        """Initialize DataValidator"""
        self.config = Config()
        self.validation_report = {}
        self.logger.info("DataValidator initialized")

    def validate_schema(
        self, data: pd.DataFrame, required_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate DataFrame schema and structure

        Args:
            data: Input DataFrame to validate
            required_columns: List of required column names

        Returns:
            Dictionary containing validation results
        """
        self.logger.info("Validating data schema")

        if required_columns is None:
            required_columns = self.config.VALIDATION_RULES["required_columns"]

        validation_results = {
            "schema_valid": True,
            "issues": [],
            "warnings": [],
            "stats": {
                "total_rows": len(data),
                "total_columns": len(data.columns),
                "empty_rows": data.isnull().all(axis=1).sum(),
                "duplicate_rows": data.duplicated().sum(),
            },
        }

        # Check if DataFrame is empty
        if data.empty:
            validation_results["schema_valid"] = False
            validation_results["issues"].append("DataFrame is empty")
            return validation_results

        # Check for required columns
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            validation_results["schema_valid"] = False
            validation_results["issues"].append(
                f"Missing required columns: {missing_columns}"
            )

        # Check for duplicate columns
        duplicate_columns = data.columns[data.columns.duplicated()].tolist()
        if duplicate_columns:
            validation_results["warnings"].append(
                f"Duplicate column names: {duplicate_columns}"
            )

        # Check for empty columns
        empty_columns = data.columns[data.isnull().all()].tolist()
        if empty_columns:
            validation_results["warnings"].append(
                f"Completely empty columns: {empty_columns}"
            )

        # Check data types
        numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        object_columns = data.select_dtypes(include=[object]).columns.tolist()

        validation_results["stats"].update(
            {
                "numeric_columns": len(numeric_columns),
                "object_columns": len(object_columns),
                "numeric_column_names": numeric_columns,
                "object_column_names": object_columns,
            }
        )

        self.logger.info(
            f"Schema validation completed. Valid: {validation_results['schema_valid']}"
        )
        return validation_results

    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality issues

        Args:
            data: Input DataFrame to validate

        Returns:
            Dictionary containing data quality results
        """
        self.logger.info("Validating data quality")

        quality_results = {
            "quality_score": 0.0,
            "issues": [],
            "warnings": [],
            "missing_data": {},
            "outliers": {},
            "data_types": {},
        }

        # Missing data analysis
        missing_counts = data.isnull().sum()
        missing_percentages = (missing_counts / len(data)) * 100

        for col in data.columns:
            missing_pct = missing_percentages[col]
            quality_results["missing_data"][col] = {
                "count": int(missing_counts[col]),
                "percentage": float(missing_pct),
            }

            if missing_pct > 50:
                quality_results["issues"].append(
                    f"Column '{col}' has {missing_pct:.1f}% missing values"
                )
            elif missing_pct > 20:
                quality_results["warnings"].append(
                    f"Column '{col}' has {missing_pct:.1f}% missing values"
                )

        # Outlier detection for numeric columns
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            if col in data.columns:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = ((data[col] < lower_bound) | (data[col] > upper_bound)).sum()
                outlier_percentage = (outliers / len(data)) * 100

                quality_results["outliers"][col] = {
                    "count": int(outliers),
                    "percentage": float(outlier_percentage),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                }

                if outlier_percentage > 10:
                    quality_results["warnings"].append(
                        f"Column '{col}' has {outlier_percentage:.1f}% outliers"
                    )

        # Data type validation
        for col in data.columns:
            dtype = str(data[col].dtype)
            quality_results["data_types"][col] = dtype

            # Check if numeric columns have any string values
            if dtype in ["object", "string"]:
                if col in ["Year"] or any(
                    kw in col.lower() for kw in ["rainfall", "yield", "annual"]
                ):
                    try:
                        pd.to_numeric(data[col], errors="raise")
                    except:
                        quality_results["issues"].append(
                            f"Column '{col}' should be numeric but contains non-numeric values"
                        )

        # Calculate quality score
        issues_penalty = len(quality_results["issues"]) * 0.2
        warnings_penalty = len(quality_results["warnings"]) * 0.1
        missing_penalty = (
            np.mean(
                [
                    info["percentage"]
                    for info in quality_results["missing_data"].values()
                ]
            )
            / 100
        )

        quality_score = max(
            0.0, 1.0 - issues_penalty - warnings_penalty - missing_penalty
        )
        quality_results["quality_score"] = quality_score

        self.logger.info(
            f"Data quality validation completed. Score: {quality_score:.2f}"
        )
        return quality_results

    def validate_business_rules(
        self, data: pd.DataFrame, crop: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate business logic and domain-specific rules

        Args:
            data: Input DataFrame to validate
            crop: Crop type for specific validations

        Returns:
            Dictionary containing business rule validation results
        """
        self.logger.info("Validating business rules")

        business_results = {
            "rules_passed": 0,
            "rules_failed": 0,
            "issues": [],
            "warnings": [],
        }

        # Year validation
        if "Year" in data.columns:
            min_year = self.config.VALIDATION_RULES["min_year"]
            max_year = self.config.VALIDATION_RULES["max_year"]

            invalid_years = data[(data["Year"] < min_year) | (data["Year"] > max_year)]
            if not invalid_years.empty:
                business_results["rules_failed"] += 1
                business_results["issues"].append(
                    f"Found {len(invalid_years)} records with years outside valid range ({min_year}-{max_year})"
                )
            else:
                business_results["rules_passed"] += 1

        # Rainfall validation
        rainfall_columns = [
            col
            for col in data.columns
            if any(
                rf in col
                for rf in ["Annual", "Jan-Feb", "Mar-May", "Jun-Sep", "Oct-Dec"]
            )
        ]

        for col in rainfall_columns:
            min_rainfall = self.config.VALIDATION_RULES["min_rainfall"]
            max_rainfall = self.config.VALIDATION_RULES["max_rainfall"]

            invalid_rainfall = data[
                (data[col] < min_rainfall) | (data[col] > max_rainfall)
            ]
            if not invalid_rainfall.empty:
                business_results["rules_failed"] += 1
                business_results["warnings"].append(
                    f"Column '{col}': {len(invalid_rainfall)} values outside expected range ({min_rainfall}-{max_rainfall}mm)"
                )
            else:
                business_results["rules_passed"] += 1

        # Yield validation (if crop is specified)
        if crop:
            target_col = self.config.get_target_column(crop)
            if target_col in data.columns:
                # Typical yield ranges (kg/ha)
                yield_ranges = {
                    "RICE": (500, 8000),
                    "WHEAT": (500, 6000),
                    "MAIZE": (1000, 12000),
                }

                if crop in yield_ranges:
                    min_yield, max_yield = yield_ranges[crop]
                    invalid_yields = data[
                        (data[target_col] < min_yield) | (data[target_col] > max_yield)
                    ]

                    if not invalid_yields.empty:
                        business_results["rules_failed"] += 1
                        business_results["warnings"].append(
                            f"Found {len(invalid_yields)} {crop} yield values outside typical range ({min_yield}-{max_yield} kg/ha)"
                        )
                    else:
                        business_results["rules_passed"] += 1

        # Seasonal rainfall consistency
        seasonal_cols = ["Jan-Feb", "Mar-May", "Jun-Sep", "Oct-Dec"]
        if (
            all(col in data.columns for col in seasonal_cols)
            and "Annual" in data.columns
        ):
            seasonal_sum = data[seasonal_cols].sum(axis=1)
            annual_values = data["Annual"]

            # Allow 10% tolerance for rounding errors
            inconsistent = np.abs(seasonal_sum - annual_values) > (annual_values * 0.1)
            if inconsistent.sum() > 0:
                business_results["rules_failed"] += 1
                business_results["warnings"].append(
                    f"Found {inconsistent.sum()} records where seasonal rainfall doesn't sum to annual rainfall"
                )
            else:
                business_results["rules_passed"] += 1

        # Geographical consistency
        if all(col in data.columns for col in ["State Name", "Dist Name"]):
            # Check for valid state-district combinations
            state_district_pairs = data[["State Name", "Dist Name"]].drop_duplicates()

            # Basic consistency check - no null values in geographical columns
            null_geo = data[["State Name", "Dist Name"]].isnull().any(axis=1).sum()
            if null_geo > 0:
                business_results["rules_failed"] += 1
                business_results["issues"].append(
                    f"Found {null_geo} records with missing geographical information"
                )
            else:
                business_results["rules_passed"] += 1

        self.logger.info(
            f"Business rules validation completed. "
            f"Passed: {business_results['rules_passed']}, Failed: {business_results['rules_failed']}"
        )
        return business_results

    def validate_prediction_input(
        self, input_data: Dict[str, Any], crop: str
    ) -> Dict[str, Any]:
        """
        Validate input data for prediction requests

        Args:
            input_data: Dictionary containing prediction input
            crop: Crop type for prediction

        Returns:
            Dictionary containing validation results
        """
        self.logger.info(f"Validating prediction input for {crop}")

        validation_results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "processed_data": {},
        }

        # Validate crop
        try:
            crop = self.config.validate_crop(crop)
        except ValueError as e:
            validation_results["valid"] = False
            validation_results["issues"].append(str(e))
            return validation_results

        # Required fields for prediction
        required_fields = ["Annual", "Jun-Sep", "Year"]
        optional_fields = ["Jan-Feb", "Mar-May", "Oct-Dec", "State Name", "Dist Name"]

        # Check required fields
        for field in required_fields:
            if field not in input_data:
                validation_results["valid"] = False
                validation_results["issues"].append(f"Missing required field: {field}")
            else:
                # Validate data types and ranges
                value = input_data[field]

                if field == "Year":
                    if (
                        not isinstance(value, (int, float))
                        or value < 2000
                        or value > 2030
                    ):
                        validation_results["valid"] = False
                        validation_results["issues"].append(f"Invalid year: {value}")

                elif field in ["Annual", "Jun-Sep"]:
                    if not isinstance(value, (int, float)) or value < 0 or value > 5000:
                        validation_results["valid"] = False
                        validation_results["issues"].append(
                            f"Invalid rainfall value for {field}: {value}"
                        )

        # Process and validate optional fields
        for field in optional_fields:
            if field in input_data:
                value = input_data[field]

                if field in ["Jan-Feb", "Mar-May", "Oct-Dec"]:
                    if not isinstance(value, (int, float)) or value < 0 or value > 2000:
                        validation_results["warnings"].append(
                            f"Suspicious rainfall value for {field}: {value}"
                        )

                validation_results["processed_data"][field] = value

        # Copy required fields to processed data
        for field in required_fields:
            if field in input_data:
                validation_results["processed_data"][field] = input_data[field]

        self.logger.info(
            f"Prediction input validation completed. Valid: {validation_results['valid']}"
        )
        return validation_results

    def generate_validation_report(
        self, data: pd.DataFrame, crop: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive validation report

        Args:
            data: DataFrame to validate
            crop: Optional crop type for specific validations

        Returns:
            Complete validation report
        """
        self.logger.info("Generating comprehensive validation report")

        # Run all validations
        schema_results = self.validate_schema(data)
        quality_results = self.validate_data_quality(data)
        business_results = self.validate_business_rules(data, crop)

        # Compile comprehensive report
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "data_summary": {
                "rows": len(data),
                "columns": len(data.columns),
                "crop": crop,
            },
            "schema_validation": schema_results,
            "quality_validation": quality_results,
            "business_validation": business_results,
            "overall_assessment": {
                "schema_valid": schema_results["schema_valid"],
                "quality_score": quality_results["quality_score"],
                "business_rules_passed": business_results["rules_passed"],
                "business_rules_failed": business_results["rules_failed"],
            },
        }

        # Calculate overall validity
        overall_valid = (
            schema_results["schema_valid"]
            and quality_results["quality_score"] >= 0.7
            and business_results["rules_failed"] == 0
        )

        report["overall_assessment"]["overall_valid"] = overall_valid

        # Aggregate all issues and warnings
        all_issues = (
            schema_results["issues"]
            + quality_results["issues"]
            + business_results["issues"]
        )

        all_warnings = (
            schema_results["warnings"]
            + quality_results["warnings"]
            + business_results["warnings"]
        )

        report["summary"] = {
            "total_issues": len(all_issues),
            "total_warnings": len(all_warnings),
            "all_issues": all_issues,
            "all_warnings": all_warnings,
            "recommendation": self._get_recommendation(report),
        }

        self.validation_report = report
        self.logger.info("Validation report generated successfully")
        return report

    def _get_recommendation(self, report: Dict[str, Any]) -> str:
        """
        Generate recommendation based on validation results

        Args:
            report: Validation report

        Returns:
            Recommendation string
        """
        if report["overall_assessment"]["overall_valid"]:
            return "Data is suitable for model training and prediction."

        issues = report["summary"]["total_issues"]
        warnings = report["summary"]["total_warnings"]
        quality_score = report["quality_validation"]["quality_score"]

        if issues > 0:
            return (
                f"Data has {issues} critical issues that must be resolved before use."
            )
        elif quality_score < 0.5:
            return "Data quality is poor. Consider data cleaning and preprocessing."
        elif warnings > 5:
            return f"Data has {warnings} warnings. Review and address before production use."
        else:
            return "Data is acceptable but consider addressing warnings for optimal results."


class Validator:
    """Stub for Validator. Implement functionality as needed."""

    pass
