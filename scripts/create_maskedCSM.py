# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:55:04 2019

@author: bfhNT



import cv2


"""
import rasterio
import rasterio.plot
import numpy as np
np.seterr(divide='ignore', invalid='ignore')

import matplotlib.pyplot as plt
import os
import fiona
from rasterio.enums import Resampling
from shapely.geometry import shape     

#Set path to python functions
os.chdir('G:/00_Codes/')
# file MultiChannel_VegIndices.py


plt.close("all")

os.chdir('G:/fibl/Weizen')

#################################################################################
#%% Read data and print details
#################################################################################

date = [
       # "2024-03-22"
       # "2024-03-26"
       # "2024-04-04"
        # "2024-04-11"      
        # "2024-04-18",
        # "2024-04-24",
        # "2024-04-30"
        "2024-05-23"
        ]

date = date[-1]


filename = date+"_allChannels_xy_transformed.tif"


#########################################################

###################################################################################
date = filename[0:10]

path_to_data = date+"/Agisoft/Agi_EXPORT/"

read_allChannels = path_to_data+filename

path_to_shapefile = "./zz_Qgis/Shapefiles/Hackfolgen_DSM.shp"



#################################################################################
#%% Read ShapeFile
#################################################################################

shapefile = fiona.open(path_to_shapefile)
# print(shape.schema)
#first feature of the shapefile
all_shapes = []
shp_id_ls = []
num = 1

with shapefile as input:
    for feat in input:
        shp_id = feat['properties']['id']
        # print(shp_id)
        shp_geom = shape(feat['geometry'])
        # print(shp_geom)
        all_shapes.append(shp_geom)
        shp_id_ls.append(shp_id)

shp_geom = all_shapes[num-1]


#################################################################################
#%% Mask for CSM
#################################################################################




# Read NDVI mask and CSM
ndvi_mask_path = path_to_data +"VIs/" +date + "_MASK.tif"
csm_path = path_to_data + date + "_clipped_CSM.tif"

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
output_path = path_to_data + date + "_masked_CSM.tif"
with rasterio.open(output_path, "w", **out_meta_CSM) as dest:
    dest.write(masked_CSM, 1)  # Write the first band

print(date, "calculate masked CSM done")
