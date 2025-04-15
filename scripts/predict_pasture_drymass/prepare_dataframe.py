import pandas as pd
import os


def prepare_df(date, region, site):
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
    df["pastureI"] = df["fifty_perc"] + df["WDRVI_mean"]
    df["PastureI"] = df["ninety_perc"] + df["WDRVI_mean"]

    # Clean up
    df.dropna(inplace=True)
    df["Cameratype"] = 1
    df["Use"] = 0

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
