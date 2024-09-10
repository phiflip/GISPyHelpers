# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 08:09:58 2024

@author: MinorNT
"""

import os
import argparse
import rasterio
import numpy as np
from matplotlib import pyplot as plt
from os.path import join

# Function to scale a band individually to the full 0-255 range
def scale_band_individually(array):
    """Scales each band individually to the full 0-255 range."""
    array_min, array_max = array.min(), array.max()
    return ((array - array_min) / (array_max - array_min) * 255).astype(np.uint8)

# Function to further enhance brightness
def enhance_brightness(array, brightness_factor=4):
    """Further enhances brightness by scaling the array."""
    array_enhanced = array * brightness_factor
    return np.clip(array_enhanced, 0, 255).astype(np.uint8)

# Main function to process the images
def process_images_for_date(date, subfolder=None):
    # Define the base path pattern
    if subfolder:
        base_path_pattern = os.path.join(date, subfolder, "Agisoft", "Agi_EXPORT")
    else:
        base_path_pattern = os.path.join(date, "Agisoft", "Agi_EXPORT")
    
    # Set file paths
    filename = date + "_allChannels.tif"
    read_allChannels = join(base_path_pattern, filename)

    if not os.path.exists(read_allChannels):
        print(f"File not found: {read_allChannels}")
        return

    # Open the GeoTIFF file
    with rasterio.open(read_allChannels) as src:
        # Read bands (BGR, RedEdge, NIR, Alpha)
        blue = src.read(1) / 32768.0  # Normalize the blue band to a 0-1 range
        green = src.read(2) / 32768.0  # Normalize the green band to a 0-1 range
        red = src.read(3) / 32768.0  # Normalize the red band to a 0-1 range

    # Scale each band individually
    red_scaled = scale_band_individually(red)
    green_scaled = scale_band_individually(green)
    blue_scaled = scale_band_individually(blue)

    # Enhance brightness for each band
    red_enhanced = enhance_brightness(red_scaled)
    green_enhanced = enhance_brightness(green_scaled)
    blue_enhanced = enhance_brightness(blue_scaled)

    # Create an RGB image (BGR order)
    rgb_image = np.stack((red_enhanced, green_enhanced, blue_enhanced), axis=-1)

    # Optionally display the image
    # plt.imshow(rgb_image)
    # plt.title(f"RGB Image for {date} (Brightness Enhanced)")
    # plt.show()

    # Optionally save the RGB image as a new GeoTIFF file
    output_path = join(base_path_pattern, "output_rgb.tif")
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=rgb_image.shape[0],
        width=rgb_image.shape[1],
        count=3,
        dtype=rgb_image.dtype,
        crs=src.crs,
        transform=src.transform,
    ) as dst:
        dst.write(rgb_image[:, :, 0], 1)  # Write red channel
        dst.write(rgb_image[:, :, 1], 2)  # Write green channel
        dst.write(rgb_image[:, :, 2], 3)  # Write blue channel

    print(f"Processing complete for {date}. Output saved to {output_path}")

# Function to process multiple dates
def process_multiple_dates(dates, subfolder=None):
    for date in dates:
        process_images_for_date(date, subfolder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and enhance GeoTIFF images for multiple dates.")
    parser.add_argument("dates", nargs='+', help="List of date strings for the directories to process")
    parser.add_argument("--subfolder", type=str, help="Optional subfolder under each date directory", default=None)
    
    args = parser.parse_args()
    process_multiple_dates(args.dates, args.subfolder)
