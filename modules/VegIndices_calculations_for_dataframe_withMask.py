from matplotlib import pylab as plt
import numpy.ma as ma
import pandas as pd
import PIL.ExifTags
import glob
import numpy as np
import os
os.chdir('G:/GISPyHelpers/modules/')
import multichannel_index_definitions as mcvi

# file MultiChannel_VegIndices.py

#%% VegIndices calculations for dataframe

print("calculating VIs - don't forget to check your NDVI threshold")
def vi_calcs_for_df(

    all_shapes,
    shp_id_ls,
    # shp_block_ls,
    # shp_tillage_ls,
    # shp_fert_ls,
    # shp_plot_ls,
    # shp_blocktill_ls,
    # shp_verfahren_ls,
    read_allChannels,
    path_to_images,
    cameratype,
    ndvi_mask_threshold=0.0,
):

    

    green_mean_ls = []
    green_med_ls = []
    green_std_ls = []

    red_mean_ls = []
    red_med_ls = []
    red_std_ls = []

    rededge_mean_ls = []
    rededge_med_ls = []
    rededge_std_ls = []

    nir_mean_ls = []
    nir_med_ls = []
    nir_std_ls = []

    ndvi_mean_ls = []
    ndvi_med_ls = []
    ndvi_std_ls = []

    wdrvi_mean_ls = []
    wdrvi_med_ls = []
    wdrvi_std_ls = []

    gndvi_mean_ls = []
    gndvi_med_ls = []
    gndvi_std_ls = []

    savi_mean_ls = []
    savi_med_ls = []
    savi_std_ls = []

    gci_mean_ls = []
    gci_med_ls = []
    gci_std_ls = []

    rci_mean_ls = []
    rci_med_ls = []
    rci_std_ls = []

    resratio_mean_ls = []
    resratio_med_ls = []
    resratio_std_ls = []

    mrci_mean_ls = []
    mrci_med_ls = []
    mrci_std_ls = []

    cretvi_mean_ls = []
    cretvi_med_ls = []
    cretvi_std_ls = []

    reddi_mean_ls = []
    reddi_med_ls = []
    reddi_std_ls = []

    greendi_mean_ls = []
    greendi_med_ls = []
    greendi_std_ls = []

    greensratio_mean_ls = []
    greensratio_med_ls = []
    greensratio_std_ls = []

    ndre_mean_ls = []
    ndre_med_ls = []
    ndre_std_ls = []

    grvi_mean_ls = []
    grvi_med_ls = []
    grvi_std_ls = []

    mgrvi_mean_ls = []
    mgrvi_std_ls = []
    mgrvi_med_ls = []

    month_ls = []
    hour_ls = []
    # shutterSpeed_avg_ls = []
    counter = 0
    for shp_geom in all_shapes:
        counter = counter+1

        ###########################################################################################################
        # Read Images without ROI (shapeFile)
        ###########################################################################################################
        multiChannel_array, out_meta = mcvi.clip(shp_geom, read_allChannels)

        #################################################################################
        #%% Define Shape with shapely to do calculations on the same area with the same dimensions
        #################################################################################

        multiChannel_array_trans = multiChannel_array.transpose((1, 2, 0))

        # Why divide by 32768?
        # Reference: https://agisoft.freshdesk.com/support/solutions/articles/31000148780-micasense-rededge-mx-processing-workflow-including-reflectance-calibration-in-agisoft-metashape-pro
        # Agisoft exports 16-bit TIFFs; dividing by 32768 normalizes the reflectance values to a 0–1 range.
        
        if cameratype == 0:  # dji

            blue = multiChannel_array_trans[:, :, 0].astype(float)/32768
            green = multiChannel_array_trans[:, :, 1].astype(float)/32768
            red = multiChannel_array_trans[:, :, 2].astype(float)/32768
            rededge = multiChannel_array_trans[:, :, 3].astype(float)/32768
            nir = multiChannel_array_trans[:, :, 4].astype(float)/32768
            # alpha = multiChannel_array_trans[:,:,4].astype(float)

        elif cameratype == 1:  # sequoia
            green = multiChannel_array_trans[:, :, 0].astype(float)/32768
            red = multiChannel_array_trans[:, :, 1].astype(float)/32768
            rededge = multiChannel_array_trans[:, :, 2].astype(float)/32768
            nir = multiChannel_array_trans[:, :, 3].astype(float)/32768
            # alpha = multiChannel_array_trans[:,:,4].astype(float)

        # elif cameratype==2: #dji Mavic3M
        #     green = multiChannel_array_trans[:,:,0].astype(float)/32768
        #     red = multiChannel_array_trans[:,:,1].astype(float)/32768
        #     rededge = multiChannel_array_trans[:,:,2].astype(float)/32768
        #     nir = multiChannel_array_trans[:,:,3].astype(float)/32768
        #     # alpha = multiChannel_array_trans[:,:,4].astype(float)

        #################################################################################
        #%% RAW bands calculations
        #################################################################################

        green_mean_ls.append(np.nanmean(green))
        green_med_ls.append(np.nanquantile(green, 0.5))
        green_std_ls.append(np.nanstd(green))

        red_mean_ls.append(np.nanmean(red))
        red_med_ls.append(np.nanquantile(red, 0.5))
        red_std_ls.append(np.nanstd(red))

        rededge_mean_ls.append(np.nanmean(rededge))
        rededge_med_ls.append(np.nanquantile(rededge, 0.5))
        rededge_std_ls.append(np.nanstd(rededge))

        nir_mean_ls.append(np.nanmean(nir))
        nir_med_ls.append(np.nanquantile(nir, 0.5))
        nir_std_ls.append(np.nanstd(nir))

        #################################################################################
        #%% Create MASK
        #################################################################################
        ndvi = mcvi.ndvi(nir, red)

        ndvi_mask = mcvi.ndvi(nir, red)
        # 3 dim image from [rows,cols] to[rows,cols,bands]
        ndvi_mask = np.expand_dims(ndvi_mask, axis=2)

        ndvi_mask[ndvi_mask <= ndvi_mask_threshold] = 0
        ndvi_mask[ndvi_mask > ndvi_mask_threshold] = 255

        # print(np.nanmax(ndvi_mask))

        # normalize the data to 0 - 1
        mask = ndvi_mask.astype(np.float64)/np.nanmax(ndvi_mask)
        mask = 255 * mask  # Now scale by 255
        mask = mask.astype(np.uint8)
        boolean_mask = ma.make_mask(mask)

        #%% NDVI calculations
        #################################################################################

        masked_ndvi = np.ma.masked_array(
            data=ndvi, mask=np.logical_not(boolean_mask))
        non_masked_ndvi_data = masked_ndvi[masked_ndvi.mask == False]

        ndvi_mean_ls.append(np.nanmean(non_masked_ndvi_data))
        ndvi_med_ls.append(np.nanquantile(non_masked_ndvi_data, 0.5))
        ndvi_std_ls.append(np.nanstd(non_masked_ndvi_data))

        #################################################################################
        #%% WDRVI calculations
        #################################################################################
        wdrvi = mcvi.wdrvi(nir, red, alpha=0.2)

        masked_wdrvi = np.ma.masked_array(
            data=wdrvi, mask=np.logical_not(boolean_mask))
        non_masked_wdrvi_data = masked_wdrvi[masked_wdrvi.mask == False]

        wdrvi_mean_ls.append(np.nanmean(non_masked_wdrvi_data))
        wdrvi_med_ls.append(np.nanquantile(non_masked_wdrvi_data, 0.5))
        wdrvi_std_ls.append(np.nanstd(non_masked_wdrvi_data))
        #################################################################################
        #%% gNDVI calculations
        #################################################################################
        gndvi = mcvi.gndvi(nir, green)

        masked_gndvi = np.ma.masked_array(
            data=gndvi, mask=np.logical_not(boolean_mask))
        non_masked_gndvi_data = masked_gndvi[masked_gndvi.mask == False]

        gndvi_mean_ls.append(np.nanmean(non_masked_gndvi_data))
        gndvi_med_ls.append(np.quantile(non_masked_gndvi_data, 0.5))
        gndvi_std_ls.append(np.nanstd(non_masked_gndvi_data))
        #################################################################################
        #%% NDRE calculations
        #################################################################################
        ndre = mcvi.ndre(nir, rededge)

        masked_ndre = np.ma.masked_array(
            data=ndre, mask=np.logical_not(boolean_mask))
        non_masked_ndre_data = masked_ndre[masked_ndre.mask == False]

        ndre_mean_ls.append(np.nanmean(non_masked_ndre_data))
        ndre_med_ls.append(np.nanquantile(non_masked_ndre_data, 0.5))
        ndre_std_ls.append(np.nanstd(non_masked_ndre_data))
        #################################################################################
        #%% SAVI calculations
        #################################################################################
        savi = mcvi.savi(nir, red)

        masked_savi = np.ma.masked_array(
            data=savi, mask=np.logical_not(boolean_mask))
        non_masked_savi_data = masked_savi[masked_savi.mask == False]

        savi_mean_ls.append(np.nanmean(non_masked_savi_data))
        savi_med_ls.append(np.nanquantile(non_masked_savi_data, 0.5))
        savi_std_ls.append(np.nanstd(non_masked_savi_data))
        #################################################################################
        #%% GCI calculations
        #################################################################################
        gci = mcvi.gci(nir, green)

        masked_gci = np.ma.masked_array(
            data=gci, mask=np.logical_not(boolean_mask))
        non_masked_gci_data = masked_gci[masked_gci.mask == False]

        gci_mean_ls.append(np.nanmean(non_masked_gci_data))
        gci_med_ls.append(np.nanquantile(non_masked_gci_data, 0.5))
        gci_std_ls.append(np.nanstd(non_masked_gci_data))
        #################################################################################
        #%% RCI calculations
        #################################################################################
        rci = mcvi.rci(nir, rededge)

        masked_rci = np.ma.masked_array(
            data=rci, mask=np.logical_not(boolean_mask))
        non_masked_rci_data = masked_rci[masked_rci.mask == False]

        rci_mean_ls.append(np.nanmean(non_masked_rci_data))
        rci_med_ls.append(np.nanquantile(non_masked_rci_data, 0.5))
        rci_std_ls.append(np.nanstd(non_masked_rci_data))
        #################################################################################
        #%% Red edge simple ratio calculations
        #################################################################################
        resratio = mcvi.resratio(nir, rededge)

        masked_resratio = np.ma.masked_array(
            data=resratio, mask=np.logical_not(boolean_mask))
        non_masked_resratio_data = masked_resratio[masked_resratio.mask == False]

        resratio_mean_ls.append(np.nanmean(non_masked_resratio_data))
        resratio_med_ls.append(np.nanquantile(non_masked_resratio_data, 0.5))
        resratio_std_ls.append(np.nanstd(non_masked_resratio_data))

        #################################################################################
        #%% Medium Resolution Imaging Spectrometer (MERIS) Terrestrial Chlorophyll Index (MRCI)
        #################################################################################
        mrci = mcvi.mrci(nir, red, rededge)

        masked_mrci = np.ma.masked_array(
            data=mrci, mask=np.logical_not(boolean_mask))
        non_masked_mrci_data = masked_mrci[masked_mrci.mask == False]

        mrci_mean_ls.append(np.nanmean(non_masked_mrci_data))
        mrci_med_ls.append(np.nanquantile(non_masked_mrci_data, 0.5))
        mrci_std_ls.append(np.nanstd(non_masked_mrci_data))
        #################################################################################
        #%% Core Red Edge Triangular Vegetation Index
        #################################################################################
        cretvi = mcvi.cretvi(nir, green, rededge)

        masked_cretvi = np.ma.masked_array(
            data=cretvi, mask=np.logical_not(boolean_mask))
        non_masked_cretvi_data = masked_cretvi[masked_cretvi.mask == False]

        cretvi_mean_ls.append(np.nanmean(non_masked_cretvi_data))
        cretvi_med_ls.append(np.nanquantile(non_masked_cretvi_data, 0.5))
        cretvi_std_ls.append(np.nanstd(non_masked_cretvi_data))
        #################################################################################
        #%% Red Difference Index
        #################################################################################
        reddi = mcvi.reddi(nir, red)

        masked_reddi = np.ma.masked_array(
            data=reddi, mask=np.logical_not(boolean_mask))
        non_masked_reddi_data = masked_reddi[masked_reddi.mask == False]

        reddi_mean_ls.append(np.nanmean(non_masked_reddi_data))
        reddi_med_ls.append(np.nanquantile(non_masked_reddi_data, 0.5))
        reddi_std_ls.append(np.nanstd(non_masked_reddi_data))
        #################################################################################
        #%% Canopy Chlorophyll Concentration Index
        #################################################################################
        # ccci = mcvi.ccci(nir,red,ndvi)
        # ccci_mean_ls.append(np.nanmean(ccci))
        # ccci_med_ls.append(np.nanquantile(ccci, 0.5))
        # ccci_std_ls.append(np.nanstd(ccci))
        #################################################################################
        #%% Green Difference Index
        #################################################################################
        greendi = mcvi.greendi(nir, green)

        masked_greendi = np.ma.masked_array(
            data=greendi, mask=np.logical_not(boolean_mask))
        non_masked_greendi_data = masked_greendi[masked_greendi.mask == False]

        greendi_mean_ls.append(np.nanmean(non_masked_greendi_data))
        greendi_med_ls.append(np.nanquantile(non_masked_greendi_data, 0.5))
        greendi_std_ls.append(np.nanstd(non_masked_greendi_data))
        #################################################################################
        #%% Green Ratio Simple Index
        #################################################################################
        greensratio = mcvi.greensratio(nir, green)

        masked_greensratio = np.ma.masked_array(
            data=greensratio, mask=np.logical_not(boolean_mask))
        non_masked_greensratio_data = masked_greensratio[masked_greensratio.mask == False]

        greensratio_mean_ls.append(np.nanmean(non_masked_greensratio_data))
        greensratio_med_ls.append(np.nanquantile(
            non_masked_greensratio_data, 0.5))
        greensratio_std_ls.append(np.nanstd(non_masked_greensratio_data))
        #################################################################################
        #%% GRVI calculations
        #################################################################################
        grvi = mcvi.grvi(red, green)

        masked_grvi = np.ma.masked_array(
            data=grvi, mask=np.logical_not(boolean_mask))
        non_masked_grvi_data = masked_grvi[masked_grvi.mask == False]

        grvi_mean_ls.append(np.nanmean(non_masked_grvi_data))
        grvi_med_ls.append(np.nanquantile(non_masked_grvi_data, 0.5))
        grvi_std_ls.append(np.nanstd(non_masked_grvi_data))
        #################################################################################
        #%% MGRVI calculations
        #################################################################################
        mgrvi = mcvi.mgrvi(red, green)

        masked_mgrvi = np.ma.masked_array(
            data=mgrvi, mask=np.logical_not(boolean_mask))
        non_masked_mgrvi_data = masked_mgrvi[masked_mgrvi.mask == False]

        mgrvi_mean_ls.append(np.nanmean(non_masked_mgrvi_data))
        mgrvi_med_ls.append(np.nanquantile(non_masked_mgrvi_data, 0.5))
        mgrvi_std_ls.append(np.nanstd(non_masked_mgrvi_data))
        #%%
        #################################################################################
        #%% collect exif data
        #################################################################################
        all_images = glob.glob(os.path.join(path_to_images, "**", "*.jpg"), recursive=True)


        images_for_calcs = all_images[0::10]

        # shutterSpeed = 0
        hour = 0

        for s in images_for_calcs:
            img = PIL.Image.open(s)  # get single image
            # get exif data as dict
            exif = {PIL.ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in PIL.ExifTags.TAGS}

            # shutterSpeed = shutterSpeed+exif["ExposureTime"]  # [0]

            hour = hour+int(exif["DateTime"][-8:-6])

        # *1000 to have it in ms
        # shutterSpeed_avg = float(shutterSpeed/len(images_for_calcs))*1000
        hour_avg = int(hour/len(images_for_calcs))
        month = int(exif["DateTime"][5:7])

        month_ls.append(month)
        hour_ls.append(hour_avg)
        # shutterSpeed_avg_ls.append(shutterSpeed_avg)
    ############################################################################################

    #######################################################
    # create pandas df
    #######################################################

    final_df = pd.DataFrame(list(zip(shp_id_ls,
                                     # shp_block_ls,
                                     green_mean_ls, green_med_ls, green_std_ls,
                                     red_mean_ls, red_med_ls, red_std_ls,
                                     rededge_mean_ls, rededge_med_ls, rededge_std_ls,
                                     nir_mean_ls, nir_med_ls, nir_std_ls,
                                     ndvi_mean_ls, ndvi_med_ls, ndvi_std_ls,
                                     wdrvi_mean_ls, wdrvi_med_ls, wdrvi_std_ls,
                                     gndvi_mean_ls, gndvi_med_ls, gndvi_std_ls,
                                     savi_mean_ls, savi_med_ls, savi_std_ls,
                                     gci_mean_ls, gci_med_ls, gci_std_ls,
                                     rci_mean_ls, rci_med_ls, rci_std_ls,
                                     resratio_mean_ls, resratio_med_ls, resratio_std_ls,
                                     mrci_mean_ls, mrci_med_ls, mrci_std_ls,
                                     cretvi_mean_ls, cretvi_med_ls, cretvi_std_ls,
                                     reddi_mean_ls, reddi_med_ls, reddi_std_ls,
                                     # ccci_mean_ls,ccci_med_ls,ccci_std_ls,
                                     greendi_mean_ls, greendi_med_ls, greendi_std_ls,
                                     greensratio_mean_ls, greensratio_med_ls, greensratio_std_ls,
                                     ndre_mean_ls, ndre_med_ls, ndre_std_ls,
                                     grvi_mean_ls, grvi_med_ls, grvi_std_ls,
                                     mgrvi_mean_ls, mgrvi_med_ls, mgrvi_std_ls,
                                     month_ls, hour_ls,
                                      # shutterSpeed_avg_ls
                                     )),
                            columns=["STR",
                                     "GREEN_mean", "GREEN_med", "GREEN_std",
                                     "RED_mean", "RED_med", "RED_std",
                                     "REDEDGE_mean", "REDEDGE_med", "REDEDGE_std",
                                     "NIR_mean", "NIR_med", "NIR_std",
                                     "NDVI_mean", "NDVI_med", "NDVI_std",
                                     "WDRVI_mean", "WDRVI_med", "WDRVI_std",
                                     "GNDVI_mean", "GNDVI_med", "GNDVI_std",
                                     "SAVI_mean", "SAVI_med", "SAVI_std",
                                     "GCI_mean", "GCI_med", "GCI_std",
                                     "RCI_mean", "RCI_med", "RCI_std",
                                     "RESRATIO_mean", "RESRATIO_med", "RESRATIO_std",
                                     "MRCI_mean", "MRCI_med", "MRCI_std",
                                     "CRETVI_mean", "CRETVI_med", "CRETVI_std",
                                     "REDDI_mean", "REDDI_med", "REDDI_std",
                                     # "CCCI_mean","CCCI_med", "CCCI_std",
                                     "GREENDI_mean", "GREENDI_med", "GREENDI_std",
                                     "GREENSRATIO_mean", "GREENSRATIO_med", "GREENSRATIO_std",
                                     "NDRE_mean", "NDRE_med", "NDRE_std",
                                     "GRVI_mean", "GRVI_med", "GRVI_std",
                                     "MGRVI_mean", "MGRVI_med", "MGRVI_std",
                                     "month", "hour", 
                                      # "shutterSpeed"
                                     ])

    final_df = final_df.set_index('STR')

    return final_df
