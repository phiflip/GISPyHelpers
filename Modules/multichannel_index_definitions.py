# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:47:31 2020

@author: phiflip
"""
import rasterio
import rasterio.plot
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from rasterio.mask import mask
import cv2
import json

#  Clipping


def getFeatures(gdf):
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def clip(shapefile, input_image):
    data = rasterio.open(input_image)

    # Convert shapefile to GeoDataFrame
    geo = gpd.GeoDataFrame({'geometry': [shapefile]}, crs="EPSG:21781")

    # Project the GeoDataFrame to match the CRS of the raster
    geo = geo.to_crs(crs=data.crs)

    # Extract the geometry from the GeoDataFrame
    coords = getFeatures(geo)

    # Clip the raster with the geometry
    out_img, out_transform = mask(dataset=data, shapes=coords, crop=True)

    # Copy the metadata
    out_meta = data.meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": out_img.shape[1],
                     "width": out_img.shape[2],
                     "transform": out_transform})

    return out_img, out_meta


#
# NDVI calculate
def ndvi(nir, red):
    ndvi = (nir-red)/(nir+red)
    return ndvi
#
# WDRVI calculate
# (https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2003GL019034)
# https://geopard.tech/blog/tpost/kc9y2x96kv-which-vegetation-index-is-better-to-use


def wdrvi(nir, red, alpha):
    wdrvi = (alpha*nir-red)/(alpha*nir+red)
    return wdrvi

# gNDVI calculate


def gndvi(nir, green):
    gndvi = (nir-green)/(nir+green)
    return gndvi

# NDRE calculate


def ndre(nir, rededge):
    ndre = (nir-rededge)/(nir+rededge)
    return ndre

# SAVI calculate


def savi(nir, red):
    savi = ((nir-red)/(nir+red+0.5))*1.5
    return savi
#  Green Chlorophyll Index GCI


def gci(nir, green):
    gci = (nir/green)-1
    gci[np.isinf(gci)] = np.nan
    return gci
#  Red-Edge Chlorophyll Index RCI


def rci(nir, rededge):
    rci = (nir/rededge)-1
    rci[np.isinf(rci)] = np.nan
    return rci

#  Red Edge Simple Ratio


def resratio(nir, rededge):
    resratio = (nir/rededge)
    resratio[np.isinf(resratio)] = np.nan
    return resratio

#  Medium Resolution Imaging Spectrometer (MERIS) Terrestrial Chlorophyll Index (MRCI)


def mrci(nir, red, rededge):
    mrci = (nir-rededge)/(rededge+red)
    mrci[np.isinf(mrci)] = np.nan
    return mrci
#  Core Red Edge Triangular Vegetation Index


def cretvi(nir, green, rededge):
    cretvi = (100*(nir-rededge)) - (10*(nir-green))
    cretvi[np.isinf(cretvi)] = np.nan
    return cretvi
#  Red Difference Index


def reddi(nir, red):
    reddi = nir-red
    reddi[np.isinf(reddi)] = np.nan
    return reddi
#  Canopy Chlorophyll Concentration Index


def ccci(nir, rededge, ndvi):
    ccci = ((nir-rededge)/(nir+rededge))/ndvi
    ccci[np.isinf(ccci)] = np.nan
    return ccci
#  Green Difference Index


def greendi(nir, green):
    greendi = nir-green
    greendi[np.isinf(greendi)] = np.nan
    return greendi
#  Green Ratio Simple Index


def greensratio(nir, green):
    greensratio = (nir/green)
    greensratio[np.isinf(greensratio)] = np.nan
    return greensratio

#
# GRVI Green and Red ratio Vegetation Index calculate


def grvi(red, green):
    grvi = np.divide((green - red), (green + red))
    return grvi

#
# MGRVI calculate


def mgrvi(red, green):
    mgrvi = np.divide((green**2 - red**2), (green**2 + red**2))
    return mgrvi

################################################################################################
#  RGB Indices
################################################################################################

#


def white_balance(rgb_img):
    result = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - \
        ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - \
        ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result
#
# RGBVI calculate


def rgbvi(red, green, blue):
    red = red
    green = green
    blue = blue
    rgbvi = (green**2 - (blue*red)) / (green**2 + (blue*red))
    return rgbvi
#
# VARI calculate


def vari(red, green, blue):
    red = red/(red+green+blue)
    green = green/(red+green+blue)
    blue = blue/(red+green+blue)
    vari = np.divide((green - red), (green + red - blue))
    vari[np.isinf(vari)] = np.nan
    return vari
#
# GLI calculate


def gli(red, green, blue):
    red = np.divide(red, (red+green+blue))
    green = np.divide(green, (red+green+blue))
    blue = np.divide(blue, (red+green+blue))
    gli = np.divide(((green - red)+(green-blue)), (2*green + (red - blue)))
    gli[np.isinf(gli)] = np.nan
    return gli
#
   # VDVI calculate


def vdvi(red, green, blue):
    vdvi = np.divide(2*green + (- red - blue), 2*green + (red + blue))
    vdvi[np.isinf(vdvi)] = np.nan
    return vdvi
#  Excessive Green Index


def egi(red, green, blue):
    r = np.divide(red, (red+green+blue))
    g = np.divide(green, (red+green+blue))
    b = np.divide(blue, (red+green+blue))
    egi = (2*g*r) - b
    egi[np.isinf(egi)] = np.nan
    return egi
#  Excessive Red Index


def eri(red, green, blue):
    r = np.divide(red, (red+green+blue))
    b = np.divide(blue, (red+green+blue))
    eri = (1.4*r) - b
    eri[np.isinf(eri)] = np.nan
    return eri


##############################################################################################
# ----------------------------------------------------------------------------------------
##############################################################################################


def plotVI(array, figname, cmap, quantile):
    plt.figure(figname)
    plt.title(figname)
    plt.imshow(array[:, :, 0], cmap=cmap)
    plt.colorbar()
    plt.clim(np.nanquantile(array[:, :, 0], quantile/100.),
             np.nanquantile(array[:, :, 0], 1-quantile/100.))
    return
