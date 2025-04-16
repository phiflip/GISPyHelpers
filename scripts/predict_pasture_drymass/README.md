
# Prediction Pipeline for Pasture Dry Mass (estiGrass3D+)

This repository provides a modular pipeline for predicting pasture dry mass using height and vegetation index features derived from multispectral imagery and digital surface models.

## Project Structure

```bash
.
├── data/                          # Structured input data and results
│   ├── <site>/<date>/<region>/   # Agisoft exports and images
│   ├── zz_Resultate/             # Intermediate and final results
│   └── zz_Qgis/Shapefiles/       # Plot shapefiles
├── models/                       # Trained ML models (.pkl)
├── scripts/
│   └── predict_pasture_drymass/  # Core prediction pipeline scripts
│       ├── run_prediction_pipeline.py
│       ├── config_prediction.py
│       ├── features.py
│       ├── model_utils.py
│       └── prepare_dataframe.py
```

## Pipeline Overview

The pipeline performs the following steps:

1. **Extract height features** from `CSM.tif` using shapefiles.
2. **Compute vegetation indices** from multispectral images.
3. **Combine and prepare all features** into a prediction-ready DataFrame.
4. **Load a trained ML model** (e.g., `estiGrass3Dplus.pkl`).
5. **Run predictions** of pasture dry mass.
6. **Export results** to CSV format.

## Usage

### Batch Mode (loop over all dates/sites/regions from `config_prediction.py`):

```bash
python ./scripts/predict_pasture_drymass/run_prediction_pipeline.py --model estiGrass3Dplus.pkl
```

### Single Site Execution:

```bash
python ./scripts/predict_pasture_drymass/run_prediction_pipeline.py --date 2020-06-03 --site Ruetti --region "Area" --model estiGrass3Dplus.pkl
```

## Configuration

Default values, region mappings, and date lists are set in:

- `scripts/predict_pasture_drymass/config_prediction.py`

You can customize `SITES`, `REGIONS`, `DATES`, and the `MASL_DEFAULT` elevation value there.

## Output

Prediction results are saved to:

```
data/zz_Results/<date>_<region>_predictions.csv
```

A `last_run_info.txt` log is also created with the details of the last pipeline execution.

---

