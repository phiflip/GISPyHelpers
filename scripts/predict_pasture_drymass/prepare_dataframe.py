import pandas as pd
import os


def prepare_df(date, region, site, cameratype, use):
    """
    Reads the combined height + VI data, computes derived features,
    cleans the DataFrame and returns it ready for prediction.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    
    base_path = f"{project_root}/data/zz_Results/"
    filename = f"{date}_{region}.csv"
    filepath = os.path.join(base_path, filename)

    df = pd.read_csv(filepath)
    df = df.set_index("STR")
    
    

    # Derived features
    df["CCCI_mean"] = df["NDRE_mean"] / df["NDVI_mean"]
    df["PastureI"] = df["ninety_perc"] + df["WDRVI_mean"]

    # Clean up
    df.dropna(inplace=True)
    df["Cameratype"] = cameratype
    df["Use"] = use


    
        
    if df["Cameratype"].iloc[0] == 2:
        df["GCI_mean"] *= 0.65
        df["GNDVI_mean"] *= 0.9
        df["CCCI_mean"] *= 0.8
        # df["PastureI"] *= 0.95
        df["WDRVI_mean"] *= 0.9

        
        print("VI correction ACTIVE")





    df.rename(columns={
        "std_dev": "CH_stdev",
        "GNDVI_std": "GNDVI_stdev",
        "MRCI_std": "MRCI_stdev",
        "CRETVI_std": "CRETVI_stdev",
        "GREENSRATIO_std": "GREENSRATIO_stdev",
        "month": "Month",
        "fifty_perc": "CH_P50",
        
    }, inplace=True)

    # Keep only relevant features
    features_to_keep = [
        "CH_stdev", "GNDVI_mean", "GNDVI_stdev", "GCI_mean", "MRCI_stdev",
        "CRETVI_stdev", "GREENDI_mean", "GREENSRATIO_stdev", "Month",
        "Use", "CCCI_mean", "PastureI", "CH_P50", "Cameratype"
    ]

    df = df[features_to_keep]
    df = pd.get_dummies(df)

    return df
