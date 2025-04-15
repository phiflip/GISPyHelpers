# config_prediction.py

DEFAULTS = {
    "date": "2020-06-03",
    "region": "Area",  # leave empty if you want to supply via CLI
    "site": "Ruetti",
    "model_name": "estiGrass3Dplus.pkl"
}

# Site-to-region mapping for batch processing
SITE_REGION_MAP = {
    "Ruetti": ["Area"],
}

# All relevant dates to loop over
DATES = [
    "2020-06-03",
    "2020-06-04",
    # "2025-05-01"
]

# Default elevation above sea level for reflectance correction
MASL_DEFAULT = "1200"

# NDVI threshold used in VI masking
NDVI_THRESHOLD = 0.0
