# Monsoon Crop Predictor Documentation

Welcome to the Monsoon Crop Predictor documentation! This package provides advanced machine learning capabilities for predicting crop yields during monsoon seasons in India.

```{toctree}
:maxdepth: 2
:caption: Contents:

getting_started
user_guide/index
api_reference/index
examples/index
development/index
```

## Quick Start

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

print(f"Predicted yield: {result.yield_prediction:.2f} tonnes/hectare")
```

## Features

- **Multi-crop Support**: Predictions for rice, wheat, and maize
- **Advanced ML Models**: Ensemble models with 90%+ accuracy
- **Real-time API**: FastAPI-based REST API
- **CLI Interface**: Command-line tools for batch processing
- **Data Validation**: Comprehensive input validation and quality checks
- **Risk Assessment**: Climate risk analysis and recommendations

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
