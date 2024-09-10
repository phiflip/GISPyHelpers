
# Create Stacked RGB Script

## Description
This script, `create_stackedRGB.py`, is designed to process and enhance GeoTIFF images for multiple dates. It reads multispectral bands (such as Blue, Green, and Red) from a GeoTIFF file, applies individual scaling to each band, enhances the brightness using a gamma correction method, and outputs an RGB image.

The script supports batch processing of multiple date directories, ensuring consistent image processing across all datasets.

## Features
- **Band Scaling**: Each spectral band is scaled to the full 0-255 range to fully utilize the dynamic range.
- **Gamma Correction**: Brightness is enhanced using gamma correction, resulting in clearer and more visually accurate images.
- **Batch Processing**: Multiple date directories can be processed in one go.
- **Output**: The final enhanced RGB image is saved as a GeoTIFF file.

## Usage
To run this script, use the following command in your terminal or command prompt:

```bash
python create_stackedRGB.py [date1] [date2] ... [dateN] --subfolder [subfolder_name]
```

- **`[date1] [date2] ... [dateN]`**: List of date strings representing the directories to process.
- **`--subfolder [subfolder_name]`**: (Optional) Specify a subfolder under each date directory if necessary.

### Example

If you have images from the dates `2020-06-03`, `2020-06-04`, and `2020-06-05` stored in corresponding directories, and these directories have a subfolder called `Data`, run the script as follows:

```bash
python create_stackedRGB.py 2020-06-03 2020-06-04 2020-06-05 --subfolder Data
```

If there is no subfolder, simply omit the `--subfolder` option:

```bash
python create_stackedRGB.py 2020-06-03 2020-06-04 2020-06-05
```

### Dependencies

- **Python 3.x**
- **rasterio**
- **numpy**
- **matplotlib**

Ensure all dependencies are installed. You can install them using `pip`:

```bash
pip install rasterio numpy matplotlib
```

## Gamma Correction Note
This script enhances the brightness of each band by applying a gamma correction method. The gamma correction adjusts the brightness of an image, making the output more visually appealing and suitable for further analysis.


