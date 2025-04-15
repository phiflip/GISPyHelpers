
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
**Make sure you are in the root directory of the project**, specifically the `GISPyHelpers` folder. All relative paths used by the script assume this as the working directory.

Navigate to the root like this:
```bash
cd path/to/GISPyHelpers
```
To run this script, use the following command in your terminal or command prompt:

```bash
python calculate_derivedDTM.py --shapefile [path_to_shapefile] --date [date] --pixel_size_factor [factor] --subfolder [subfolder_name]
```

- **`--shapefile [path_to_shapefile]`**: The path to the shapefile used for masking or region-specific processing.
- **`--site [site]`**: The site representing the directory to process.
- **`--date [date]`**: The date string representing the directory to process.
- **`--region [subfolder_name]`**: Specify a subfolder under the date directory.
- **`--pixel_size_factor [factor]`**: The factor by which to scale the pixel size (e.g., 2).

### Example

If you have a shapefile located at `G:/GISData/Area.shp` and want to process data from the date `2020-06-03`, scaling the pixel size by a factor of `1.5`, with results stored in a subfolder called `Area`, run the script as follows:

```bash
python .\scripts.\03_calculate_derivedDTM_and_CSM\calculate_derivedDTM.py --shapefile ./data/zz_QGis/Shapefiles/Area.shp --site Ruetti --date 2020-06-03 --region Area --pixel_size_factor 1.5
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
