# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:55:04 2019

@author: phiflip
"""


import os
import rasterio
from rasterio.transform import from_origin
from matplotlib import pylab as plt
# Close all open plots to free up memory.
plt.close("all")

# Set the working directory.
os.chdir('G:/GISPyHelpers/GIS_Data_Examples')

reference_coordinateX = 601898.63
reference_coordinateY = 204436.08

# Dates and their corresponding shifts. Example: {"2023-06-20": (shift_x, shift_y), ...}
shifts = {

    "2020-06-03": (reference_coordinateX-601898.63, reference_coordinateY-204436.08),

    # Add more dates and their shifts as needed.
}

# File suffixes for the types of images to process
file_suffixes = [
    # "_DSM.tif", 
    "_allChannels.tif",
    # "_jpgOrtho.tif"
    ]

# Loop through each date in the shifts dictionary.
for date, (shift_x, shift_y) in shifts.items():
    for suffix in file_suffixes:
        # Define the path to the file for the current date and type.
        img_path = f'{date}/Agisoft/Agi_EXPORT/{date}{suffix}'

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
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(data_array)  # Write the original data into the new file with updated metadata.

            print(f"Processed and saved: {output_path}")

        except FileNotFoundError:
            print(f"File not found: {img_path}, skipping.")
