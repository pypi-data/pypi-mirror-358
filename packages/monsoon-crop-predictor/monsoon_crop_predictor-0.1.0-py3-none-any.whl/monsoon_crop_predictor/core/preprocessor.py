"""
Data preprocessing utilities for Monsoon Crop Predictor
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer, KNNImputer
from ..utils.config import Config
from ..utils.exceptions import DataValidationError, FeatureEngineeringError
from ..utils.logger import LoggerMixin


class Preprocessor:
    """Stub for Preprocessor. Implement functionality as needed."""

    def handle_missing_values(self, data):
        """Stub method for handling missing values."""
        return data


class DataPreprocessor(LoggerMixin):
    """
    Data preprocessing utilities for crop yield prediction
    """

    def __init__(self):
        """Initialize DataPreprocessor"""
        self.config = Config()
        self.scalers = {}
        self.imputers = {}
        self.logger.info("DataPreprocessor initialized")

    def handle_missing_values(
        self,
        data: pd.DataFrame,
        strategy: str = "mean",
        columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Handle missing values in the dataset

        Args:
            data: Input DataFrame
            strategy: Imputation strategy ('mean', 'median', 'mode', 'knn', 'forward_fill')
            columns: Specific columns to impute (if None, impute all numeric columns)

        Returns:
            DataFrame with missing values handled
        """
        self.logger.info(f"Handling missing values using strategy: {strategy}")

        data_copy = data.copy()

        # Identify columns to process
        if columns is None:
            numeric_cols = data_copy.select_dtypes(include=[np.number]).columns.tolist()
            columns = numeric_cols

        # Check for missing values
        missing_info = data_copy[columns].isnull().sum()
        cols_with_missing = missing_info[missing_info > 0]

        if cols_with_missing.empty:
            self.logger.info("No missing values found")
            return data_copy

        self.logger.info(f"Found missing values in {len(cols_with_missing)} columns")

        if strategy in ["mean", "median", "most_frequent"]:
            imputer = SimpleImputer(strategy=strategy)
            data_copy[columns] = imputer.fit_transform(data_copy[columns])
            self.imputers[strategy] = imputer

        elif strategy == "knn":
            imputer = KNNImputer(n_neighbors=5)
            data_copy[columns] = imputer.fit_transform(data_copy[columns])
            self.imputers["knn"] = imputer

        elif strategy == "forward_fill":
            data_copy[columns] = data_copy[columns].fillna(method="ffill")

        elif strategy == "interpolate":
            for col in columns:
                data_copy[col] = data_copy[col].interpolate(method="linear")

        else:
            raise DataValidationError(f"Unsupported imputation strategy: {strategy}")

        self.logger.info("Missing values handled successfully")
        return data_copy

    def clean_outliers(
        self,
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = "iqr",
        threshold: float = 1.5,
    ) -> pd.DataFrame:
        """
        Clean outliers from the dataset

        Args:
            data: Input DataFrame
            columns: Columns to process for outliers
            method: Outlier detection method ('iqr', 'zscore', 'isolation_forest')
            threshold: Threshold for outlier detection

        Returns:
            DataFrame with outliers handled
        """
        self.logger.info(f"Cleaning outliers using method: {method}")

        data_copy = data.copy()

        if columns is None:
            columns = data_copy.select_dtypes(include=[np.number]).columns.tolist()

        outliers_removed = 0

        for col in columns:
            if method == "iqr":
                Q1 = data_copy[col].quantile(0.25)
                Q3 = data_copy[col].quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR

                outliers = (data_copy[col] < lower_bound) | (
                    data_copy[col] > upper_bound
                )
                outliers_removed += outliers.sum()

                # Cap outliers instead of removing
                data_copy.loc[data_copy[col] < lower_bound, col] = lower_bound
                data_copy.loc[data_copy[col] > upper_bound, col] = upper_bound

            elif method == "zscore":
                z_scores = np.abs(
                    (data_copy[col] - data_copy[col].mean()) / data_copy[col].std()
                )
                outliers = z_scores > threshold
                outliers_removed += outliers.sum()

                # Cap outliers
                mean_val = data_copy[col].mean()
                std_val = data_copy[col].std()
                lower_bound = mean_val - threshold * std_val
                upper_bound = mean_val + threshold * std_val

                data_copy.loc[data_copy[col] < lower_bound, col] = lower_bound
                data_copy.loc[data_copy[col] > upper_bound, col] = upper_bound

        self.logger.info(f"Handled {outliers_removed} outliers")
        return data_copy

    def normalize_geographical_names(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize geographical names (states, districts) for consistency

        Args:
            data: Input DataFrame with geographical columns

        Returns:
            DataFrame with normalized geographical names
        """
        self.logger.info("Normalizing geographical names")

        data_copy = data.copy()

        # Define common geographical mappings
        state_mappings = {
            "JAMMU AND KASHMIR": "JAMMU & KASHMIR",
            "HIMACHAL PRADESH": "HIMACHAL PRADESH",
            "UTTARAKHAND": "UTTARAKHAND",
            "UTTAR PRADESH": "UTTAR PRADESH",
            "MADHYA PRADESH": "MADHYA PRADESH",
            "ANDHRA PRADESH": "ANDHRA PRADESH",
            "ARUNACHAL PRADESH": "ARUNACHAL PRADESH",
            "WEST BENGAL": "WEST BENGAL",
            "TAMIL NADU": "TAMIL NADU",
            # Add more mappings as needed
        }

        if "State Name" in data_copy.columns:
            # Clean and normalize state names
            data_copy["State Name"] = data_copy["State Name"].str.upper().str.strip()
            data_copy["State Name"] = data_copy["State Name"].replace(state_mappings)

        if "Dist Name" in data_copy.columns:
            # Clean district names
            data_copy["Dist Name"] = data_copy["Dist Name"].str.upper().str.strip()

        self.logger.info("Geographical names normalized")
        return data_copy

    def create_subdivision_mapping(
        self, rainfall_data: pd.DataFrame, crop_data: pd.DataFrame
    ) -> Dict:
        """
        Create mapping between subdivisions and state-district combinations

        Args:
            rainfall_data: DataFrame with subdivision information
            crop_data: DataFrame with state-district information

        Returns:
            Dictionary mapping subdivisions to state-district combinations
        """
        self.logger.info("Creating subdivision mapping")

        # This is a simplified mapping - in practice, you'd have a more comprehensive mapping
        subdivision_mapping = {
            "HIMACHAL PRADESH": ["HIMACHAL PRADESH"],
            "PUNJAB": ["PUNJAB"],
            "HARYANA": ["HARYANA"],
            "RAJASTHAN": ["RAJASTHAN"],
            "UTTAR PRADESH": ["UTTAR PRADESH"],
            "BIHAR": ["BIHAR"],
            "WEST BENGAL": ["WEST BENGAL"],
            "ODISHA": ["ODISHA"],
            "MADHYA PRADESH": ["MADHYA PRADESH"],
            "GUJARAT": ["GUJARAT"],
            "MAHARASHTRA": ["MAHARASHTRA"],
            "ANDHRA PRADESH": ["ANDHRA PRADESH"],
            "KARNATAKA": ["KARNATAKA"],
            "TAMIL NADU": ["TAMIL NADU"],
            "KERALA": ["KERALA"],
            # Add more comprehensive mappings
        }

        return subdivision_mapping

    def merge_rainfall_crop_data(
        self,
        rainfall_data: pd.DataFrame,
        crop_data: pd.DataFrame,
        subdivision_mapping: Optional[Dict] = None,
    ) -> pd.DataFrame:
        """
        Merge rainfall and crop data based on geographical and temporal information

        Args:
            rainfall_data: DataFrame with rainfall information
            crop_data: DataFrame with crop yield information
            subdivision_mapping: Optional mapping between subdivisions and states

        Returns:
            Merged DataFrame
        """
        self.logger.info("Merging rainfall and crop data")

        if subdivision_mapping is None:
            subdivision_mapping = self.create_subdivision_mapping(
                rainfall_data, crop_data
            )

        # Prepare rainfall data
        rainfall_prepared = rainfall_data.copy()
        if "Sub_Division" in rainfall_prepared.columns:
            rainfall_prepared["State Name"] = rainfall_prepared["Sub_Division"].map(
                lambda x: subdivision_mapping.get(x, x)
            )
            rainfall_prepared["State Name"] = rainfall_prepared["State Name"].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x
            )

        # Merge on State Name and Year
        merge_cols = ["State Name", "Year"]
        merged_data = crop_data.merge(
            rainfall_prepared, on=merge_cols, how="inner", suffixes=("", "_rainfall")
        )

        self.logger.info(f"Merged data shape: {merged_data.shape}")
        return merged_data

    def scale_features(
        self,
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        scaler_type: str = "standard",
    ) -> pd.DataFrame:
        """
        Scale numerical features

        Args:
            data: Input DataFrame
            columns: Columns to scale (if None, scale all numeric columns)
            scaler_type: Type of scaler ('standard', 'minmax', 'robust')

        Returns:
            DataFrame with scaled features
        """
        self.logger.info(f"Scaling features using {scaler_type} scaler")

        data_copy = data.copy()

        if columns is None:
            columns = data_copy.select_dtypes(include=[np.number]).columns.tolist()
            # Exclude target columns and identifiers
            exclude_cols = ["Year", "State Name", "Dist Name"] + list(
                self.config.TARGET_COLUMNS.values()
            )
            columns = [col for col in columns if col not in exclude_cols]

        if scaler_type == "standard":
            scaler = StandardScaler()
        elif scaler_type == "minmax":
            scaler = MinMaxScaler()
        else:
            raise DataValidationError(f"Unsupported scaler type: {scaler_type}")

        data_copy[columns] = scaler.fit_transform(data_copy[columns])
        self.scalers[scaler_type] = scaler

        self.logger.info(f"Scaled {len(columns)} features")
        return data_copy

    def create_temporal_splits(
        self,
        data: pd.DataFrame,
        target_col: str,
        test_size: float = 0.2,
        validation_size: float = 0.1,
    ) -> Tuple:
        """
        Create temporal train/validation/test splits

        Args:
            data: Input DataFrame
            target_col: Target column name
            test_size: Proportion of data for testing
            validation_size: Proportion of data for validation

        Returns:
            Tuple of (X_train, X_val, X_test, y_train, y_val, y_test, feature_cols)
        """
        self.logger.info("Creating temporal splits")

        # Sort by year for temporal splitting
        data_sorted = data.sort_values("Year")

        n_total = len(data_sorted)
        n_test = int(n_total * test_size)
        n_val = int(n_total * validation_size)
        n_train = n_total - n_test - n_val

        # Split data
        train_data = data_sorted.iloc[:n_train]
        val_data = data_sorted.iloc[n_train : n_train + n_val]
        test_data = data_sorted.iloc[n_train + n_val :]

        # Define feature columns
        exclude_cols = [target_col, "Year", "State Name", "Dist Name"]
        feature_cols = [col for col in data.columns if col not in exclude_cols]

        # Extract features and targets
        X_train = train_data[feature_cols]
        X_val = val_data[feature_cols]
        X_test = test_data[feature_cols]

        y_train = train_data[target_col]
        y_val = val_data[target_col]
        y_test = test_data[target_col]

        self.logger.info(
            f"Created splits - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}"
        )

        return X_train, X_val, X_test, y_train, y_val, y_test, feature_cols

    def preprocess_pipeline(
        self,
        data: pd.DataFrame,
        target_col: str,
        missing_strategy: str = "mean",
        outlier_method: str = "iqr",
        scaling_method: str = "standard",
    ) -> Tuple:
        """
        Complete preprocessing pipeline

        Args:
            data: Input DataFrame
            target_col: Target column name
            missing_strategy: Strategy for handling missing values
            outlier_method: Method for outlier detection
            scaling_method: Method for feature scaling

        Returns:
            Tuple of processed train/val/test splits
        """
        self.logger.info("Starting complete preprocessing pipeline")

        # Step 1: Normalize geographical names
        data = self.normalize_geographical_names(data)

        # Step 2: Handle missing values
        data = self.handle_missing_values(data, strategy=missing_strategy)

        # Step 3: Clean outliers
        data = self.clean_outliers(data, method=outlier_method)

        # Step 4: Create temporal splits
        splits = self.create_temporal_splits(data, target_col)
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols = splits

        # Step 5: Scale features
        if scaling_method:
            scaler = (
                StandardScaler() if scaling_method == "standard" else MinMaxScaler()
            )
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            X_test_scaled = scaler.transform(X_test)

            # Convert back to DataFrames
            X_train = pd.DataFrame(
                X_train_scaled, columns=feature_cols, index=X_train.index
            )
            X_val = pd.DataFrame(X_val_scaled, columns=feature_cols, index=X_val.index)
            X_test = pd.DataFrame(
                X_test_scaled, columns=feature_cols, index=X_test.index
            )

            self.scalers["final"] = scaler

        self.logger.info("Preprocessing pipeline completed successfully")
        return X_train, X_val, X_test, y_train, y_val, y_test, feature_cols
