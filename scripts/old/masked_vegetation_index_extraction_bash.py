# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:55:04 2019

@author: phiflip
"""
import os
import argparse
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import fiona
from pyproj import CRS
from shapely.geometry import shape
import sys

# Add path to module
sys.path.append('G:/GISPyHelpers/modules')

import multichannel_index_definitions as mcvi

def main(shapefile_path, date, ndvi_threshold, indices_to_save):
    # Define the base path pattern
    base_path_pattern = os.path.join(date, "Agisoft", "Agi_EXPORT")
    
    # Reading data and setting paths
    filename = date + "_allChannels_xy_transformed.tif"
    read_allChannels = os.path.join(base_path_pattern, filename)

    with fiona.open(shapefile_path, 'r') as shapefile:
        # Direct creation of CRS from EPSG code
        crs = CRS.from_epsg("21781")
        all_shapes = [shape(feat['geometry']) for feat in shapefile]
        shp_geom = all_shapes[0]  # Example, using the first geometry

    # Read images without ROI
    multiChannel_array, out_meta = mcvi.clip(shp_geom, read_allChannels)
    multiChannel_array_trans = multiChannel_array.transpose((1, 2, 0))
    
    # Identify available channels
    num_channels = multiChannel_array_trans.shape[2]
    channels = {}
    if num_channels == 6:
        channels['blue'] = multiChannel_array_trans[:, :, 0].astype(float) / 32768
        channels['green'] = multiChannel_array_trans[:, :, 1].astype(float) / 32768
        channels['red'] = multiChannel_array_trans[:, :, 2].astype(float) / 32768
        channels['rededge'] = multiChannel_array_trans[:, :, 3].astype(float) / 32768
        channels['nir'] = multiChannel_array_trans[:, :, 4].astype(float) / 32768
        channels['alpha'] = multiChannel_array_trans[:, :, 5].astype(float)
    elif num_channels == 5:
        channels['green'] = multiChannel_array_trans[:, :, 0].astype(float) / 32768
        channels['red'] = multiChannel_array_trans[:, :, 1].astype(float) / 32768
        channels['rededge'] = multiChannel_array_trans[:, :, 2].astype(float) / 32768
        channels['nir'] = multiChannel_array_trans[:, :, 3].astype(float) / 32768
        channels['alpha'] = multiChannel_array_trans[:, :, 4].astype(float)
    else:
        raise ValueError("Unexpected number of channels in the input data.")

    # Create a mask based on a NDVI threshold
    ndvi_mask = mcvi.ndvi(channels['nir'], channels['red'])
    ndvi_mask = np.expand_dims(ndvi_mask, axis=2)  # Expand dimensions

    # Create a binary mask: Values <= ndvi_threshold become 0, values > ndvi_threshold become 255
    binary_mask = np.where(ndvi_mask > ndvi_threshold, np.nan, 0).astype(np.float64)

    # Visualize the mask
    # plt.figure("Binary NDVI Mask")
    # plt.imshow(binary_mask[:, :, 0], cmap='gray')
    # plt.colorbar()
    # plt.show()

    # Retransform (bands, rows, cols)
    binary_mask_geo_trans = binary_mask.transpose((2, 0, 1))

    # Define metadata for GeoTIFF storage
    out_meta.update({"driver": "GTiff", "count": 1, "dtype": rasterio.float64})

    # Save as GeoTIFF
    output_path = os.path.join(base_path_pattern, "VIs", f"{date}_Mask.tif")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(binary_mask_geo_trans)

    print(f"MASK saved at {output_path}")

    # Definition of available indices and required channels
    available_indices = {
        "NDVI": (mcvi.ndvi, ['nir', 'red']),
        "WDRVI": (mcvi.wdrvi, ['nir', 'red', 0.2]),
        "GNDVI": (mcvi.gndvi, ['nir', 'green']),
        "SAVI": (mcvi.savi, ['nir', 'red']),
        "GCI": (mcvi.gci, ['nir', 'green']),
        "RCI": (mcvi.rci, ['nir', 'rededge']),
        "NDRE": (mcvi.ndre, ['nir', 'rededge']),
        "GRVI": (mcvi.grvi, ['red', 'green']),
        "MGRVI": (mcvi.mgrvi, ['red', 'green']),
        "RGBVI": (mcvi.rgbvi, ['red', 'green', 'blue'])
    }

    # Filter available indices based on available channels
    filtered_indices = {k: v for k, v in available_indices.items() if all(c in channels for c in v[1] if isinstance(c, str))}

    # Processing and saving the selected indices
    for index in indices_to_save:
        if index in filtered_indices:
            func, params = filtered_indices[index]
            if len(params) == 3 and isinstance(params[2], float):
                result = func(channels[params[0]], channels[params[1]], params[2])
            else:
                result = func(*[channels[channel] for channel in params if channel in channels])
            result = np.expand_dims(result, axis=2)

            # Plot and save the results
            mcvi.plotVI(result, index, "RdYlGn", quantile=0.5)
            out_meta.update({"driver": "GTiff", "count": 1, "dtype": rasterio.float64})
            result_geo_trans = result.transpose((2, 0, 1))
            output_path = os.path.join(base_path_pattern, "VIs", f"{date}_{index}.tif")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(result_geo_trans)
            print(f"{index} calculated and saved at {output_path}.")
        else:
            print(f"{index} is not a valid index or required channels are missing.")

    print(f"{date} Visualize VIs done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process GIS data and calculate vegetation indices.")
    parser.add_argument("--shapefile_path", required=True, help="Path to the shapefile")
    parser.add_argument("--date", required=True, help="Date of the dataset (format: YYYY-MM-DD)")
    parser.add_argument("--ndvi_threshold", type=float, required=True, help="NDVI threshold for mask")
    parser.add_argument("--indices_to_save", nargs='+', required=True, help="List of indices to save (e.g., NDVI WDRVI)")

    args = parser.parse_args()
    main(args.shapefile_path, args.date, args.ndvi_threshold, args.indices_to_save)
