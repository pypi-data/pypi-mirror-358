# Contributing to Monsoon Crop Predictor

We welcome contributions to the Monsoon Crop Predictor project! This guide will help you get started.

## Types of Contributions

### Code Contributions

- Bug fixes
- New features
- Performance improvements
- Code refactoring

### Documentation

- API documentation improvements
- Tutorial enhancements
- Example notebooks
- Translation (future)

### Testing

- Unit tests
- Integration tests
- Performance tests
- Edge case testing

### Community

- Issue reporting
- Feature requests
- Discussion participation
- User support

## Getting Started

### 1. Development Environment Setup

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/monsoon-crop-predictor.git
cd monsoon-crop-predictor

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -e ".[dev]"
```

### 2. Development Dependencies

The development setup includes:

```bash
# Core package
pip install -e .

# Development tools
pip install pytest pytest-cov black flake8 mypy

# Documentation
pip install sphinx sphinx-rtd-theme myst-parser

# Optional: Pre-commit hooks
pip install pre-commit
pre-commit install
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

### 2. Make Your Changes

Follow these guidelines:

#### Code Style

- Use Black for code formatting: `black .`
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write descriptive variable and function names

#### Testing

- Write tests for new features
- Ensure all existing tests pass
- Aim for >90% code coverage

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=monsoon_crop_predictor tests/

# Run specific test
pytest tests/test_core.py::TestCropPredictor::test_predict
```

#### Documentation

- Update docstrings for new functions/classes
- Add examples where helpful
- Update relevant documentation files

### 3. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add rainfall pattern analysis feature"

# Push to your fork
git push origin feature/your-feature-name
```

#### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/modifications
- `refactor:` for code refactoring
- `perf:` for performance improvements

### 4. Submit a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template
5. Wait for review and feedback

## Code Guidelines

### Python Code Style

```python
# Good: Type hints and clear naming
def predict_yield(
    crop: str,
    rainfall: float,
    temperature: float,
    humidity: float
) -> PredictionResult:
    """
    Predict crop yield based on weather conditions.

    Args:
        crop: Type of crop (rice, wheat, maize)
        rainfall: Rainfall in mm
        temperature: Temperature in °C
        humidity: Humidity percentage

    Returns:
        Prediction result with yield and confidence

    Raises:
        ValidationError: If input parameters are invalid
    """
    # Implementation here
    pass

# Bad: No type hints, unclear naming
def predict(c, r, t, h):
    # No docstring, unclear purpose
    pass
```

### Error Handling

```python
# Good: Specific exceptions with helpful messages
try:
    result = model.predict(features)
except ModelNotFoundError as e:
    logger.error(f"Model file not found: {e}")
    raise PredictionError(f"Cannot make prediction: {e}")

# Bad: Generic exception handling
try:
    result = model.predict(features)
except Exception:
    pass  # Silent failure
```

### Logging

```python
# Good: Structured logging
logger = get_logger(__name__)
logger.info("Starting prediction", extra={
    "crop": crop,
    "model_version": model_version
})

# Bad: Print statements
print("Making prediction...")
```

## Testing Guidelines

### Test Structure

```python
import unittest
from unittest.mock import Mock, patch

class TestCropPredictor(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.predictor = CropPredictor()
        self.valid_input = {
            'crop': 'rice',
            'state': 'West Bengal',
            'district': 'Bardhaman',
            'rainfall': 1200,
            'temperature': 28,
            'humidity': 75
        }

    def test_predict_valid_input(self):
        """Test prediction with valid input."""
        result = self.predictor.predict(**self.valid_input)

        self.assertIsInstance(result, PredictionResult)
        self.assertGreater(result.yield_prediction, 0)
        self.assertBetween(result.confidence, 0, 1)

    def test_predict_invalid_crop(self):
        """Test prediction with invalid crop type."""
        invalid_input = self.valid_input.copy()
        invalid_input['crop'] = 'invalid_crop'

        with self.assertRaises(ValidationError):
            self.predictor.predict(**invalid_input)

    @patch('monsoon_crop_predictor.core.predictor.joblib.load')
    def test_predict_model_loading_error(self, mock_load):
        """Test prediction when model loading fails."""
        mock_load.side_effect = FileNotFoundError("Model not found")

        with self.assertRaises(ModelNotFoundError):
            self.predictor.predict(**self.valid_input)
```

### Test Categories

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test API endpoints
4. **CLI Tests**: Test command-line interface

## Documentation Guidelines

### Docstring Format

Use Google-style docstrings:

```python
def analyze_rainfall_patterns(
    rainfall_data: pd.DataFrame,
    window_size: int = 30
) -> Dict[str, float]:
    """
    Analyze rainfall patterns for crop prediction.

    This function calculates various rainfall statistics that are useful
    for predicting crop yields, including moving averages, intensity
    measures, and variability metrics.

    Args:
        rainfall_data: DataFrame with daily rainfall measurements.
            Must contain 'date' and 'rainfall' columns.
        window_size: Size of the moving window for calculations.
            Defaults to 30 days.

    Returns:
        Dictionary containing rainfall statistics:
        - moving_average: Moving average rainfall
        - intensity: Average daily intensity
        - variability: Coefficient of variation
        - extreme_days: Number of extreme rainfall days

    Raises:
        ValueError: If rainfall_data is empty or missing required columns.

    Example:
        >>> import pandas as pd
        >>> data = pd.DataFrame({
        ...     'date': pd.date_range('2023-01-01', periods=100),
        ...     'rainfall': np.random.exponential(2, 100)
        ... })
        >>> stats = analyze_rainfall_patterns(data)
        >>> print(stats['moving_average'])
        1.95
    """
    # Implementation here
    pass
```

### Documentation Files

- Keep documentation files in Markdown format
- Use clear headings and structure
- Include code examples
- Add cross-references where helpful

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `setup.py` and `__init__.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Build and test documentation
5. Create release tag
6. Build and upload to PyPI
7. Create GitHub release

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: Direct contact for urgent issues

### Resources

- [Python Development Guide](https://devguide.python.org/)
- [NumPy Style Guide](https://numpydoc.readthedocs.io/en/latest/format.html)
- [scikit-learn Contributor Guide](https://scikit-learn.org/stable/developers/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Recognition

Contributors will be:

- Listed in the `CONTRIBUTORS.md` file
- Mentioned in release notes
- Credited in documentation (where appropriate)

Thank you for contributing to Monsoon Crop Predictor! 🌾
