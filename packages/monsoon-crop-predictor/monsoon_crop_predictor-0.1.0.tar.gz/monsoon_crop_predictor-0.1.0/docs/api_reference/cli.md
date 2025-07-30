# CLI API Reference

## monsoon_crop_predictor.cli

### Command Interface

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.cli
```

### Commands

#### predict

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.predict
```

**Usage:**

```bash
monsoon-crop predict --crop rice --state "West Bengal" --district "Bardhaman" \
    --rainfall 1200.5 --temperature 28.3 --humidity 75.0
```

**Options:**

- `--crop`: Crop type (rice, wheat, maize)
- `--state`: Indian state name
- `--district`: District name
- `--rainfall`: Rainfall in mm
- `--temperature`: Temperature in °C
- `--humidity`: Humidity percentage
- `--area`: Cultivation area in hectares (optional)
- `--irrigation`: Irrigation percentage (optional)
- `--fertilizer`: Fertilizer usage in kg/hectare (optional)
- `--output`: Output format (json, table, csv)

#### batch-predict

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.batch_predict
```

**Usage:**

```bash
monsoon-crop batch-predict --input data.csv --output results.csv
```

**Options:**

- `--input`: Input CSV file path
- `--output`: Output CSV file path
- `--format`: Output format (csv, json)

#### analyze

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.analyze
```

**Usage:**

```bash
monsoon-crop analyze --crop rice --state "West Bengal" --district "Bardhaman" --year 2024
```

**Options:**

- `--crop`: Crop type
- `--state`: State name
- `--district`: District name
- `--year`: Year for analysis
- `--output`: Output format (json, table)

#### recommend

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.recommend
```

**Usage:**

```bash
monsoon-crop recommend --crop rice --state "West Bengal" --district "Bardhaman" \
    --rainfall 1200.5 --temperature 28.3 --humidity 75.0
```

**Options:**

- `--crop`: Crop type
- `--state`: State name
- `--district`: District name
- `--rainfall`: Current rainfall
- `--temperature`: Current temperature
- `--humidity`: Current humidity
- `--irrigation`: Current irrigation level (optional)
- `--fertilizer`: Current fertilizer usage (optional)

#### validate

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.validate
```

**Usage:**

```bash
monsoon-crop validate --file data.csv
```

**Options:**

- `--file`: Data file to validate
- `--schema`: Validation schema (prediction, historical)
- `--strict`: Enable strict validation

#### info

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.info
```

**Usage:**

```bash
monsoon-crop info
```

Shows package information, model status, and system details.

#### interactive

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.interactive
```

**Usage:**

```bash
monsoon-crop interactive
```

Starts an interactive mode for making predictions.

#### api

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.api
```

**Usage:**

```bash
monsoon-crop api --host 0.0.0.0 --port 8000
```

**Options:**

- `--host`: Host address (default: 127.0.0.1)
- `--port`: Port number (default: 8000)
- `--reload`: Enable auto-reload for development
- `--debug`: Enable debug mode

### Utility Functions

#### format_output

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.format_output
```

#### validate_crop_input

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.validate_crop_input
```

#### load_csv_data

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.load_csv_data
```

#### save_csv_data

```{eval-rst}
.. autofunction:: monsoon_crop_predictor.cli.commands.save_csv_data
```

## Configuration Files

### CSV Input Format

For batch predictions, the input CSV should have the following columns:

**Required columns:**

- `crop`: Crop type (rice, wheat, maize)
- `state`: Indian state name
- `district`: District name
- `rainfall`: Rainfall in mm
- `temperature`: Temperature in °C
- `humidity`: Humidity percentage

**Optional columns:**

- `area`: Cultivation area in hectares
- `irrigation`: Irrigation percentage (0-100)
- `fertilizer_usage`: Fertilizer usage in kg/hectare
- `seed_variety`: Seed variety name

**Example CSV:**

```csv
crop,state,district,rainfall,temperature,humidity,area,irrigation
rice,West Bengal,Bardhaman,1200.5,28.3,75.0,100.0,80.0
wheat,Punjab,Ludhiana,400.2,22.1,65.0,200.0,90.0
maize,Maharashtra,Pune,800.7,25.5,70.0,150.0,60.0
```

### Output Formats

#### JSON Format

```json
{
  "yield_prediction": 4.25,
  "confidence": 0.87,
  "risk_level": "Low",
  "prediction_interval": {
    "lower": 3.85,
    "upper": 4.65
  }
}
```

#### Table Format

```
Crop Yield Prediction Results
============================
Crop: rice
Location: West Bengal, Bardhaman
Predicted Yield: 4.25 tonnes/hectare
Confidence: 87%
Risk Level: Low
Prediction Interval: 3.85 - 4.65 tonnes/hectare
```

#### CSV Format (for batch results)

```csv
crop,state,district,yield_prediction,confidence,risk_level,lower_bound,upper_bound
rice,West Bengal,Bardhaman,4.25,0.87,Low,3.85,4.65
wheat,Punjab,Ludhiana,3.12,0.92,Low,2.89,3.35
```
