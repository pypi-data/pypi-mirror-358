# Making Predictions

This guide covers how to make predictions using the core library.

## Basic Prediction

### Single Prediction

```python
from monsoon_crop_predictor import CropPredictor

# Initialize predictor
predictor = CropPredictor()

# Make a prediction
result = predictor.predict(
    crop='rice',
    state='West Bengal',
    district='Bardhaman',
    rainfall=1200.5,
    temperature=28.3,
    humidity=75.0
)

# Access results
print(f"Predicted yield: {result.yield_prediction:.2f} tonnes/hectare")
print(f"Confidence: {result.confidence:.2f}")
print(f"Risk level: {result.risk_level}")
```

### With Additional Features

```python
result = predictor.predict(
    crop='rice',
    state='West Bengal',
    district='Bardhaman',
    rainfall=1200.5,
    temperature=28.3,
    humidity=75.0,
    area=100.0,
    irrigation=80.0,
    fertilizer_usage=150.0,
    seed_variety='IR64'
)
```

## Batch Predictions

### From Lists

```python
import pandas as pd

# Prepare data
data = [
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
    }
]

# Make batch predictions
results = predictor.batch_predict(data)

# Convert to DataFrame for analysis
df_results = pd.DataFrame([r.dict() for r in results])
print(df_results)
```

### From CSV Files

```python
# Load data from CSV
df = pd.read_csv('input_data.csv')

# Make predictions
results = predictor.batch_predict(df.to_dict('records'))

# Save results
results_df = pd.DataFrame([r.dict() for r in results])
results_df.to_csv('predictions.csv', index=False)
```

## Advanced Prediction Options

### Custom Configuration

```python
from monsoon_crop_predictor.utils.config import Config

# Custom configuration
config = Config(
    model_ensemble_weights={'random_forest': 0.4, 'xgboost': 0.6},
    confidence_threshold=0.8,
    feature_importance=True
)

predictor = CropPredictor(config=config)
```

### Feature Importance Analysis

```python
result = predictor.predict(
    crop='rice',
    state='West Bengal',
    district='Bardhaman',
    rainfall=1200.5,
    temperature=28.3,
    humidity=75.0,
    include_feature_importance=True
)

# Access feature importance
for feature, importance in result.feature_importance.items():
    print(f"{feature}: {importance:.3f}")
```

## Monsoon Analysis

### Seasonal Predictions

```python
# Analyze monsoon impact
monsoon_analysis = predictor.analyze_monsoon_impact(
    crop='rice',
    state='West Bengal',
    district='Bardhaman',
    year=2024
)

print(f"Early monsoon yield: {monsoon_analysis.early_monsoon_yield:.2f}")
print(f"Peak monsoon yield: {monsoon_analysis.peak_monsoon_yield:.2f}")
print(f"Late monsoon yield: {monsoon_analysis.late_monsoon_yield:.2f}")
```

### Climate Scenarios

```python
# Test different climate scenarios
scenarios = [
    {'rainfall': 800, 'temperature': 30, 'humidity': 70},  # Dry scenario
    {'rainfall': 1200, 'temperature': 28, 'humidity': 75}, # Normal scenario
    {'rainfall': 1600, 'temperature': 26, 'humidity': 80}  # Wet scenario
]

for i, scenario in enumerate(scenarios):
    result = predictor.predict(
        crop='rice',
        state='West Bengal',
        district='Bardhaman',
        **scenario
    )
    print(f"Scenario {i+1}: {result.yield_prediction:.2f} tonnes/hectare")
```

## Error Handling

### Validation Errors

```python
try:
    result = predictor.predict(
        crop='invalid_crop',  # This will raise an error
        state='West Bengal',
        district='Bardhaman',
        rainfall=1200.5,
        temperature=28.3,
        humidity=75.0
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Model Errors

```python
from monsoon_crop_predictor.utils.exceptions import ModelNotFoundError

try:
    result = predictor.predict(...)
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
    # Handle missing model files
```

## Performance Optimization

### Batch Processing Tips

```python
# Process large datasets in chunks
def process_large_dataset(data, chunk_size=1000):
    results = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        chunk_results = predictor.batch_predict(chunk)
        results.extend(chunk_results)
    return results
```

### Caching Results

```python
import functools

# Cache predictions for identical inputs
@functools.lru_cache(maxsize=1000)
def cached_predict(**kwargs):
    return predictor.predict(**kwargs)
```
