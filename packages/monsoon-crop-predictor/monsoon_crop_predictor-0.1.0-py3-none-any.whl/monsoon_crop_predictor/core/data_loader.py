"""
Data loading utilities for Monsoon Crop Predictor
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import requests
import json
from ..utils.config import Config
from ..utils.exceptions import DataValidationError, InsufficientDataError
from ..utils.logger import LoggerMixin


class DataLoader(LoggerMixin):
    """
    Data loading and validation utilities for crop yield prediction
    """

    def __init__(self):
        """Initialize DataLoader"""
        self.config = Config()
        self.logger.info("DataLoader initialized")

    def load_csv_data(
        self, file_path: Union[str, Path], validate: bool = True
    ) -> pd.DataFrame:
        """
        Load data from CSV file

        Args:
            file_path: Path to CSV file
            validate: Whether to validate the loaded data

        Returns:
            Loaded DataFrame

        Raises:
            FileNotFoundError: If file doesn't exist
            DataValidationError: If data validation fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        try:
            self.logger.info(f"Loading data from {file_path}")
            data = pd.read_csv(file_path)

            if validate:
                self.validate_data(data)

            self.logger.info(f"Successfully loaded {len(data)} records")
            return data

        except Exception as e:
            self.logger.error(f"Error loading data from {file_path}: {str(e)}")
            raise DataValidationError(f"Failed to load data: {str(e)}")

    def load_imd_rainfall_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load IMD rainfall data with specific preprocessing

        Args:
            file_path: Path to IMD rainfall data file

        Returns:
            Processed rainfall DataFrame
        """
        self.logger.info("Loading IMD rainfall data")
        data = self.load_csv_data(file_path, validate=False)

        # Standard IMD data preprocessing
        required_cols = [
            "SUBDIVISION",
            "YEAR",
            "ANNUAL",
            "JAN-FEB",
            "MAR-MAY",
            "JUN-SEP",
            "OCT-DEC",
        ]

        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise DataValidationError(
                f"Missing required columns in IMD data: {missing_cols}"
            )

        # Rename columns to standard format
        column_mapping = {
            "SUBDIVISION": "Sub_Division",
            "YEAR": "Year",
            "ANNUAL": "Annual",
            "JAN-FEB": "Jan-Feb",
            "MAR-MAY": "Mar-May",
            "JUN-SEP": "Jun-Sep",
            "OCT-DEC": "Oct-Dec",
        }

        data = data.rename(columns=column_mapping)

        self.logger.info(f"Successfully processed IMD rainfall data: {data.shape}")
        return data

    def load_icrisat_crop_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load ICRISAT crop yield data with specific preprocessing

        Args:
            file_path: Path to ICRISAT crop data file

        Returns:
            Processed crop DataFrame
        """
        self.logger.info("Loading ICRISAT crop data")
        data = self.load_csv_data(file_path, validate=False)

        # Standard ICRISAT data preprocessing
        required_cols = ["State Name", "Dist Name", "Year"]
        missing_cols = [col for col in required_cols if col not in data.columns]

        if missing_cols:
            raise DataValidationError(
                f"Missing required columns in ICRISAT data: {missing_cols}"
            )

        # Ensure yield columns exist for at least one crop
        yield_cols = [col for col in data.columns if "YIELD" in col.upper()]
        if not yield_cols:
            raise DataValidationError("No yield columns found in ICRISAT data")

        self.logger.info(f"Successfully processed ICRISAT crop data: {data.shape}")
        return data

    def load_enhanced_dataset(
        self, crop: str, data_dir: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load pre-processed enhanced dataset for specific crop

        Args:
            crop: Crop name (RICE, WHEAT, MAIZE)
            data_dir: Optional directory containing enhanced datasets

        Returns:
            Enhanced DataFrame for the specified crop
        """
        crop = self.config.validate_crop(crop)

        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent.parent
        else:
            data_dir = Path(data_dir)

        # Look for enhanced dataset file
        possible_files = [
            data_dir / f"{crop.lower()}_enhanced_dataset.csv",
            data_dir / f"{crop}_enhanced_dataset.csv",
            data_dir / f"{crop.title()}_enhanced_dataset.csv",
        ]

        data_file = None
        for file_path in possible_files:
            if file_path.exists():
                data_file = file_path
                break

        if data_file is None:
            raise FileNotFoundError(f"Enhanced dataset not found for {crop}")

        self.logger.info(f"Loading enhanced dataset for {crop}")
        data = self.load_csv_data(data_file)

        # Validate that the target column exists
        target_col = self.config.get_target_column(crop)
        if target_col not in data.columns:
            raise DataValidationError(
                f"Target column '{target_col}' not found in {crop} dataset"
            )

        return data

    def load_from_api(
        self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Load data from API endpoint

        Args:
            url: API endpoint URL
            params: Optional query parameters
            headers: Optional request headers

        Returns:
            DataFrame from API response
        """
        self.logger.info(f"Loading data from API: {url}")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                raise DataValidationError("Unexpected API response format")

            self.logger.info(f"Successfully loaded {len(df)} records from API")
            return df

        except requests.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise DataValidationError(f"Failed to load data from API: {str(e)}")

    def validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate loaded data against basic requirements

        Args:
            data: DataFrame to validate

        Raises:
            DataValidationError: If validation fails
        """
        if data.empty:
            raise DataValidationError("Dataset is empty")

        # Check for required columns
        required_cols = self.config.VALIDATION_RULES["required_columns"]
        missing_cols = [col for col in required_cols if col not in data.columns]

        if missing_cols:
            raise DataValidationError(f"Missing required columns: {missing_cols}")

        # Validate year range
        if "Year" in data.columns:
            min_year = self.config.VALIDATION_RULES["min_year"]
            max_year = self.config.VALIDATION_RULES["max_year"]

            invalid_years = data[(data["Year"] < min_year) | (data["Year"] > max_year)]

            if not invalid_years.empty:
                raise DataValidationError(
                    f"Invalid years found. Expected range: {min_year}-{max_year}"
                )

        # Validate rainfall values
        rainfall_cols = [
            col
            for col in data.columns
            if any(rf_col in col for rf_col in self.config.RAINFALL_FEATURES)
        ]

        for col in rainfall_cols:
            if col in data.columns:
                min_rainfall = self.config.VALIDATION_RULES["min_rainfall"]
                max_rainfall = self.config.VALIDATION_RULES["max_rainfall"]

                invalid_rainfall = data[
                    (data[col] < min_rainfall) | (data[col] > max_rainfall)
                ]

                if not invalid_rainfall.empty:
                    self.logger.warning(f"Suspicious rainfall values in column {col}")

        self.logger.info("Data validation passed")

    def get_data_summary(self, data: pd.DataFrame) -> Dict:
        """
        Get summary statistics for the loaded data

        Args:
            data: DataFrame to summarize

        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            "shape": data.shape,
            "columns": list(data.columns),
            "data_types": data.dtypes.to_dict(),
            "missing_values": data.isnull().sum().to_dict(),
            "numeric_summary": (
                data.describe().to_dict()
                if not data.select_dtypes(include=[np.number]).empty
                else {}
            ),
            "memory_usage": data.memory_usage(deep=True).sum(),
        }

        # Add date range if Year column exists
        if "Year" in data.columns:
            summary["year_range"] = {
                "min": int(data["Year"].min()),
                "max": int(data["Year"].max()),
                "unique_years": sorted(data["Year"].unique().tolist()),
            }

        return summary
