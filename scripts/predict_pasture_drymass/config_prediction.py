import os

def find_root_from_cwd():
    p = os.path.abspath(os.getcwd())
    for _ in range(10):
        if os.path.isdir(os.path.join(p, "data")) and os.path.isdir(os.path.join(p, "zz_QGis")):
            return p
        p = os.path.dirname(p)
    raise RuntimeError("Could not find project root (expected folders: data and zz_QGis)")

PROJECT_ROOT = find_root_from_cwd()
DATA_ROOT  = os.path.join(PROJECT_ROOT, "data")
SHAPE_ROOT = os.path.join(PROJECT_ROOT, "zz_QGis", "Shapefiles")



DEFAULTS = {
    "date": "2020-06-03",
    "region": "Area",  # leave empty if you want to supply via CLI
    "site": "Ruetti",
    "model_name": "estiGrass3Dplus.pkl"
}


CAMERATYPE = 2 #0 for five channels (P4M), 1 for 4 channels (sequoia), 2 (Mavic 3M)
USE = 0 # 0 for pasture use, 1 for cutting use

RASTER_VARIANT = "raw"   # "raw" | "withoutRest" | "onlyRest"
# Optional: if set, this shapefile is used instead of f"{region}.shp"

SHAPEFILE_NAME = "3_estiGrass.shp"   # None = use region-based shapefile

# All relevant dates to loop over
DATES = [
    # "2025-08-27",
    # "2025-09-18",
    "2025-10-02",
    # "2025-10-31",
    # "2025-11-13",

]


# Site-to-region mapping for batch processing
SITE_REGION_MAP = {
    "Balsingen": ["3_Weide"],
#     "Carrouge": [
#         "SB6A_3",
#         "SB7B_4"
#                   ],
#     "Gysenstein": [
#         "RJ1",
#         "RJ2",
#         "RJ3",
#         "RJ4"
#                  ],
}


# Default elevation above sea level for reflectance correction
MASL_DEFAULT = "1200"

# NDVI threshold used in VI masking
NDVI_THRESHOLD = 0.0
