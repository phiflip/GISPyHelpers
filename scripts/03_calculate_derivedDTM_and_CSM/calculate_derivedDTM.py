# -*- coding: utf-8 -*-
"""
Created on Mon May 18 09:12:29 2020

Updated for additional subfolder and shapefile handling
"""

import os
import sys
import rasterio
import rasterio.plot
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters
import fiona
from scipy.stats import norm
from shapely.geometry import shape
import argparse

# Add the path to your custom module

sys.path.append('G:/GISPyHelpers/modules')
import module_DTMmodel as DTMm

# sys.path.append("D:/aa_Weidemanagement/P4_Multispectral/00_Codes")
# import module_DTMmodel_vfibl as DTMm #muss noch angepasst werden - die 10fache Pixelgrösse passt bei sehr hohen Beständen. nicht aber kleinen.


# Argumente von der Befehlszeile einlesen
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--date', type=str,
                    help='Date for the filename', required=True)
parser.add_argument('--pixel_size_factor', type=float,
                    help='Factor for pixel size - the higher the factor, the smaller the moving windows', required=True)
parser.add_argument('--subfolder', type=str,
                    help='Subfolder within the date directory', required=False)
parser.add_argument('--shapefile', type=str,
                    help='Path to the shapefile', required=True)
args = parser.parse_args()

date = args.date
pixelSizeX_factor = args.pixel_size_factor
subfolder = args.subfolder
shapefile_path = args.shapefile

# Define the base path pattern
if subfolder:
    path_to_data = os.path.join(date, subfolder, "Agisoft", "Agi_EXPORT")
else:
    path_to_data = os.path.join(date, "Agisoft", "Agi_EXPORT")

#################################################################################
# Read data and print details
#################################################################################
filename = date + "_DSM_xy_transformed.tif"
read_DSM = os.path.join(path_to_data, filename)

#################################################################################
# Read DSM-ShapeFile
#################################################################################

shapefile = fiona.open(shapefile_path)
# first feature of the shapefile
all_shapes = []
shp_id_ls = []
num = 1

with shapefile as input:
    for feat in input:
        shp_id = feat['properties']['id']
        shp_geom = shape(feat['geometry'])
        all_shapes.append(shp_geom)
        shp_id_ls.append(shp_id)

shp_geom = all_shapes[num-1]

print("Shapefile loaded!")
###########################################################################################################
#  clip DEMs
###########################################################################################################

clipped_array_DSM_1, out_meta = DTMm.clip(shp_geom, read_DSM)
clipped_array_DSM_2, out_meta = DTMm.clip(shp_geom, read_DSM)

data_dir = '.\\zz_PythonCodes\\__temp_data_dir'

# get metadata
affine = out_meta["transform"]
pixelSizeX = affine[0] * pixelSizeX_factor  # mit Faktor multiplizieren
pixelSizeY = -affine[4] * pixelSizeX_factor

# Calculate DTM
print("Started DTM calculation ...")
DTM = DTMm.DTM_PixelSizeSensitive(clipped_array_DSM_1, pixelSizeX, plot=True)
print("DTM created!")

clipped_array_DSM_2[clipped_array_DSM_2 == -32767.0] = np.nan
clipped_array_DSM_2_gauss = filters.gaussian(clipped_array_DSM_2, sigma=0)

# Create CEM
rows1 = DTM.shape[0]
rows2 = len(clipped_array_DSM_2_gauss[0])

cols1 = DTM.shape[1]
cols2 = len((clipped_array_DSM_2_gauss[0])[0])

upper_clim = np.min([cols1, cols2])
upper_rlim = np.min([rows1, rows2])

CEM = (clipped_array_DSM_2_gauss[0])[
    # Crop Elevation Model
    0:upper_rlim, 0:upper_clim] - DTM[0:upper_rlim, 0:upper_clim]

CEM[CEM[:, :] >= 5.5] = np.nan
CEM[CEM[:, :] <= -0.9] = np.nan

# Calculate CTM
print("Started CTM calculation ...")
CTM = DTMm.CTM_PixelSizeSensitive(CEM, pixelSizeX, plot=True)
print("CTM created!")

# Crop Surface Model (CSM)
print("Started CSM calculation ...")
CSM = CEM[0:upper_rlim, 0:upper_clim] - CTM[0:upper_rlim, 0:upper_clim]
print("CSM created!")

# Save DSM, DTM and CSM as GeoTiff
out_meta.update({"driver": "GTiff"})

# Save clipped DSM
# "w" : open in writing mode
with rasterio.open(os.path.join(path_to_data, f'{date}_clipped_DSM.tif'), "w", **out_meta) as dest:
    dest.write(clipped_array_DSM_2_gauss)

# Save clipped DTM
# 3 dim image from [rows,cols] to[rows,cols,bands]
DTM = np.expand_dims(DTM, axis=2)
DTM_trans = DTM.transpose((2, 0, 1))
DTM_trans32 = np.float32(DTM_trans)

# "w" : open in writing mode
with rasterio.open(os.path.join(path_to_data, f'{date}_clipped_DTM.tif'), "w", **out_meta) as dest:
    dest.write(DTM_trans32)

# Save clipped CSM
# 3 dim image from [rows,cols] to[rows,cols,bands]
CSM = np.expand_dims(CSM, axis=2)
CSM_trans = CSM.transpose((2, 0, 1))
CSM_trans32 = np.float32(CSM_trans)

# "w" : open in writing mode
with rasterio.open(os.path.join(path_to_data, f'{date}_clipped_CSM.tif'), "w", **out_meta) as dest:
    dest.write(CSM_trans32)
print(date, f"done check here: path_to_data, {date}_clipped_CSM.tif")
