"""
Feature engineering utilities for Monsoon Crop Predictor
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.preprocessing import PolynomialFeatures
from ..utils.config import Config
from ..utils.exceptions import FeatureEngineeringError
from ..utils.logger import LoggerMixin


class FeatureEngineer(LoggerMixin):
    """
    Advanced feature engineering for crop yield prediction
    """

    def __init__(self):
        """Initialize FeatureEngineer"""
        self.config = Config()
        self.feature_selectors = {}
        self.poly_features = None
        self.logger.info("FeatureEngineer initialized")

    def create_rainfall_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create advanced rainfall features

        Args:
            data: Input DataFrame with basic rainfall columns

        Returns:
            DataFrame with additional rainfall features
        """
        self.logger.info("Creating advanced rainfall features")

        data_copy = data.copy()

        # Basic rainfall columns that should exist
        rainfall_cols = ["Annual", "Jan-Feb", "Mar-May", "Jun-Sep", "Oct-Dec"]

        # Verify required columns exist
        missing_cols = [col for col in rainfall_cols if col not in data_copy.columns]
        if missing_cols:
            raise FeatureEngineeringError(f"Missing rainfall columns: {missing_cols}")

        # Seasonal variability
        seasonal_cols = ["Jan-Feb", "Mar-May", "Jun-Sep", "Oct-Dec"]
        data_copy["Seasonal_Variability"] = data_copy[seasonal_cols].std(axis=1)

        # Monsoon intensity (Jun-Sep as primary monsoon)
        data_copy["Monsoon_Intensity"] = data_copy["Jun-Sep"] / data_copy["Annual"]
        data_copy["Monsoon_Intensity"] = data_copy["Monsoon_Intensity"].fillna(0)

        # Pre and post monsoon ratios
        data_copy["Pre_Monsoon_Ratio"] = (
            data_copy["Jan-Feb"] + data_copy["Mar-May"]
        ) / data_copy["Annual"]
        data_copy["Post_Monsoon_Ratio"] = data_copy["Oct-Dec"] / data_copy["Annual"]

        # Fill NaN values with 0
        data_copy["Pre_Monsoon_Ratio"] = data_copy["Pre_Monsoon_Ratio"].fillna(0)
        data_copy["Post_Monsoon_Ratio"] = data_copy["Post_Monsoon_Ratio"].fillna(0)

        # Monsoon concentration index
        data_copy["Monsoon_Concentration"] = data_copy["Jun-Sep"] / (
            data_copy["Jun-Sep"] + data_copy["Mar-May"] + data_copy["Oct-Dec"]
        )
        data_copy["Monsoon_Concentration"] = data_copy["Monsoon_Concentration"].fillna(
            0
        )

        # Rainfall balance index
        expected_monsoon_ratio = 0.6  # Typical monsoon contribution
        data_copy["Rainfall_Balance"] = np.abs(
            data_copy["Monsoon_Intensity"] - expected_monsoon_ratio
        )

        # Drought/flood indicators
        data_copy["Drought_Risk"] = (
            data_copy["Annual"] < data_copy["Annual"].quantile(0.25)
        ).astype(int)
        data_copy["Flood_Risk"] = (
            data_copy["Annual"] > data_copy["Annual"].quantile(0.75)
        ).astype(int)

        self.logger.info("Advanced rainfall features created")
        return data_copy

    def create_temporal_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create temporal and trend features

        Args:
            data: Input DataFrame with Year column

        Returns:
            DataFrame with temporal features
        """
        self.logger.info("Creating temporal features")

        data_copy = data.copy()

        if "Year" not in data_copy.columns:
            raise FeatureEngineeringError("Year column required for temporal features")

        # Sort by geographical units and year for proper lag calculation
        sort_cols = (
            ["State Name", "Dist Name", "Year"]
            if all(col in data_copy.columns for col in ["State Name", "Dist Name"])
            else ["Year"]
        )

        data_copy = data_copy.sort_values(sort_cols)

        # Rainfall trend features
        if "Annual" in data_copy.columns:
            # Lag features for rainfall
            if len(sort_cols) > 1:  # Geographical grouping available
                data_copy["Rainfall_Lag_1"] = data_copy.groupby(
                    ["State Name", "Dist Name"]
                )["Annual"].shift(1)
                data_copy["Rainfall_Lag_2"] = data_copy.groupby(
                    ["State Name", "Dist Name"]
                )["Annual"].shift(2)

                # Rolling averages
                data_copy["Rainfall_3yr_Avg"] = (
                    data_copy.groupby(["State Name", "Dist Name"])["Annual"]
                    .rolling(window=3, min_periods=1)
                    .mean()
                    .reset_index(level=[0, 1], drop=True)
                )

                # Rainfall trend (linear slope over past 3 years)
                def calculate_trend(series):
                    if len(series) < 2:
                        return 0
                    x = np.arange(len(series))
                    slope, _, _, _, _ = stats.linregress(x, series)
                    return slope

                data_copy["Rainfall_Trend"] = (
                    data_copy.groupby(["State Name", "Dist Name"])["Annual"]
                    .rolling(window=3, min_periods=2)
                    .apply(calculate_trend, raw=False)
                    .reset_index(level=[0, 1], drop=True)
                )
            else:
                # Global lag features if no geographical grouping
                data_copy["Rainfall_Lag_1"] = data_copy["Annual"].shift(1)
                data_copy["Rainfall_Lag_2"] = data_copy["Annual"].shift(2)
                data_copy["Rainfall_3yr_Avg"] = (
                    data_copy["Annual"].rolling(window=3, min_periods=1).mean()
                )
                data_copy["Rainfall_Trend"] = (
                    0  # Cannot calculate meaningful trend without grouping
                )

        # Cyclical features for year
        data_copy["Year_Sin"] = np.sin(
            2
            * np.pi
            * (data_copy["Year"] - data_copy["Year"].min())
            / (data_copy["Year"].max() - data_copy["Year"].min())
        )
        data_copy["Year_Cos"] = np.cos(
            2
            * np.pi
            * (data_copy["Year"] - data_copy["Year"].min())
            / (data_copy["Year"].max() - data_copy["Year"].min())
        )

        # Decade indicator
        data_copy["Decade"] = (data_copy["Year"] // 10) * 10

        # Climate cycle approximation (El Niño/La Niña-like cycles)
        data_copy["Climate_Cycle"] = np.sin(
            2 * np.pi * data_copy["Year"] / 3.5
        )  # ~3.5 year cycle

        # Fill NaN values created by lag features
        lag_columns = [
            "Rainfall_Lag_1",
            "Rainfall_Lag_2",
            "Rainfall_3yr_Avg",
            "Rainfall_Trend",
        ]
        for col in lag_columns:
            if col in data_copy.columns:
                data_copy[col] = data_copy[col].fillna(data_copy[col].mean())

        self.logger.info("Temporal features created")
        return data_copy

    def create_interaction_features(
        self, data: pd.DataFrame, max_interactions: int = 10
    ) -> pd.DataFrame:
        """
        Create interaction features between important variables

        Args:
            data: Input DataFrame
            max_interactions: Maximum number of interaction features to create

        Returns:
            DataFrame with interaction features
        """
        self.logger.info("Creating interaction features")

        data_copy = data.copy()

        # Key variables for interactions
        key_vars = ["Annual", "Jun-Sep", "Monsoon_Intensity", "Rainfall_Trend"]
        available_vars = [var for var in key_vars if var in data_copy.columns]

        if len(available_vars) < 2:
            self.logger.warning("Insufficient variables for interaction features")
            return data_copy

        interactions_created = 0

        # Create pairwise interactions
        for i, var1 in enumerate(available_vars):
            for var2 in available_vars[i + 1 :]:
                if interactions_created >= max_interactions:
                    break

                # Multiplicative interaction
                interaction_name = f"{var1}_x_{var2}"
                data_copy[interaction_name] = data_copy[var1] * data_copy[var2]
                interactions_created += 1

        self.logger.info(f"Created {interactions_created} interaction features")
        return data_copy

    def create_polynomial_features(
        self, data: pd.DataFrame, columns: Optional[List[str]] = None, degree: int = 2
    ) -> pd.DataFrame:
        """
        Create polynomial features for specified columns

        Args:
            data: Input DataFrame
            columns: Columns to create polynomial features for
            degree: Polynomial degree

        Returns:
            DataFrame with polynomial features
        """
        self.logger.info(f"Creating polynomial features (degree={degree})")

        data_copy = data.copy()

        if columns is None:
            # Use key rainfall and temporal features
            columns = ["Annual", "Jun-Sep", "Monsoon_Intensity"]
            columns = [col for col in columns if col in data_copy.columns]

        if not columns:
            self.logger.warning("No suitable columns for polynomial features")
            return data_copy

        # Create polynomial features
        poly = PolynomialFeatures(
            degree=degree, include_bias=False, interaction_only=False
        )

        # Fit on selected columns
        poly_features = poly.fit_transform(data_copy[columns])

        # Get feature names
        feature_names = poly.get_feature_names_out(columns)

        # Add only the new polynomial features (exclude original features)
        original_feature_count = len(columns)
        new_features = poly_features[:, original_feature_count:]
        new_feature_names = feature_names[original_feature_count:]

        # Add to dataframe
        for i, name in enumerate(new_feature_names):
            # Clean up feature names
            clean_name = name.replace(" ", "_").replace("^", "_pow_")
            data_copy[f"poly_{clean_name}"] = new_features[:, i]

        self.poly_features = poly
        self.logger.info(f"Created {len(new_feature_names)} polynomial features")
        return data_copy

    def select_features(
        self, X: pd.DataFrame, y: pd.Series, method: str = "mutual_info", k: int = 20
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Select top k features using specified method

        Args:
            X: Feature DataFrame
            y: Target Series
            method: Selection method ('mutual_info', 'f_regression', 'correlation')
            k: Number of features to select

        Returns:
            Tuple of (selected features DataFrame, selected feature names)
        """
        self.logger.info(f"Selecting top {k} features using {method}")

        if method == "mutual_info":
            selector = SelectKBest(score_func=mutual_info_regression, k=k)
        elif method == "f_regression":
            selector = SelectKBest(score_func=f_regression, k=k)
        else:
            raise FeatureEngineeringError(
                f"Unsupported feature selection method: {method}"
            )

        # Fit selector
        X_selected = selector.fit_transform(X, y)

        # Get selected feature names
        selected_indices = selector.get_support(indices=True)
        selected_features = X.columns[selected_indices].tolist()

        # Create DataFrame with selected features
        X_selected_df = pd.DataFrame(
            X_selected, columns=selected_features, index=X.index
        )

        # Store selector for future use
        self.feature_selectors[method] = selector

        self.logger.info(f"Selected features: {selected_features}")
        return X_selected_df, selected_features

    def get_feature_importance(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Calculate feature importance using multiple methods

        Args:
            X: Feature DataFrame
            y: Target Series

        Returns:
            Dictionary mapping feature names to importance scores
        """
        self.logger.info("Calculating feature importance")

        importance_scores = {}

        # Correlation-based importance
        correlations = X.corrwith(y).abs()

        # Mutual information
        mi_scores = mutual_info_regression(X, y)

        # F-statistic
        f_scores, _ = f_regression(X, y)

        # Combine scores
        for i, feature in enumerate(X.columns):
            importance_scores[feature] = {
                "correlation": (
                    correlations.iloc[i] if not np.isnan(correlations.iloc[i]) else 0
                ),
                "mutual_info": mi_scores[i],
                "f_statistic": f_scores[i] if not np.isnan(f_scores[i]) else 0,
            }

        # Calculate combined score (weighted average)
        for feature in importance_scores:
            scores = importance_scores[feature]
            combined_score = (
                0.4 * scores["correlation"]
                + 0.4 * scores["mutual_info"]
                + 0.2 * scores["f_statistic"]
            )
            importance_scores[feature]["combined"] = combined_score

        # Sort by combined score
        sorted_features = sorted(
            importance_scores.items(), key=lambda x: x[1]["combined"], reverse=True
        )

        self.logger.info(
            f"Feature importance calculated for {len(importance_scores)} features"
        )
        return dict(sorted_features)

    def engineer_features_pipeline(
        self,
        data: pd.DataFrame,
        target_col: Optional[str] = None,
        create_interactions: bool = True,
        create_polynomials: bool = False,
        feature_selection: bool = True,
        selection_method: str = "mutual_info",
        n_features: int = 25,
    ) -> pd.DataFrame:
        """
        Complete feature engineering pipeline

        Args:
            data: Input DataFrame
            target_col: Target column for feature selection
            create_interactions: Whether to create interaction features
            create_polynomials: Whether to create polynomial features
            feature_selection: Whether to perform feature selection
            selection_method: Method for feature selection
            n_features: Number of features to select

        Returns:
            DataFrame with engineered features
        """
        self.logger.info("Starting feature engineering pipeline")

        # Step 1: Create rainfall features
        data = self.create_rainfall_features(data)

        # Step 2: Create temporal features
        data = self.create_temporal_features(data)

        # Step 3: Create interaction features
        if create_interactions:
            data = self.create_interaction_features(data)

        # Step 4: Create polynomial features
        if create_polynomials:
            data = self.create_polynomial_features(data)

        # Step 5: Feature selection
        if feature_selection and target_col and target_col in data.columns:
            # Prepare features and target
            exclude_cols = [target_col, "Year", "State Name", "Dist Name"]
            feature_cols = [col for col in data.columns if col not in exclude_cols]

            X = data[feature_cols]
            y = data[target_col]

            # Remove any non-numeric columns
            X_numeric = X.select_dtypes(include=[np.number])

            if len(X_numeric.columns) > n_features:
                X_selected, selected_features = self.select_features(
                    X_numeric, y, method=selection_method, k=n_features
                )

                # Reconstruct data with selected features
                non_feature_cols = [col for col in data.columns if col in exclude_cols]
                data = pd.concat([data[non_feature_cols], X_selected], axis=1)

        self.logger.info("Feature engineering pipeline completed")
        return data
