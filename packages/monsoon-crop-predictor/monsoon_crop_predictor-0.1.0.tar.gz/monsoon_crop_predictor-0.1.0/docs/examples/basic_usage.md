# Basic Usage Examples

This section provides basic examples to get you started with the Monsoon Crop Predictor.

## Installation and Setup

```python
# Install the package
# pip install monsoon-crop-predictor

# Import the main predictor
from monsoon_crop_predictor import CropPredictor

# Initialize the predictor
predictor = CropPredictor()
```

## Single Predictions

### Rice Prediction

```python
# Predict rice yield in West Bengal
result = predictor.predict(
    crop='rice',
    state='West Bengal',
    district='Bardhaman',
    rainfall=1200.5,
    temperature=28.3,
    humidity=75.0
)

print(f"Predicted yield: {result.yield_prediction:.2f} tonnes/hectare")
print(f"Confidence: {result.confidence:.2f}")
print(f"Risk level: {result.risk_level}")
```

### Wheat Prediction

```python
# Predict wheat yield in Punjab
result = predictor.predict(
    crop='wheat',
    state='Punjab',
    district='Ludhiana',
    rainfall=400.2,
    temperature=22.1,
    humidity=65.0,
    area=200.0,
    irrigation=90.0
)

print(f"Predicted yield: {result.yield_prediction:.2f} tonnes/hectare")
print(f"Risk level: {result.risk_level}")
```

### Maize Prediction

```python
# Predict maize yield in Maharashtra
result = predictor.predict(
    crop='maize',
    state='Maharashtra',
    district='Pune',
    rainfall=800.7,
    temperature=25.5,
    humidity=70.0,
    fertilizer_usage=120.0
)

print(f"Predicted yield: {result.yield_prediction:.2f} tonnes/hectare")
```

## Working with Results

### Accessing Prediction Details

```python
result = predictor.predict(
    crop='rice',
    state='West Bengal',
    district='Bardhaman',
    rainfall=1200,
    temperature=28,
    humidity=75
)

# Basic prediction
print(f"Yield: {result.yield_prediction:.2f} tonnes/hectare")
print(f"Confidence: {result.confidence:.2f}")
print(f"Risk Level: {result.risk_level}")

# Prediction interval
if hasattr(result, 'prediction_interval'):
    interval = result.prediction_interval
    print(f"Range: {interval['lower']:.2f} - {interval['upper']:.2f} tonnes/hectare")

# Feature importance (if available)
if hasattr(result, 'feature_importance'):
    print("Most important factors:")
    for feature, importance in result.feature_importance.items():
        print(f"  {feature}: {importance:.3f}")
```

### Converting to Dictionary

```python
# Convert result to dictionary for further processing
result_dict = result.dict()
print(result_dict)

# Save to JSON
import json
with open('prediction_result.json', 'w') as f:
    json.dump(result_dict, f, indent=2)
```

## Batch Predictions

### From Python List

```python
# Prepare multiple predictions
predictions_data = [
    {
        'crop': 'rice',
        'state': 'West Bengal',
        'district': 'Bardhaman',
        'rainfall': 1200.5,
        'temperature': 28.3,
        'humidity': 75.0
    },
    {
        'crop': 'wheat',
        'state': 'Punjab',
        'district': 'Ludhiana',
        'rainfall': 400.2,
        'temperature': 22.1,
        'humidity': 65.0
    },
    {
        'crop': 'maize',
        'state': 'Maharashtra',
        'district': 'Pune',
        'rainfall': 800.7,
        'temperature': 25.5,
        'humidity': 70.0
    }
]

# Make batch predictions
results = predictor.batch_predict(predictions_data)

# Process results
for i, result in enumerate(results):
    data = predictions_data[i]
    print(f"{data['crop']} in {data['district']}: {result.yield_prediction:.2f} tonnes/hectare")
```

### From CSV File

```python
import pandas as pd

# Load data from CSV
df = pd.read_csv('crop_data.csv')
print("Data shape:", df.shape)
print("Columns:", df.columns.tolist())

# Convert to list of dictionaries
data_list = df.to_dict('records')

# Make predictions
results = predictor.batch_predict(data_list)

# Create results DataFrame
results_df = pd.DataFrame([r.dict() for r in results])

# Combine with original data
combined_df = pd.concat([df, results_df], axis=1)

# Save results
combined_df.to_csv('results_with_predictions.csv', index=False)
print("Results saved to results_with_predictions.csv")
```

## Error Handling

### Handling Validation Errors

```python
from monsoon_crop_predictor.utils.exceptions import ValidationError

try:
    result = predictor.predict(
        crop='invalid_crop',  # This will cause an error
        state='West Bengal',
        district='Bardhaman',
        rainfall=1200,
        temperature=28,
        humidity=75
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    print("Please check your input values.")
```

### Handling Missing Models

```python
from monsoon_crop_predictor.utils.exceptions import ModelNotFoundError

try:
    result = predictor.predict(...)
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
    print("Please check if model files are properly installed.")
```

## Configuration

### Custom Configuration

```python
from monsoon_crop_predictor.utils.config import Config

# Create custom configuration
config = Config(
    model_path='/custom/model/path',
    confidence_threshold=0.8,
    feature_importance=True
)

# Initialize predictor with custom config
predictor = CropPredictor(config=config)
```

### Environment Variables

```python
import os

# Set environment variables
os.environ['MONSOON_MODEL_PATH'] = '/path/to/models'
os.environ['MONSOON_LOG_LEVEL'] = 'DEBUG'

# These will be automatically picked up by the predictor
predictor = CropPredictor()
```

## Logging

### Enable Logging

```python
import logging
from monsoon_crop_predictor.utils.logger import setup_logging

# Setup logging
setup_logging(level='INFO')

# Now predictions will be logged
result = predictor.predict(...)
```

### Custom Logger

```python
from monsoon_crop_predictor.utils.logger import get_logger

logger = get_logger('my_app')
logger.info("Starting crop prediction...")

result = predictor.predict(...)
logger.info(f"Prediction completed: {result.yield_prediction:.2f}")
```

## Performance Tips

### Reuse Predictor Instance

```python
# Good: Reuse the predictor instance
predictor = CropPredictor()

for data in multiple_predictions:
    result = predictor.predict(**data)
    # Process result...
```

### Batch Processing for Large Datasets

```python
def process_large_dataset(data, batch_size=100):
    """Process large datasets in batches"""
    results = []

    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        batch_results = predictor.batch_predict(batch)
        results.extend(batch_results)

        # Optional: Progress reporting
        print(f"Processed {min(i+batch_size, len(data))}/{len(data)} records")

    return results

# Use for large datasets
large_data = [...] # Your large dataset
results = process_large_dataset(large_data)
```
