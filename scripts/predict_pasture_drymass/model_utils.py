import sys
import os
import pickle

# Ensure project root and modules folder are on the Python path
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))



def load_model(model_name):
    """
    Loads a trained sklearn model from the models directory.
    """
    model_path = os.path.join(f"{project_root}/models", model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    return model


def predict(model, features_df):
    """
    Runs prediction using the loaded model and returns predictions.
    Multiplies the output by 10000 to match dry mass units.
    """
    predictions = model.predict(features_df) * 10000  # scale if needed
    return predictions
