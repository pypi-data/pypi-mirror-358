# Getting Started

## Installation

### From PyPI (Recommended)

```bash
pip install monsoon-crop-predictor
```

### From Source

```bash
git clone https://github.com/your-username/monsoon-crop-predictor.git
cd monsoon-crop-predictor
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/your-username/monsoon-crop-predictor.git
cd monsoon-crop-predictor
pip install -e ".[dev]"
```

## Requirements

- Python 3.8+
- NumPy >= 1.21.0
- Pandas >= 1.3.0
- Scikit-learn >= 1.0.0
- FastAPI >= 0.70.0
- Click >= 8.0.0

## Quick Verification

After installation, verify everything is working:

```python
import monsoon_crop_predictor
print(monsoon_crop_predictor.__version__)
```

## Basic Usage

### Library Usage

```python
from monsoon_crop_predictor import CropPredictor

# Initialize predictor
predictor = CropPredictor()

# Single prediction
result = predictor.predict(
    crop='rice',
    state='West Bengal',
    district='Bardhaman',
    rainfall=1200.5,
    temperature=28.3,
    humidity=75.0,
    area=100.0
)

print(f"Yield: {result.yield_prediction:.2f} tonnes/hectare")
print(f"Confidence: {result.confidence:.2f}")
print(f"Risk Level: {result.risk_level}")
```

### CLI Usage

```bash
# Single prediction
monsoon-crop predict --crop rice --state "West Bengal" --district "Bardhaman" \
    --rainfall 1200.5 --temperature 28.3 --humidity 75.0

# Batch predictions from CSV
monsoon-crop batch-predict --input data.csv --output results.csv

# Interactive mode
monsoon-crop interactive
```

### API Usage

```bash
# Start the API server
monsoon-crop api --host 0.0.0.0 --port 8000

# Make predictions via HTTP
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "crop": "rice",
       "state": "West Bengal",
       "district": "Bardhaman",
       "rainfall": 1200.5,
       "temperature": 28.3,
       "humidity": 75.0
     }'
```

## Configuration

The package can be configured using environment variables or a config file:

```python
import os
os.environ['MONSOON_MODEL_PATH'] = '/path/to/your/models'
os.environ['MONSOON_LOG_LEVEL'] = 'INFO'
```

Or create a `.env` file:

```
MONSOON_MODEL_PATH=/path/to/your/models
MONSOON_LOG_LEVEL=INFO
MONSOON_API_RATE_LIMIT=100
```

## Next Steps

- Read the [User Guide](user_guide/index.md) for detailed usage instructions
- Check out [Examples](examples/index.md) for practical use cases
- Explore the [API Reference](api_reference/index.md) for complete documentation
