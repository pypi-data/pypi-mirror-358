# Development Guide

This section provides information for developers who want to contribute to or extend the Monsoon Crop Predictor package.

```{toctree}
:maxdepth: 2

setup
contributing
architecture
testing
deployment
```

## Quick Start for Developers

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/monsoon-crop-predictor.git
cd monsoon-crop-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Build documentation
cd docs
make html
```

### Project Structure

```
monsoon-crop-predictor/
├── monsoon_crop_predictor/     # Main package
│   ├── core/                   # Core functionality
│   ├── models/                 # Model management
│   ├── api/                    # REST API
│   ├── utils/                  # Utilities
│   └── cli/                    # Command-line interface
├── tests/                      # Test suite
├── docs/                       # Documentation
├── examples/                   # Examples and demos
└── setup.py                    # Package configuration
```

## Development Workflow

1. **Fork and Clone**: Fork the repository and clone your fork
2. **Create Branch**: Create a feature branch for your changes
3. **Develop**: Make your changes with tests
4. **Test**: Run the test suite and ensure all tests pass
5. **Document**: Update documentation as needed
6. **Submit**: Create a pull request with your changes
