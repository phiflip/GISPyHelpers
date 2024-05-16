# -*- coding: utf-8 -*-
"""
Created on Mon May 18 09:12:29 2020

Author: phiflip
"""

import os
import sys
import rasterio
import rasterio.plot
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters
import fiona
# from fiona.crs import from_epsg
from scipy.stats import norm
from shapely.geometry import shape
import argparse

# Add the path to your custom module
sys.path.append('G:/GISPyHelpers/modules')
import module_DTMmodel as DTMm

# Argumente von der Befehlszeile einlesen
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--date', type=str, help='Date for the filename')
parser.add_argument('--pixel_size_factor', type=float, help='Factor for pixel size')
args = parser.parse_args()

date = args.date
pixelSizeX_factor = args.pixel_size_factor


# os.chdir('G:/Kernza/')

#################################################################################
#%% Read data and print details
#################################################################################
filename = date+"_DSM_xy_transformed.tif"

###################################################################################

path_to_data = date+"/Agisoft/Agi_EXPORT/"

read_DSM = path_to_data+filename

#################################################################################
#%% Read DSM-ShapeFile
#################################################################################

shapefile = fiona.open('./zz_Qgis/Shapefiles/Kernza_DSM.shp')
#first feature of the shapefile
all_shapes = []
shp_id_ls = []
num = 1

with shapefile as input:
    for feat in input:
        print(feat)
        shp_id = feat['properties']['id']
        print(shp_id)
        shp_geom = shape(feat['geometry'])
        print(shp_geom)
        all_shapes.append(shp_geom)
        shp_id_ls.append(shp_id)

shp_geom = all_shapes[num-1]

###########################################################################################################
#  clip DEMs
###########################################################################################################

clipped_array_DSM_1, out_meta = DTMm.clip(shp_geom, read_DSM) 
clipped_array_DSM_2, out_meta = DTMm.clip(shp_geom, read_DSM) 

data_dir = '.\\zz_PythonCodes\\__temp_data_dir'

#%% get met adata

affine = out_meta["transform"]
pixelSizeX = affine[0] * pixelSizeX_factor # mit Faktor multiplizieren
pixelSizeY =-affine[4] * pixelSizeX_factor

#%% Calculate DTM

DTM = DTMm.DTM_PixelSizeSensitive(clipped_array_DSM_1, pixelSizeX, plot=True)

#%%
clipped_array_DSM_2[clipped_array_DSM_2 == -32767.0] = 'nan'
clipped_array_DSM_2_gauss = filters.gaussian(clipped_array_DSM_2, sigma = 0)

#################################################################################         
#%% Create CEM
#################################################################################
rows1 = DTM.shape[0]
rows2 = len(clipped_array_DSM_2_gauss[0])

cols1 = DTM.shape[1]
cols2 = len((clipped_array_DSM_2_gauss[0])[0])

upper_clim = np.min([cols1,cols2])
upper_rlim = np.min([rows1,rows2])

CEM = (clipped_array_DSM_2_gauss[0])[0:upper_rlim,0:upper_clim] - DTM[0:upper_rlim,0:upper_clim] # Crop Elevation Model

CEM[CEM[:,:] >= 5.5] = 'nan'
CEM[CEM[:,:] <= -0.9] = 'nan'

# mu = np.nanmean(CEM.flatten())
# sigma = np.nanstd(CEM.flatten())

# plt.figure("CEM (DSM-DTM)")
# plt.imshow(CEM, cmap='RdYlGn')
# clb = plt.colorbar()
# clb.set_label('[m]')
# plt.clim(-0.4,2.8)

##############################################################################
# Histogram
# the histogram of the data
# plt.figure("CEM")
# n, bins, patches = plt.hist(CEM.flatten(),80, density=1, facecolor='red', alpha=0.75, label =r'$\mu = %.4f \ m,\  \sigma = %.4f$' %(mu, sigma))

# # add a 'best fit' line
# y = norm.pdf(bins, mu, sigma)
# l = plt.plot(bins, y, 'r--', linewidth=2)
# #plot
# plt.xlabel('CEM [m]')
# plt.ylabel('Probability')
# plt.xlim(-0.4, 2.8)
# plt.grid(True)
# plt.legend()

