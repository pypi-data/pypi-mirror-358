# API Usage

The Monsoon Crop Predictor provides a RESTful API built with FastAPI for integration with web applications and microservices.

## Starting the API Server

### Command Line

```bash
# Start with default settings
monsoon-crop api

# Custom host and port
monsoon-crop api --host 0.0.0.0 --port 8080

# Development mode with auto-reload
monsoon-crop api --reload --debug
```

### Programmatically

```python
from monsoon_crop_predictor.api import create_app
import uvicorn

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Single Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "crop": "rice",
       "state": "West Bengal",
       "district": "Bardhaman",
       "rainfall": 1200.5,
       "temperature": 28.3,
       "humidity": 75.0,
       "area": 100.0
     }'
```

Response:

```json
{
  "yield_prediction": 4.25,
  "confidence": 0.87,
  "risk_level": "Low",
  "prediction_interval": {
    "lower": 3.85,
    "upper": 4.65
  },
  "feature_importance": {
    "rainfall": 0.35,
    "temperature": 0.28,
    "humidity": 0.22,
    "location": 0.15
  }
}
```

### Batch Predictions

```bash
curl -X POST "http://localhost:8000/batch-predict" \
     -H "Content-Type: application/json" \
     -d '{
       "predictions": [
         {
           "crop": "rice",
           "state": "West Bengal",
           "district": "Bardhaman",
           "rainfall": 1200.5,
           "temperature": 28.3,
           "humidity": 75.0
         },
         {
           "crop": "wheat",
           "state": "Punjab",
           "district": "Ludhiana",
           "rainfall": 400.2,
           "temperature": 22.1,
           "humidity": 65.0
         }
       ]
     }'
```

### Monsoon Analysis

```bash
curl -X POST "http://localhost:8000/analyze-monsoon" \
     -H "Content-Type: application/json" \
     -d '{
       "crop": "rice",
       "state": "West Bengal",
       "district": "Bardhaman",
       "year": 2024
     }'
```

Response:

```json
{
  "crop": "rice",
  "location": {
    "state": "West Bengal",
    "district": "Bardhaman"
  },
  "year": 2024,
  "monsoon_phases": {
    "pre_monsoon": {
      "yield_prediction": 3.2,
      "risk_level": "Medium"
    },
    "peak_monsoon": {
      "yield_prediction": 4.5,
      "risk_level": "Low"
    },
    "post_monsoon": {
      "yield_prediction": 3.8,
      "risk_level": "Low"
    }
  },
  "recommendations": [
    "Ensure adequate drainage during peak monsoon",
    "Consider early variety for pre-monsoon planting"
  ]
}
```

### Recommendations

```bash
curl -X POST "http://localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{
       "crop": "rice",
       "state": "West Bengal",
       "district": "Bardhaman",
       "current_conditions": {
         "rainfall": 1200.5,
         "temperature": 28.3,
         "humidity": 75.0
       },
       "farming_practices": {
         "irrigation": 80.0,
         "fertilizer_usage": 150.0
       }
     }'
```

### Risk Assessment

```bash
curl -X POST "http://localhost:8000/assess-risk" \
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

## Python Client

### Using requests

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def predict_yield(crop_data):
    response = requests.post(
        f"{BASE_URL}/predict",
        json=crop_data,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# Example usage
data = {
    "crop": "rice",
    "state": "West Bengal",
    "district": "Bardhaman",
    "rainfall": 1200.5,
    "temperature": 28.3,
    "humidity": 75.0
}

result = predict_yield(data)
print(f"Predicted yield: {result['yield_prediction']}")
```

### Custom Client Class

```python
class MonsoonCropClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def predict(self, **kwargs):
        response = requests.post(
            f"{self.base_url}/predict",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    def batch_predict(self, predictions):
        response = requests.post(
            f"{self.base_url}/batch-predict",
            json={"predictions": predictions}
        )
        response.raise_for_status()
        return response.json()

    def analyze_monsoon(self, crop, state, district, year):
        response = requests.post(
            f"{self.base_url}/analyze-monsoon",
            json={
                "crop": crop,
                "state": state,
                "district": district,
                "year": year
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
client = MonsoonCropClient()
result = client.predict(
    crop="rice",
    state="West Bengal",
    district="Bardhaman",
    rainfall=1200.5,
    temperature=28.3,
    humidity=75.0
)
```

## Authentication and Security

### API Key Authentication

```python
# If API key authentication is enabled
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key"
}

response = requests.post(
    "http://localhost:8000/predict",
    json=data,
    headers=headers
)
```

### Rate Limiting

The API includes rate limiting to prevent abuse:

- Default: 100 requests per minute per IP
- Configurable via environment variables
- Returns HTTP 429 when limit exceeded

### CORS Configuration

For web applications, CORS is configured to allow:

- All origins in development mode
- Configurable origins in production
- Standard HTTP methods (GET, POST, PUT, DELETE)

## Error Handling

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request (validation error)
- `404`: Not Found (invalid endpoint)
- `422`: Unprocessable Entity (invalid data)
- `429`: Too Many Requests (rate limit)
- `500`: Internal Server Error

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid crop type",
    "details": {
      "field": "crop",
      "allowed_values": ["rice", "wheat", "maize"]
    }
  }
}
```

## Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["monsoon-crop", "api", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: "3.8"
services:
  monsoon-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONSOON_LOG_LEVEL=INFO
      - MONSOON_API_RATE_LIMIT=200
    volumes:
      - ./models:/app/models
```

### Environment Variables

```bash
# Model configuration
MONSOON_MODEL_PATH=/path/to/models
MONSOON_MODEL_CACHE_SIZE=100

# API configuration
MONSOON_API_HOST=0.0.0.0
MONSOON_API_PORT=8000
MONSOON_API_RATE_LIMIT=100
MONSOON_API_CORS_ORIGINS=http://localhost:3000,https://yourapp.com

# Logging
MONSOON_LOG_LEVEL=INFO
MONSOON_LOG_FORMAT=json
```
