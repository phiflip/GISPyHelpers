# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:55:04 2019

@author: phiflip
"""
import os
os.chdir('G:/GISPyHelpers/Modules/')

import multichannel_index_definitions as mcvi
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import fiona
from pyproj import CRS
from shapely.geometry import shape

plt.close("all")
np.seterr(divide='ignore', invalid='ignore')

# Set path to python functions and data directories
os.chdir('G:/GISPyHelpers/GIS_Data_Examples/')

# Reading data and setting paths
date = "2020-06-03"

filename = date + "_allChannels_xy_transformed.tif"
path_to_data = date + "/Agisoft/Agi_EXPORT/"
read_allChannels = path_to_data + filename
path_to_shapefile = "./zz_Qgis/Shapefiles/Area_DSM.shp"

with fiona.open(path_to_shapefile, 'r') as shapefile:
    # Direct creation of CRS from EPSG code
    crs = CRS.from_epsg("21781")
    all_shapes = [shape(feat['geometry']) for feat in shapefile]
    shp_geom = all_shapes[0]  # Example, using the first geometry

# Read images without ROI
multiChannel_array, out_meta = mcvi.clip(shp_geom, read_allChannels)
multiChannel_array_trans = multiChannel_array.transpose((1, 2, 0))
blue, green, red, rededge, nir, alpha = [
    multiChannel_array_trans[:, :, i].astype(float)/32768 for i in range(6)]

# Initialization of channels and metadata
blue = multiChannel_array_trans[:, :, 0].astype(float)/32768
green = multiChannel_array_trans[:, :, 1].astype(float)/32768
red = multiChannel_array_trans[:, :, 2].astype(float)/32768
rededge = multiChannel_array_trans[:, :, 3].astype(float)/32768
nir = multiChannel_array_trans[:, :, 4].astype(float)/32768
alpha = multiChannel_array_trans[:, :, 5].astype(float)

# Mapping of channel names to array
channels = {
    'blue': blue,
    'green': green,
    'red': red,
    'rededge': rededge,
    'nir': nir,
    'alpha': alpha
}

# Defined list of indices to be calculated
selected_indices = [
    "NDVI",
    "WDRVI",
    # "GNDVI",
    # "SAVI",
    # "GCI",
    # "RCI",
    # "NDRE",
    # "GRVI",
    # "MGRVI",
    # "RGBVI"
]

#################################################################################
# Create a mask based on a NDVI threshold
#################################################################################

# Define the threshold value for the NDVI mask
ndvi_threshold = 0.7

# Calculate the NDVI data
ndvi_mask = mcvi.ndvi(nir, red)
ndvi_mask = np.expand_dims(ndvi_mask, axis=2)  # Expand dimensions

# Create a binary mask: Values <= ndvi_threshold become 0, values > ndvi_threshold become 255
binary_mask = np.where(ndvi_mask > ndvi_threshold,
                       np.nan, 0).astype(np.float64)

# Visualize the mask
plt.figure("Binary NDVI Mask")
# Gray color map for better clarity
plt.imshow(binary_mask[:, :, 0], cmap='gray')
plt.colorbar()
plt.show()

# Retransform (bands, rows, cols)
binary_mask_geo_trans = binary_mask.transpose((2, 0, 1))

# Define metadata for GeoTIFF storage
out_meta.update({"driver": "GTiff",
                 "count": 1,
                 "dtype": rasterio.float64})

# Save as GeoTIFF
output_path = f"{path_to_data}/VIs/{date}_Mask.tif"
with rasterio.open(output_path, "w", **out_meta) as dest:
    dest.write(binary_mask_geo_trans)

print(f"MASK saved at {output_path}")

#################################################################################
# Visualize the different vegetation indices
#################################################################################

# Definition of available indices and required channels
available_indices = {
    "NDVI": (mcvi.ndvi, ['nir', 'red']),
    # Alpha parameter is part of the function parameters
    "WDRVI": (mcvi.wdrvi, ['nir', 'red', 0.2]),
    "GNDVI": (mcvi.gndvi, ['nir', 'green']),
    "SAVI": (mcvi.savi, ['nir', 'red']),
    "GCI": (mcvi.gci, ['nir', 'green']),
    "RCI": (mcvi.rci, ['nir', 'rededge']),
    "NDRE": (mcvi.ndre, ['nir', 'rededge']),
    "GRVI": (mcvi.grvi, ['red', 'green']),
    "MGRVI": (mcvi.mgrvi, ['red', 'green']),
    "RGBVI": (mcvi.rgbvi, ['red', 'green','blue'])

}
# Processing of the selected indices
for index in selected_indices:
    if index in available_indices:
        func, params = available_indices[index]
        # Passing the corresponding channels and optional parameters to the function
        # Expects a third parameter which is a float (alpha value)
        if len(params) == 3 and isinstance(params[2], float):
            result = func(channels[params[0]], channels[params[1]], params[2])
        else:
            result = func(*[channels[channel] for channel in params])
        result = np.expand_dims(result, axis=2)

        # Plot and save the results
        mcvi.plotVI(result, index, "RdYlGn", quantile=0.5)
        out_meta.update({"driver": "GTiff", "count": 1,
                        "dtype": rasterio.float64})
        result_geo_trans = result.transpose((2, 0, 1))
        output_path = f"{path_to_data}/VIs/{date}_{index}.tif"
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(result_geo_trans)
        print(f"{index} calculated and saved at {output_path}.")
    else:
        print(f"{index} is not a valid index.")


print(f"{date} Visualize VIs done")