#################################################################################
# Plot the Cross section of the CEM
#################################################################################

# plt.figure("Cross section of CEM")
# # plt.plot((DTM[int(upper_rlim/2), : ]), label="horiz. cut DTM")#
# # plt.plot((clipped_array_DSM_2_gauss[0, int(upper_rlim/2), :]), label="horiz. cut DSM")

# plt.plot((DTM[:, int(upper_clim/1.2)]), label="vert. cut DTM")#, 
# plt.plot((clipped_array_DSM_2_gauss[0,:,int(upper_clim/1.2)]), label="vert. cut DSM")

# plt.xlabel('px')
# plt.ylabel('m.a.s.l')

# plt.legend()

#################################################################################         
#%% Create CSM
#################################################################################

#%% Calculate CTM

CTM = DTMm.CTM_PixelSizeSensitive(CEM, pixelSizeX, plot=True)

#%%

# Crop Surface Model (CSM)
CSM = CEM[0:upper_rlim,0:upper_clim] - CTM[0:upper_rlim,0:upper_clim] 

# CSM[CSM[:,:] >= 0.5] = 'nan'

# mu_CSM = np.nanmean(CSM.flatten())
# sigma_CSM = np.nanstd(CSM.flatten())

# plt.figure("CSM")
# plt.imshow(CSM, cmap='RdYlGn')
# clb = plt.colorbar()
# clb.set_label('[m]')
# plt.clim(-0.5,2.9)

##############################################################################
# Histogram
# the histogram of the data
# plt.figure("CSM Histogram")
# n, bins1, patches = plt.hist(CSM.flatten(), 80, density=1, facecolor='red', alpha=0.75, label =r'$\mu = %.4f \ m,\  \sigma = %.4f$' %(mu_CSM, sigma_CSM))

# # add a 'best fit' line
# y = norm.pdf(bins1, mu_CSM, sigma_CSM)
# l = plt.plot(bins1, y, 'r--', linewidth=2)
# #plot
# plt.xlabel('CSM [m]')
# plt.ylabel('Probability')
# plt.xlim(-0.4, 2.7)
# plt.grid(True)
# plt.legend()

#################################################################################
# Plot the Cross section of the CEM
#################################################################################

# plt.figure("Cross section of CSM")
# plt.plot((CEM[:, int(upper_clim/2)]), label="vertical. cut CEM")
# plt.plot((CTM[:, int(upper_clim/2)]), label="vertical. cut CTM")

# # plt.plot((CTM[:, int(upper_clim/2)]), label="vert. cut CTM")#, 
# # plt.plot((CSM[:,int(upper_clim/2)]), label="vert. cut CSM")

# plt.xlabel('px')
# plt.ylabel('m.a.s.l')

# plt.legend()

###############################################################################################################################################################################
#%% Save DSM, DTM and CSM as GeoTiff
#################################################################################

out_meta.update({"driver": "GTiff"})

# Save clipped DSM
with rasterio.open(path_to_data + date +'_clipped_DSM.tif', "w", **out_meta) as dest: # "w" : open in writing mode
    #print(dest.bounds)
    dest.write(clipped_array_DSM_2_gauss) 

# Save clipped DTM
DTM = np.expand_dims(DTM, axis=2) # 3 dim image from [rows,cols] to[rows,cols,bands]
DTM_trans = DTM.transpose((2, 0, 1))
DTM_trans32 = np.float32(DTM_trans)

with rasterio.open(path_to_data + date +'_clipped_DTM.tif', "w", **out_meta) as dest: # "w" : open in writing mode
    #print(dest.bounds)
    dest.write(DTM_trans32) 
    
# Save clipped CSM
CSM= np.expand_dims(CSM, axis=2) # 3 dim image from [rows,cols] to[rows,cols,bands]
CSM_trans = CSM.transpose((2, 0, 1))
CSM_trans32 = np.float32(CSM_trans)


#%%

with rasterio.open(path_to_data + date +'_clipped_CSM.tif', "w", **out_meta) as dest: # "w" : open in writing mode
    #print(dest.bounds)
    dest.write(CSM_trans32) 
print(date, "calculate CSM done")


