# Core Concepts

Understanding the core concepts will help you use the Monsoon Crop Predictor effectively.

## Crops Supported

The package currently supports three major crops:

- **Rice**: Primary monsoon crop, grown across India
- **Wheat**: Rabi crop, affected by winter rainfall
- **Maize**: Grown in both seasons, versatile crop

## Input Features

### Required Features

- **Crop Type**: One of 'rice', 'wheat', or 'maize'
- **Location**: State and district in India
- **Rainfall**: Total rainfall in mm
- **Temperature**: Average temperature in °C
- **Humidity**: Relative humidity percentage

### Optional Features

- **Area**: Cultivation area in hectares
- **Irrigation**: Irrigation percentage (0-100)
- **Fertilizer**: Fertilizer usage in kg/hectare
- **Seeds**: Seed variety information

## Prediction Outputs

### Primary Output

- **Yield Prediction**: Expected yield in tonnes per hectare
- **Confidence**: Model confidence (0-1)
- **Risk Level**: Low, Medium, High, or Critical

### Additional Outputs

- **Feature Importance**: Which factors most influence the prediction
- **Recommendations**: Actionable advice for improving yield
- **Risk Factors**: Identified risks and mitigation strategies

## Model Architecture

### Ensemble Approach

The package uses ensemble models that combine:

- **Random Forest**: Handles non-linear relationships
- **XGBoost**: Gradient boosting for complex patterns
- **LightGBM**: Fast and efficient boosting
- **Neural Networks**: Deep learning for complex interactions

### Feature Engineering

Automatic feature engineering includes:

- **Rainfall Patterns**: Cumulative, moving averages, intensity
- **Temperature Indices**: Heat stress, growing degree days
- **Temporal Features**: Month, season, year effects
- **Interaction Features**: Combined weather effects
- **Polynomial Features**: Non-linear transformations

## Data Validation

### Input Validation

- **Range Checks**: Values within realistic bounds
- **Type Validation**: Correct data types
- **Completeness**: Required fields present
- **Consistency**: Logical relationships between features

### Quality Assurance

- **Outlier Detection**: Unusual values flagged
- **Distribution Checks**: Values follow expected patterns
- **Business Rules**: Domain-specific validations
- **Historical Comparison**: Comparison with historical data

## Uncertainty Quantification

### Confidence Metrics

- **Model Agreement**: How much models agree
- **Prediction Interval**: Range of likely values
- **Historical Accuracy**: Past performance on similar data
- **Feature Reliability**: Quality of input features

### Risk Assessment

- **Climate Risk**: Weather-related risks
- **Agricultural Risk**: Farming practice risks
- **Market Risk**: Economic factors
- **Combined Risk**: Overall risk assessment
