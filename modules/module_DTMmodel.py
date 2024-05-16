import numpy as np
from scipy import ndimage as ndi
from rasterio.fill import fillnodata
import rasterio
import rasterio.plot
import matplotlib.pyplot as plt
import geopandas as gpd
from pyproj import CRS
from rasterio.mask import mask

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

def clip(shapefile, input_image):
    data = rasterio.open(input_image)
    
    geo = gpd.GeoDataFrame({'geometry': shapefile}, index=[0], crs=CRS.from_epsg(21781))
    geo = geo.to_crs(crs=data.crs.to_string())
    
    coords = getFeatures(geo)
    
    out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)
    
    out_meta = data.meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": out_img.shape[1],
                     "width": out_img.shape[2],
                     "transform": out_transform
                     })
    
    return out_img, out_meta

# Reference pixel size = 0.04m
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
    
    pixelsize_in_cm = round(pixelsize, 3) * 100

    DSM_as_array[DSM_as_array == -32767.0] = np.nan  # '-32767' kann nicht interpoliert werden!
    DSM_interpolated = fillnodata(DSM_as_array.copy(), mask=DSM_as_array, max_search_distance=int((4 / pixelsize_in_cm) * 80), smoothing_iterations=0)
    DSM_interpolated = DSM_interpolated[0].astype(float)
    
    # Find minimas
    DTM_minimas = ndi.minimum_filter(DSM_interpolated[:, :], size=int((4 / pixelsize_in_cm) * 38), mode='constant') 
    
    # Bereinigen Sie das Array vor der Interpolation
    DTM_minimas_cleaned = np.nan_to_num(DTM_minimas, nan=-32767.0)
    
    # Interpolate again
    DTM_scnd_interpolated = fillnodata(DTM_minimas_cleaned.copy(), mask=DTM_minimas_cleaned != -32767.0, max_search_distance=int((4 / pixelsize_in_cm) * 25), smoothing_iterations=0) 
    # Smoothing
    DTM_final = ndi.gaussian_filter(DTM_scnd_interpolated, sigma=(4 / pixelsize_in_cm) * 38, truncate=1.5)
   
    DTM_final[DTM_final == 0.0] = np.nan
    
    if plot:
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
    CTM_final : CTM as array with shape (rows, cols)
    """
    
    pixelsize_in_cm = round(pixelsize, 3) * 100
    
    CEM_as_array[CEM_as_array == -32767.0] = np.nan  # '-32767' kann nicht interpoliert werden!
    
    CEM_as_array = CEM_as_array * 100  # Not able to interpolate values smaller than 1

    CEM_interpolated = fillnodata(CEM_as_array.copy(), mask=CEM_as_array, max_search_distance=int((4 / pixelsize_in_cm) * 80), smoothing_iterations=0)
    CEM_interpolated = CEM_interpolated.astype(float)
    
    # Find minimas
    CTM_minimas = ndi.minimum_filter(CEM_interpolated[:, :], size=int((4 / pixelsize_in_cm) * 50), mode='constant')
    
    # Bereinigen Sie das Array vor der Interpolation
    CTM_minimas_cleaned = np.nan_to_num(CTM_minimas, nan=-32767.0)
    
    # Interpolate again
    CTM_scnd_interpolated = fillnodata(CTM_minimas_cleaned.copy(), mask=CTM_minimas_cleaned != -32767.0, max_search_distance=int((4 / pixelsize_in_cm) * 80), smoothing_iterations=0)
    
    # Smoothing
    CTM_final = ndi.gaussian_filter(CTM_scnd_interpolated, sigma=(4 / pixelsize_in_cm) * 76, truncate=1.5)
   
    CTM_final[CTM_final == 0.0] = np.nan
    CTM_final = CTM_final / 100
    
    if plot:
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
