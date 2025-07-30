# Examples

Practical examples demonstrating how to use the Monsoon Crop Predictor package.

```{toctree}
:maxdepth: 2

basic_usage
advanced_examples
use_cases
jupyter_notebooks
```

## Quick Examples

### Simple Prediction

```python
from monsoon_crop_predictor import CropPredictor

predictor = CropPredictor()
result = predictor.predict(
    crop='rice',
    state='West Bengal',
    district='Bardhaman',
    rainfall=1200,
    temperature=28,
    humidity=75
)
print(f"Yield: {result.yield_prediction:.2f} tonnes/hectare")
```

### Batch Processing

```python
import pandas as pd

data = pd.read_csv('crop_data.csv')
results = predictor.batch_predict(data.to_dict('records'))
```

### API Usage

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"crop": "rice", "state": "West Bengal", ...}'
```

### CLI Usage

```bash
monsoon-crop predict --crop rice --state "West Bengal" --rainfall 1200
```
