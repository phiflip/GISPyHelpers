
# Correct XY Offset Bash Script

## Description
This script, `correct_xy_offset_bash.py`, is designed to correct XY offsets in image data. The script processes image files, applies necessary transformations based on reference coordinates, and handles additional subfolder structures if present.

The script reads offset values from a JSON file, applies the shifts to the images, and can handle multiple date directories if needed.

## Features
- **XY Offset Correction**: Corrects the XY offsets in image data using predefined shift values.
- **Subfolder Handling**: Can process images in subfolders if specified.
- **Batch Processing**: Supports processing of multiple image files based on date or folder structure.

## Usage
To run this script, use the following command in your terminal or command prompt:

```bash
python correct_xy_offset_bash.py [date] --file_suffixes [suffix1] [suffix2] ... [suffixN] --subfolder [subfolder_name]
```

- **`[date]`**: The date string representing the directory to process.
- **`--file_suffixes [suffix1] [suffix2] ... [suffixN]`**: List of file suffixes to process.
- **`--subfolder [subfolder_name]`**: (Optional) Specify a subfolder under the date directory if necessary.

### Example

If you have images from the date `2020-06-03` stored in a directory, and these directories have a subfolder called `Data`, and you want to correct files with suffixes `_B01` and `_B02`, run the script as follows:

```bash
python correct_xy_offset_bash.py 2020-06-03 --file_suffixes _B01 _B02 --subfolder Data
```

If there is no subfolder, simply omit the `--subfolder` option:

```bash
python correct_xy_offset_bash.py 2020-06-03 --file_suffixes _B01 _B02
```

## Dependencies
- Python 3.x
- `rasterio`
- `numpy`
- `matplotlib`

Ensure all dependencies are installed. You can install them using `pip`:

```bash
pip install rasterio numpy matplotlib
```

## JSON File
The script expects a JSON file containing the shift values for the coordinates. The JSON file should be named in the format `shifts_[subfolder].json` if a subfolder is specified, or `shifts.json` otherwise. This JSON file must be stored in the same directory as the script or in a path that the script can access.

The JSON file should have the following structure:

```json
{
  "2020-06-03": {
    "x_shift": 5.0,
    "y_shift": -3.2
  },
  "2020-06-04": {
    "x_shift": 2.1,
    "y_shift": -1.0
  }
}
```

In this example, `x_shift` and `y_shift` represent the offset values for correcting the images taken on the respective dates.

