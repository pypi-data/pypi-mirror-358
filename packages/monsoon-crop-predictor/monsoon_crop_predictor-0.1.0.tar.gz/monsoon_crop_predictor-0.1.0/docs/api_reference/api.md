# API Components Reference

## monsoon_crop_predictor.api

### FastAPI Application

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.api.endpoints.create_app
```

### Schemas

#### Request Schemas

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.PredictionRequest
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.BatchPredictionRequest
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.MonsoonAnalysisRequest
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.RecommendationRequest
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.RiskAssessmentRequest
   :members:
   :undoc-members:
   :show-inheritance:
```

#### Response Schemas

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.PredictionResponse
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.BatchPredictionResponse
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.MonsoonAnalysisResponse
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.RecommendationResponse
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.RiskAssessmentResponse
   :members:
   :undoc-members:
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: monsoon_crop_predictor.api.schemas.HealthResponse
   :members:
   :undoc-members:
   :show-inheritance:
```

### Middleware

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.api.middleware.add_cors_middleware
```

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.api.middleware.add_rate_limiting
```

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.api.middleware.add_logging_middleware
```

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.api.middleware.add_security_headers
```

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.api.middleware.add_metrics_middleware
```
