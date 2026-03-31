import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os

FEATURE_COLUMNS = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
]

SCALER_PATH = os.path.join(os.path.dirname(__file__), "../models/feature_scaler.pkl")


def build_features(df, fit=False):
    """
    Converts raw dataframe into normalized feature matrix
    """
    
    X = df[FEATURE_COLUMNS].copy()
    
    # Fill missing values
    X = X.fillna(0)
    
    if fit:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        joblib.dump(scaler, SCALER_PATH)
    else:
        scaler = joblib.load(SCALER_PATH)
        X_scaled = scaler.transform(X)
    
    return X_scaled


def build_single_feature(song_row):
    """
    Converts a single song into model-ready vector
    """
    from joblib import load
    
    scaler = load(SCALER_PATH)
    
    x = np.array([song_row[col] for col in FEATURE_COLUMNS]).reshape(1, -1)
    x_scaled = scaler.transform(x)
    
    return x_scaled[0]