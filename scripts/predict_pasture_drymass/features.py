import os
import sys
import pandas as pd
import numpy as np
import fiona
from shapely.geometry import shape
import traceback


# Ensure project root and modules folder are on the Python path
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()

root_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "modules"))

from module_DTMmodel import clip
from VegIndices_calculations_for_dataframe_withMask import vi_calcs_for_df
from config_prediction import NDVI_THRESHOLD


def load_shapefile(shapefile_path):
    try:
        with fiona.open(shapefile_path) as shp:
            geometries = [shape(feat['geometry']) for feat in shp]
            ids = [feat['properties']['id'] for feat in shp]
        return geometries, ids
    except Exception as e:
        raise RuntimeError(f"Error reading shapefile {shapefile_path}: {e}")


def compute_height_stats(csm_array):
    csm_array = np.where(csm_array == -32767.0, np.nan, csm_array)
    csm = csm_array[0]

    return {
        "avg_height": np.nanmean(csm),
        "std_dev": np.nanstd(csm),
        "min_height": np.nanmin(csm),
        "max_height": np.nanmax(csm),
          "five_perc": np.nanpercentile(csm, 5),
        "ten_perc": np.nanpercentile(csm, 10),
        "twentyfive_perc": np.nanpercentile(csm, 25),
        "fifty_perc": np.nanpercentile(csm, 50),
        "seventy_perc": np.nanpercentile(csm, 70),
        "ninety_perc": np.nanpercentile(csm, 90),
    }


def extract_height_features(date, site, region, base_dir="."):
    # Set the project root to navigate all paths relative to it
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    # Paths based on the project root
    path_to_data = os.path.join(project_root, "data", site, date, region, "Agisoft", "Agi_EXPORT")
    csm_file = f"{date}_clipped_CSM.tif"
    shapefile_path = os.path.join(project_root, "data", "zz_QGis", "Shapefiles", f"{region}.shp")
    output_csv_path = os.path.join(project_root, "data", "zz_Results", f"{date}_{region}.csv")

    # Load shapefile
    geometries, ids = load_shapefile(shapefile_path)

    results = []
    for shp_id, geom in zip(ids, geometries):
        try:
            clipped_array, _ = clip(geom, os.path.join(path_to_data, csm_file))
            features = compute_height_stats(clipped_array)
            features.update({"STR": shp_id, "DATE": date.replace("-", "")[2:]})
            results.append(features)
        except Exception as e:
            print(f"[Warning] Skipping {shp_id} due to error: {e}")

    df = pd.DataFrame(results)
    df.set_index("STR", inplace=True)
    
    # Ensure the directory exists before saving
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    
    df.to_csv(output_csv_path, float_format="%.5f")
    print(f"[OK] Height data saved: {output_csv_path}")
    return df



def extract_vi_features(date, masl, site, region, base_dir=".", cameratype=1):
    print("[DEBUG] Running extract_vi_features...")
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    export_path = os.path.join(project_root,"data", site, date, region, "Agisoft", "Agi_EXPORT")
    
    read_all_channels = os.path.join(export_path, f"{date}_allChannels_xy_transformed.tif")
    path_to_images = os.path.join(project_root, "data", site, date, region, "Fotos")
    path_to_csv = os.path.join(project_root,"data", "zz_Results", f"{date}_{region}.csv")
    shapefile_path = os.path.join(project_root, "data", "zz_QGis", "Shapefiles", f"{region}.shp")
    
    print(f"[DEBUG] Reading shapefile from {shapefile_path}...")
    geometries, ids = load_shapefile(shapefile_path)
    print(f"[DEBUG] Shapefile loaded. {len(geometries)} geometries found.")

    try:
        print("[DEBUG] Running VI calculation...")
        vi_df = vi_calcs_for_df(
            ndvi_mask_threshold=NDVI_THRESHOLD,
            all_shapes=geometries,
            shp_id_ls=ids,
            read_allChannels=read_all_channels,
            path_to_images=path_to_images,
            # masl=masl,
            cameratype=cameratype
        )
    except Exception as e:
       
        traceback.print_exc()
        raise RuntimeError(f"VI calculation failed: {e}")
    
    try:
        print(f"[DEBUG] Reading base CSV from {path_to_csv}...")
        base_df = pd.read_csv(path_to_csv, index_col="STR")
    except Exception as e:
        raise FileNotFoundError(f"Base CSV not found: {path_to_csv}\n{e}")

    print(f"[DEBUG] Saving full feature CSV to {path_to_csv}...")
    combined_df = pd.concat([base_df, vi_df], axis=1)
    os.makedirs(os.path.dirname(path_to_csv), exist_ok=True)
    combined_df.to_csv(path_to_csv, float_format="%.5f")
    
    print(f"[INFO] You can find the full feature CSV (height + VIs) here: {os.path.abspath(path_to_csv)}")
    print(f"[OK] VI data appended and saved: {path_to_csv}")
    
    return combined_df
