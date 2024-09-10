
# Create Masked CSM Script

## Description
This script, `create_maskedCSM_bash.py`, is designed to create a masked Canopy Surface Model (CSM) using a provided shapefile for masking and a date to locate the appropriate raster files. The script applies the mask to the CSM and outputs a masked CSM file.

## Features
- **Masking**: Applies a shapefile-based mask to the CSM.
- **Subfolder Handling**: Can process data within subfolders if specified.
- **Integration with Rasterio**: Utilizes Rasterio for reading and writing raster data.

## Usage
To run this script, use the following command in your terminal or command prompt:

```bash
python create_maskedCSM_bash.py [shapefile_path] [date] --subfolder [subfolder_name]
```

- **`[shapefile_path]`**: The path to the shapefile used for masking.
- **`[date]`**: The date string representing the directory to process.
- **`--subfolder [subfolder_name]`**: (Optional) Specify a subfolder under the date directory if necessary.

### Example

If you have a shapefile located at `G:/GISPyHelpers/data/zz_QGis/Shapefiles/Area_DSM.shp` and want to process data from the date `2020-06-03`, with results stored in the default subfolder structure, run the script as follows:

```bash
python create_maskedCSM_bash.py G:/GISPyHelpers/data/zz_QGis/Shapefiles/Area_DSM.shp 2020-06-03
```

If you need to specify a subfolder, you can do so with the `--subfolder` argument:

```bash
python create_maskedCSM_bash.py G:/GISPyHelpers/data/zz_QGis/Shapefiles/Area_DSM.shp 2020-06-03 --subfolder Data
```

## Dependencies
- Python 3.x
- `rasterio`
- `numpy`
- `matplotlib`
- `fiona`
- `shapely`

Ensure all dependencies are installed. You can install them using `pip`:

```bash
pip install rasterio numpy matplotlib fiona shapely
```

## Notes
- The script assumes that the shapefile is correctly projected and aligned with the raster data.
