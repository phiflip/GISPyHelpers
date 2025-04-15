# -*- coding: utf-8 -*-
"""
Created on Mon May 18 09:12:29 2020

@author: MinorNT
"""

#%%import packages
from scipy import ndimage as ndi
from rasterio.fill import fillnodata

import rasterio
import rasterio.plot

import matplotlib.pyplot as plt

import geopandas as gpd
from fiona.crs import from_epsg
from rasterio.mask import mask
from pyproj import CRS


if __name__ == "__main__":
    print("module_DTMmodel.py is being run directly")
else:
    print("module_DTMmodel.py was imported into this script")
    


def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def clip(shapefile, input_image):
    data = rasterio.open(input_image,
                         mode = 'r',
                         driver = 'GTiff',
                         count = None,
                         transform = None)
    
    #bbox = box(minx, miny, maxx, maxy)       
    geo = gpd.GeoDataFrame({'geometry': shapefile}, index=[0], crs=CRS.from_epsg(21781))
    geo = geo.to_crs(crs=data.crs.to_string())
    # print(geo)
    
    # Project the Polygon into same CRS as the grid
    # geo = geo.to_crs(crs=data.crs.data)
    
    coords = getFeatures(geo)
    # print(coords)
    # Clip the raster with Polygon
    
    out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)
    
    # Copy the metadata
    out_meta = data.meta.copy()
    # print(out_meta)

    # Parse EPSG code
    epsg_code = int(data.crs.data['init'][5:])
    # print(epsg_code)

    out_meta.update({"driver": "GTiff",
                  "height": out_img.shape[1],
                  "width": out_img.shape[2],
                  "transform": out_transform
                  #"crs": pycrs.parse.from_epsg_code(21781).to_proj4()
                  })
    
    return out_img, out_meta



# reference pixel size = 0.04m
def DTM_PixelSizeSensitive(DSM_as_array, pixelsize, plot):
    """
    

    Parameters
    ----------
    DSM_as_array : DSM_as_array with shape (channels, rows, cols)
    pixelsize : in meters, as float
    plot: True or False 

    Returns
    -------
    DTM_final : DTM as array with shape (rows, cols)

    """
    
    pixelsize_in_cm = round(pixelsize,3)*100

    DSM_as_array[DSM_as_array == -32767.0] = 'nan' #'-32767' kann nicht interpoliert werden!
    DSM_interpolated = fillnodata(DSM_as_array.copy(), mask=DSM_as_array, max_search_distance = int((4/pixelsize_in_cm)*80), smoothing_iterations=0) # interpolate 
    DSM_interpolated = DSM_interpolated[0].astype(float) # remove first argument (channels) to reach image friendly dimensions
    
    # find minimas

    DTM_minimas = ndi.minimum_filter(DSM_interpolated[:,:], size = int((4/pixelsize_in_cm)*38), mode='constant') 
    
    #interpolate again
    DTM_scnd_interpolated = fillnodata(DTM_minimas .copy(), mask=DTM_minimas, max_search_distance = int((4/pixelsize_in_cm)*25), smoothing_iterations=0) 
    
    # smoothing: window_width_in_pixels = 2*int(truncate*sigma + 0.5) + 1
    DTM_final = ndi.gaussian_filter(DTM_scnd_interpolated, sigma = (4/pixelsize_in_cm)*38, truncate = 1.5) # 
   
    DTM_final[DTM_final == 0.0] = 'nan'
    
    
    if plot == True:
        
        plt.figure("DSM_Reference")
        plt.imshow(DSM_as_array[0])
        plt.colorbar()

        plt.figure("DTM_Reference")
        plt.imshow(DTM_final)
        plt.colorbar()
    
    return DTM_final


def CTM_PixelSizeSensitive(CEM_as_array, pixelsize, plot):
    """
    
    Parameters
    ----------
    CEM_as_array : CEM_as_array with shape (channels, rows, cols)
    pixelsize : in meters, as float
    plot: True or False 

    Returns
    -------
    DTM_final : DTM as array with shape (rows, cols)

    """
    
    pixelsize_in_cm = round(pixelsize,3)*100
    
    CEM_as_array[CEM_as_array == -32767.0] = 'nan' #'-32767' kann nicht interpoliert werden!
    
    CEM_as_array=CEM_as_array*100 # not able to interpolate values smalle than 1

    CEM_interpolated = fillnodata(CEM_as_array.copy(), mask=CEM_as_array, max_search_distance = int((4/pixelsize_in_cm)*80), smoothing_iterations=0) # interpolate 
    CEM_interpolated = CEM_interpolated.astype(float)
    
    # find minimas
    CTM_minimas = ndi.minimum_filter(CEM_interpolated[:,:], size = int((4/pixelsize_in_cm)*50), mode='constant') # 50 malters

    
    #interpolate again
    CTM_scnd_interpolated = fillnodata(CTM_minimas.copy(), mask=CTM_minimas, max_search_distance = int((4/pixelsize_in_cm)*80), smoothing_iterations=0) 

    
    # smoothing: window_width_in_pixels = 2*int(truncate*sigma + 0.5) + 1
    CTM_final = ndi.gaussian_filter(CTM_scnd_interpolated, sigma = (4/pixelsize_in_cm)*76, truncate = 1.5) # 76 bei Malters
   
    CTM_final[CTM_final == 0.0] = 'nan'
    CTM_final = CTM_final/100
    
    if plot == True:
        

        
        plt.figure("CEM_Reference")
        plt.imshow(CEM_as_array)
        plt.colorbar()
        
        plt.figure("1st fill no data")
        plt.imshow(CEM_interpolated)
        plt.colorbar()

        plt.figure("CTM_Reference")
        plt.imshow(CTM_final)
        plt.colorbar()
    
    return CTM_final


