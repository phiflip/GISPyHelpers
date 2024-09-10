
# Masked Vegetation Index Extraction Script

## Description
This script, `masked_vegetation_index_extraction_bash.py`, is designed to extract vegetation indices from raster data. It allows for masking the data using a shapefile, applying NDVI thresholding, and saving specific vegetation indices. The script also supports additional subfolder handling for organizing output data.

## Features
- **Vegetation Index Extraction**: Calculates various vegetation indices, such as NDVI, from raster data.
- **Masking**: Supports masking the raster data using a provided shapefile.
- **NDVI Thresholding**: Applies a threshold to the NDVI values to filter the data.
- **Subfolder Handling**: Can process data within subfolders if specified.
- **Batch Processing**: Supports processing data for multiple dates or directories.

## Usage
To run this script, use the following command in your terminal or command prompt:

```bash
python masked_vegetation_index_extraction_bash.py --shapefile_path [path_to_shapefile] --date [date] --ndvi_threshold [ndvi_threshold] --indices_to_save [index1] [index2] ... [indexN] --subfolder [subfolder_name]
```

- **`--shapefile_path [path_to_shapefile]`**: The path to the shapefile used for masking.
- **`--date [date]`**: The date string representing the directory to process.
- **`--ndvi_threshold [ndvi_threshold]`**: The threshold value for NDVI filtering.
- **`--indices_to_save [index1] [index2] ... [indexN]`**: List of indices to save (e.g., NDVI, NDRE).
- **`--subfolder [subfolder_name]`**: (Optional) Specify a subfolder under the date directory if necessary.

### Example

If you have a shapefile located at `G:/GISPyHelpers/data/zz_QGis/Shapefiles/Area_DSM.shp` and want to process data from the date `2020-06-03`, applying an NDVI threshold of `0.3` and saving the indices `NDVI` and `NDRE`, run the script as follows:

```bash
python masked_vegetation_index_extraction_bash.py --shapefile_path G:/GISPyHelpers/data/zz_QGis/Shapefiles/Area_DSM.shp --date 2020-06-03 --ndvi_threshold 0.3 --indices_to_save NDVI NDRE
```

If there is no subfolder, simply omit the `--subfolder` option.

## Dependencies
- Python 3.x
- `rasterio`
- `numpy`
- `matplotlib`
- `fiona`
- `shapely`
- `pyproj`

Ensure all dependencies are installed. You can install them using `pip`:

```bash
pip install rasterio numpy matplotlib fiona shapely pyproj
```

## Notes
- The script assumes that the shapefile is correctly projected and aligned with the raster data.
- The indices to save should be specified as a list, with supported indices being determined by the `multichannel_index_definitions` module.

---
