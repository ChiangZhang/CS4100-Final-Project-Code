import pandas as pd
import numpy as np

MOODS = [
    "calm", "happy", "energetic", "sad",
    "dark", "romantic", "focus", "hype"
]

def load_data():
    # TODO: migrate cleaned data file over to src/data directory (preferably with cleanup code)
    df = pd.read_csv("data/cleaned_dataset.csv")
    
    feature_cols = [
        "danceability", "energy", "loudness",
        "speechiness", "acousticness",
        "instrumentalness", "liveness",
        "valence", "tempo"
    ]
    
    X = df[feature_cols].values
    
    # assume moods already encoded as multi-hot vectors
    y = df[MOODS].values
    
    return X, y


def encode_mood(mood):
    vec = np.zeros(len(MOODS))
    vec[MOODS.index(mood)] = 1
    return vec