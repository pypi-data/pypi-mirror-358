# Utilities API Reference

## monsoon_crop_predictor.utils

### Configuration

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.utils.config.Config
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.utils.config.get_config
```

### Exceptions

```{eval-rst}
.. autoexception:: monsoon_crop_predictor.utils.exceptions.MonsoonCropPredictorError
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: monsoon_crop_predictor.utils.exceptions.ValidationError
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: monsoon_crop_predictor.utils.exceptions.DataError
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: monsoon_crop_predictor.utils.exceptions.ModelError
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: monsoon_crop_predictor.utils.exceptions.ModelNotFoundError
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: monsoon_crop_predictor.utils.exceptions.PredictionError
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoexception:: monsoon_crop_predictor.utils.exceptions.APIError
   :members:
   :undoc-members:
   :show-inheritance:
```

### Logging

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.utils.logger.get_logger
```

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.utils.logger.setup_logging
```

## Constants

### Supported Values

#### Crops

```python
SUPPORTED_CROPS = ['rice', 'wheat', 'maize']
```

#### States and Districts

```python
INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
]
```

### Feature Ranges

#### Rainfall (mm)

- Minimum: 0
- Maximum: 5000
- Typical: 400-2000

#### Temperature (°C)

- Minimum: 5
- Maximum: 50
- Typical: 15-35

#### Humidity (%)

- Minimum: 10
- Maximum: 100
- Typical: 40-90

### Model Parameters

#### Ensemble Weights

```python
DEFAULT_ENSEMBLE_WEIGHTS = {
    'random_forest': 0.25,
    'xgboost': 0.30,
    'lightgbm': 0.25,
    'neural_network': 0.20
}
```

#### Confidence Thresholds

```python
CONFIDENCE_THRESHOLDS = {
    'high': 0.8,
    'medium': 0.6,
    'low': 0.4
}
```

#### Risk Levels

```python
RISK_LEVELS = {
    'Low': 0.2,
    'Medium': 0.5,
    'High': 0.8,
    'Critical': 1.0
}
```
