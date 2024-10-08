
# Calculate Derived Digital Terrain Model (DTM) Script

## Description
This script, `calculate_derivedDTM.py`, is designed to calculate a derived Digital Terrain Model (DTM) from UAV data. The script includes handling for subfolders, shapefiles, and allows for adjusting the pixel size through a scaling factor. It applies various filtering and modeling techniques to generate the DTM.

### Application
This routine was used in the *estiGrass3D+* paper titled **"Herbage biomass predictions from UAV data using a derived digital terrain model and machine learning."** The script played a crucial role in generating the DTM used for biomass predictions in the study.

## Features
- **DTM Calculation**: Generates a Digital Terrain Model (DTM) from UAV data.
- **Filtering**: Applies various filters to refine the DTM.
- **Subfolder and Shapefile Handling**: Can process data within subfolders and use shapefiles for masking or region-specific processing.
- **Pixel Size Adjustment**: Allows for scaling the pixel size by a specified factor using the `--pixel_size_factor` argument.
- **Integration with Custom Modules**: The script integrates with custom modules like `module_DTMmodel` for advanced processing.

## Usage
To run this script, use the following command in your terminal or command prompt:

```bash
python calculate_derivedDTM.py --shapefile [path_to_shapefile] --date [date] --pixel_size_factor [factor] --subfolder [subfolder_name]
```

- **`--shapefile [path_to_shapefile]`**: The path to the shapefile used for masking or region-specific processing.
- **`--date [date]`**: The date string representing the directory to process.
- **`--pixel_size_factor [factor]`**: The factor by which to scale the pixel size (e.g., 2).
- **`--subfolder [subfolder_name]`**: (Optional) Specify a subfolder under the date directory if necessary.

### Example

If you have a shapefile located at `G:/GISData/Regions.shp` and want to process data from the date `2020-06-03`, scaling the pixel size by a factor of `2`, with results stored in a subfolder called `south`, run the script as follows:

```bash
python calculate_derivedDTM.py --date 2020-06-03 --pixel_size_factor 2 --shapefile G:/GISData/Regions.shp --subfolder south
```

If there is no subfolder, simply omit the `--subfolder` option:

```bash
python calculate_derivedDTM.py --date 2020-06-03 --pixel_size_factor 2 --shapefile G:/GISData/Regions.shp
```

## Dependencies
- Python 3.x
- `rasterio`
- `numpy`
- `matplotlib`
- `skimage`
- `fiona`
- `scipy`
- `shapely`

Ensure all dependencies are installed. You can install them using `pip`:

```bash
pip install rasterio numpy matplotlib skimage fiona scipy shapely
```

## Notes
- The script assumes that the shapefile is correctly projected and aligned with the raster data.
- The script utilizes a custom module, `module_DTMmodel`, which should be available in the specified module path.
