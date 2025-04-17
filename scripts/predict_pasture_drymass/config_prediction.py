# config_prediction.py

DEFAULTS = {
    "date": "2020-06-03",
    "region": "Area",  # leave empty if you want to supply via CLI
    "site": "Ruetti",
    "model_name": "estiGrass3Dplus.pkl"
}

CAMERATYPE = 2 #0 for five channels (P4M), 1 for 4 channels (sequoia), 2 (Mavic 3M)
USE = 0 # 0 for pasture use, 1 for cutting use


# All relevant dates to loop over
DATES = [
    "2025-04-01",
    "2025-04-14",

]


# Site-to-region mapping for batch processing
SITE_REGION_MAP = {
    "Gampelen": ["Neugrabe1_4"],
    "Carrouge": [
        "SB6A_3",
        "SB7B_4"
                  ],
    "Gysenstein": [
        "RJ1",
        "RJ2",
        "RJ3",
        "RJ4"
                 ],
}


# Default elevation above sea level for reflectance correction
MASL_DEFAULT = "1200"

# NDVI threshold used in VI masking
NDVI_THRESHOLD = 0.0
