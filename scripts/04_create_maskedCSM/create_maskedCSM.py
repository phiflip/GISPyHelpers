# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:55:04 2019

@author: bfhNT
"""

import cv2  # You mentioned this but didn't use it in the snippet. Make sure you need it.
import rasterio
import rasterio.plot
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import matplotlib.pyplot as plt
import os
import fiona
from rasterio.enums import Resampling
from shapely.geometry import shape
import argparse

def main(shapefile_path, date, subfolder=None):
    
    plt.close("all")

    # Adjust the path if subfolder is provided
    if subfolder:
        path_to_data = os.path.join(date, subfolder, "Agisoft", "Agi_EXPORT")
    else:
        path_to_data = os.path.join(date, "Agisoft", "Agi_EXPORT")

    filename = date + "_allChannels_xy_transformed.tif"
    read_allChannels = os.path.join(path_to_data, filename)

    # Use the provided shapefile path
    path_to_shapefile = shapefile_path
    

    

    #################################################################################
    # Read ShapeFile
    #################################################################################
    shapefile = fiona.open(path_to_shapefile)
    all_shapes = []
    shp_id_ls = []
    num = 1

    with shapefile as input:
        for feat in input:
            shp_id = feat['properties']['id']
            shp_geom = shape(feat['geometry'])
            all_shapes.append(shp_geom)
            shp_id_ls.append(shp_id)

    shp_geom = all_shapes[num - 1]

    #################################################################################
    # Mask for CSM
    #################################################################################

    # Read NDVI mask and CSM
    ndvi_mask_path = os.path.join(path_to_data, "VIs", date + "_MASK.tif")
    csm_path = os.path.join(path_to_data, date + "_clipped_CSM.tif")
    


    # Read CSM
    with rasterio.open(csm_path) as clipped_CSM:
        clipped_CSM_array = clipped_CSM.read(1)  # Read only the first band
        out_meta_CSM = clipped_CSM.meta.copy()

    # CSM dimensions
    width = clipped_CSM_array.shape[1]
    height = clipped_CSM_array.shape[0]

    # Read NDVI mask and resample to CSM dimensions
    with rasterio.open(ndvi_mask_path) as dataset:
        data_MASK = dataset.read(
            out_shape=(
                dataset.count,
                height,
                width
            ),
            resampling=Resampling.nearest
        )

        # Adjust transformation matrix
        transform = dataset.transform * dataset.transform.scale(
            (dataset.width / data_MASK.shape[-1]),
            (dataset.height / data_MASK.shape[-2])
        )
    
    # Convert and apply mask
    mask_resampled = np.squeeze(data_MASK)  # Remove unnecessary dimensions
    mask_resampled = np.where(mask_resampled == 0, np.nan, 1)  # Convert 0 values to NaNs, others to 1

    # Apply mask to CSM: values where mask is 1 remain, where mask is NaN become NaN
    masked_CSM = np.where(mask_resampled == 1, clipped_CSM_array, np.nan)

    # Update metadata and save masked CSM
    out_meta_CSM.update({
        "driver": "GTiff",
        "height": height,
        "width": width,
        "transform": clipped_CSM.transform,
        "dtype": 'float32'
    })

    masked_CSM = masked_CSM.astype(np.float32)

    # Save masked CSM
    output_path = os.path.join(path_to_data, date + "_masked_CSM.tif")
    with rasterio.open(output_path, "w", **out_meta_CSM) as dest:
        dest.write(masked_CSM, 1)  # Write the first band

    print(date, "calculate masked CSM done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate Derived Digital Terrain Model (DTM).")
    parser.add_argument("shapefile_path", type=str, help="Path to the shapefile used for masking or region-specific processing")
    parser.add_argument("date", type=str, help="Date string representing the directory to process")
    parser.add_argument("--subfolder", type=str, help="Optional subfolder under the date directory", default=None)
    
    args = parser.parse_args()
    main(args.shapefile_path, args.date, args.subfolder)
