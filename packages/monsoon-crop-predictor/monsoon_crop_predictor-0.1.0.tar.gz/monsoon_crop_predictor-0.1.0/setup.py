"""
Setup script for Monsoon Crop Predictor
"""

from setuptools import setup, find_packages
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
except FileNotFoundError:
    # Fallback requirements
    requirements = [
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "scipy>=1.7.0",
        "lightgbm>=3.2.0",
        "xgboost>=1.4.0",
    ]

# Optional dependencies for different features
extras_require = {
    "api": ["fastapi>=0.68.0", "uvicorn[standard]>=0.15.0", "pydantic>=1.8.0"],
    "cli": ["click>=8.0.0"],
    "visualization": ["matplotlib>=3.3.0", "seaborn>=0.11.0", "plotly>=5.0.0"],
    "jupyter": ["jupyter>=1.0.0", "ipykernel>=6.0.0", "notebook>=6.4.0"],
    "dev": [
        "pytest>=6.0.0",
        "pytest-cov>=2.12.0",
        "black>=21.0.0",
        "flake8>=3.9.0",
        "mypy>=0.910",
        "pre-commit>=2.15.0",
    ],
}

# All optional dependencies
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    name="monsoon-crop-predictor",
    version="0.1.0",
    description="Advanced ML-based crop yield prediction system using monsoon and rainfall data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SubratDash67/Monsoon-Crop-Yield",
    author="Subrat Dash",
    author_email="subratdash2022@gmail.com",
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="agriculture, crop yield, machine learning, monsoon, rainfall, prediction, farming",
    # Package configuration
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    python_requires=">=3.8",
    # Dependencies
    install_requires=requirements,
    extras_require=extras_require,
    # Entry points for CLI commands
    entry_points={
        "console_scripts": [
            "crop-predictor=monsoon_crop_predictor.cli.commands:cli",
        ],
    },
    # Include package data
    package_data={
        "monsoon_crop_predictor": [
            "models/best_advanced_models/*.pkl",
            "data/*.csv",
            "config/*.json",
        ],
    },
    include_package_data=True,
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/SubratDash67/Monsoon-Crop-Yield/issues",
        "Source": "https://github.com/SubratDash67/Monsoon-Crop-Yield",
        "Documentation": "https://github.com/SubratDash67/Monsoon-Crop-Yield/blob/main/README.md",
    },
    # License
    license="MIT",
    # Zip safe
    zip_safe=False,
)
