# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:55:04 2019

@author: bfhNT

import cv2

"""
import numpy as np
np.seterr(divide='ignore', invalid='ignore')

import matplotlib.pyplot as plt
import os
import fiona
from shapely.geometry import shape     
import pandas as pd
import sys
import json

module_directory = 'G:/GISPyHelpers/modules/'
if module_directory not in sys.path:
    sys.path.append(module_directory)

import VegIndices_calculations_for_dataframe_withMask as vegicalcs

####################################################

plt.close("all")

os.chdir('G:/fibl/Weizen/')

#################################################################################
# Read data and print details
##############################################################################.###

###################################################################################
# date = "2024-04-04"
ndvi_mask_threshold = 0.8


json_file_path = './shifts.json'

with open(json_file_path, 'r') as file:
    data = json.load(file)

# Extrahiere nur die Datumswerte (Schlüssel) aus 'shifts'
dates = list(data['shifts'].keys())


for date in dates:
    print(f"Verarbeite Datum: {date}")

    filename = date+"_allChannels_xy_transformed.tif"
    
    path_to_data = date+"/Agisoft/Agi_EXPORT/"
    path_to_csv = "./zz_Resultate/"+date+"_Hackfolgen_Weizen.csv"
    path_to_images = date+"/Fotos/"
    
    read_allChannels = path_to_data+filename
    
    #################################################################################
    # Read ShapeFile
    #################################################################################
    
    shapefile = fiona.open('./zz_Qgis/Shapefiles/Hackfolgen_Streifen_buffered.shp')
    
    all_shapes = []
    shp_id_ls = []
    shp_block_ls = []
    shp_tillage_ls = []
    shp_fert_ls = []
    shp_plot_ls = []
    shp_blocktill_ls = []
    shp_verfahren_ls = []
    
    
    
    with shapefile as input:
        for feat in input:
            shp_id = feat['properties']['id']
            shp_block = feat['properties']['Block']
            shp_tillage = feat['properties']['Tillage']
            shp_fert = feat['properties']['Fert']
            shp_plot = feat['properties']['Plot']
            shp_blocktill = feat['properties']['Block_Till']
            shp_verfahren = feat['properties']['Verfahren']
            shp_geom = shape(feat['geometry'])
            all_shapes.append(shp_geom)
            shp_id_ls.append(shp_id)
            shp_block_ls.append(shp_block)
            shp_tillage_ls.append(shp_tillage)
            shp_fert_ls.append(shp_fert)
            shp_plot_ls.append(shp_plot)
            shp_blocktill_ls.append(shp_blocktill)
            shp_verfahren_ls.append(shp_verfahren)
    
    
    
    # Berechnung der Vegetationsindizes für das DataFrame
    final_df = vegicalcs.vi_calcs_for_df(
        all_shapes,
        shp_id_ls,
        shp_block_ls,
        shp_tillage_ls,
        shp_fert_ls,
        shp_plot_ls,
        shp_blocktill_ls,
        shp_verfahren_ls,
        read_allChannels,
        path_to_images,
        cameratype=0,
        ndvi_mask_threshold=ndvi_mask_threshold
        )
    
    
    date_ls = [date] * len(shp_id_ls)
    
    additional_columns_df = pd.DataFrame({
        'date': date_ls,  
        'ID': shp_id_ls,
        'block': shp_block_ls,
        'tillage': shp_tillage_ls,
        'fert': shp_fert_ls,
        'plot': shp_plot_ls,
        'block_till': shp_blocktill_ls,
        'hoeing': shp_verfahren_ls
    })
    
    # Setze die Indexe beider DataFrames zurück
    final_df.reset_index(drop=True, inplace=True)
    additional_columns_df.reset_index(drop=True, inplace=True)
    
    # Füge die neuen Spalten vorne an das existierende DataFrame an
    final_df = pd.concat([additional_columns_df, final_df], axis=1)
    
    # Das Original CSV-File laden
    df_csv = pd.read_csv(path_to_csv, index_col='STR')
    
    # Die DataFrames NICHT zusammenführen, sondern separat speichern
    # Speichere die Ergebnisse der Vegetationsindizes in einer neuen CSV-Datei
    final_df_path = "./zz_Resultate/"+date+"_VIs.csv"
    final_df.to_csv(final_df_path, float_format="%.5f")
    
    print(f"{date} done. Vegetationsindizes gespeichert unter: {final_df_path}")
    
    
