import sys
import os
import argparse
from datetime import datetime

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()

sys.path.append(os.path.abspath(os.path.join(script_dir, "..", "..")))

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


from config_prediction import DEFAULTS, SITE_REGION_MAP, DATES, MASL_DEFAULT, CAMERATYPE, USE
from scripts.predict_pasture_drymass.prepare_dataframe import prepare_df
from scripts.predict_pasture_drymass.model_utils import load_model, predict
from features import extract_height_features, extract_vi_features


def main(date, region, site, model_name):
    print("="*60)
    print("[DEBUG] Starting pipeline with:")
    print(f"  Date: {date}\n  Region: {region}\n  Site: {site}\n  Model: {model_name}")
    print("="*60)
    print("\n--- Starting Prediction Pipeline ---")
    print(f"Date: {date} | Region: {region} | Site: {site} | Use: {USE}\n")

    # Step 1: Generate height data
    print("[STEP] Running extract_height_features...")
    try:
        print("Calculating height features...")
        extract_height_features(date, site, region)
    except Exception as e:
        print(f"[Error] Height calculation failed: {e}")
        return

    # Step 2: Generate VI features
    print("[STEP] Running extract_vi_features...")
    try:
        print("Calculating vegetation indices...")
        extract_vi_features(date, MASL_DEFAULT, site, region)
    except Exception as e:
        print(f"[Error] VI calculation failed: {e}")
        return

    # Step 3: Prepare dataframe
    print("[STEP] Preparing final DataFrame for prediction...")
    df = prepare_df(date, region, site, CAMERATYPE, USE)

    # Step 4: Load model
    print("[STEP] Loading model...")
    model = load_model(model_name)

    # Step 5: Run prediction
    print("[STEP] Predicting dry mass...")
    predictions = predict(model, df)

    # Step 6: Save results in local "results" folder
    print("[STEP] Saving predictions to CSV...")
    out_path = os.path.join(project_root, "data","zz_Results", f"{date}_{region}_predictions.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    df["Prediction_DM"] = predictions
    df.to_csv(out_path, index=True, float_format="%.2f")
    print(f"[INFO] You can find the prediction output here: {os.path.abspath(out_path)}")

    log_run(date, region, site, model_name)


def log_run(date, region, site, model_name):
    log_txt = f"""
Last Run:
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Region: {region}
Site: {site}
Date: {date}
Model: {model_name}
"""
    with open("last_run_info.txt", "w") as f:
        f.write(log_txt)


def run_all_for_sites(model_name):
    for site in SITE_REGION_MAP:  # First loop through sites
        print(f"[DEBUG] Processing site: {site}")
        
        for date in DATES:  # Then loop through dates for each site
            print(f"[DEBUG] Processing date: {date} for site: {site}")
            
            # Fetch the regions for the current site
            regions = SITE_REGION_MAP.get(site, [])
            if not regions:
                print(f"[Warning] No region specified for site '{site}', skipping.")
                continue
                
            for region in regions:  # Loop through regions for each date/site combination
                try:
                    print(f"\nProcessing: {date} | {site} | {region}")
                    main(date, region, site, model_name)
                except Exception as e:
                    print(f"[Error] {date} | {site} | {region}: {e}")


# Direct call for interactive use (e.g. in Spyder)
if __name__ == "__main__" or True:
    parser = argparse.ArgumentParser(description="Prediction pipeline for pasture dry mass")
    parser.add_argument("--date", type=str, default=None)
    parser.add_argument("--region", type=str, help="Specify a single region")
    parser.add_argument("--site", type=str, help="Specify a single site")
    parser.add_argument("--model", type=str, default=DEFAULTS["model_name"])

    args = parser.parse_args()

    if args.date or args.site or args.region:
        main(
        date=args.date or DEFAULTS["date"],
        region=args.region or DEFAULTS["region"] or SITE_REGION_MAP.get(DEFAULTS["site"], [None])[0],
        site=args.site or DEFAULTS["site"],
        model_name=args.model
    )
    else:
        run_all_for_sites(model_name=args.model)

else:
    # Spyder-friendly fallback using config defaults
    region = DEFAULTS["region"] or SITE_REGION_MAP.get(DEFAULTS["site"], [None])[0]
    if region:
        main(
            date=DEFAULTS["date"],
            region=region,
            site=DEFAULTS["site"],
            model_name=DEFAULTS["model_name"]
        )
    else:
        print("[ERROR] No region provided or found for the given site in DEFAULTS.")
