# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:55:04 2019

Updated for additional subfolder handling
"""

import os
import json
import rasterio
from rasterio.transform import from_origin
from matplotlib import pylab as plt
import argparse

def process_images(date, file_suffixes, subfolder=None):
    # Close all open plots to free up memory.
    plt.close("all")

    # Load the reference coordinates and shifts from the JSON file
    json_path = f'shifts_{subfolder}.json' if subfolder else 'shifts.json'
    with open(json_path, 'r') as f:
        data = json.load(f)
        reference_coordinateX = data["reference_coordinateX"]
        reference_coordinateY = data["reference_coordinateY"]
        shifts = data["shifts"]

    # Get the shift values for the specified date
    if date in shifts:
        shift_x_orig, shift_y_orig = shifts[date]
        shift_x = reference_coordinateX - shift_x_orig
        shift_y = reference_coordinateY - shift_y_orig
    else:
        print(f"No shift data available for date: {date}")
        return

    # Loop through each file suffix.
    for suffix in file_suffixes:
        # Define the path to the file for the current date and type.
        if subfolder:
            img_path = os.path.join(date, subfolder, 'Agisoft', 'Agi_EXPORT', f'{date}{suffix}')
        else:
            img_path = os.path.join(date, 'Agisoft', 'Agi_EXPORT', f'{date}{suffix}')

        # Attempt to open and process the image file.
        try:
            with rasterio.open(img_path) as data:
                data_array = data.read()  # Read the data into a numpy array.
                gt = data.transform  # Extract geotransform information.

                # Calculate new transformation coordinates using the specific shifts for the date.
                transformed_coords = from_origin(gt[2] + shift_x, gt[5] + shift_y, gt[0], -gt[4])
                
                # Prepare metadata for the output image.
                out_meta = data.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": data.height,
                    "width": data.width,
                    "transform": transformed_coords
                })

            # Save the transformed image data in a new file for the current date and type.
            output_path = img_path[:-4] + '_xy_transformed.tif'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(data_array)  # Write the original data into the new file with updated metadata.

            print(f"Processed and saved: {output_path}")

        except FileNotFoundError:
            print(f"File not found: {img_path}, skipping.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process image files and apply coordinate shifts.")
    parser.add_argument("--date", required=True, help="Date of the dataset (format: YYYY-MM-DD)")
    parser.add_argument("--file_suffixes", required=True, nargs='+', help="List of file suffixes to process (e.g., _DSM.tif _allChannels.tif)")
    parser.add_argument("--subfolder", required=False, help="Subfolder within the date directory")

    args = parser.parse_args()
    process_images(args.date, args.file_suffixes, args.subfolder)
