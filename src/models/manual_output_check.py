import torch
import joblib
import pandas as pd
import numpy as np
from mood_model import MoodNet

# Paths
MODEL_PATH = "src/models/mood_model.pt"
SCALER_PATH = "src/models/feature_scaler.pkl"
MASTER_DATA_PATH = "src/data/cleaned_dataset_unique.csv" 

# --- CONFIGURATION ---
# Change this to any track_id from your dataset
TARGET_TRACK_ID = "3N69Iu7bWun04E5vXf2L7a" 

SCALABLE_COLS = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
MOOD_COLS = ["calm", "happy", "energetic", "sad", "dark", "romantic", "focus", "hype"]

def run_targeted_check():
    scaler = joblib.load(SCALER_PATH)
    model = MoodNet(input_dim=9, hidden_dim=64, num_moods=8)
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()

    df = pd.read_csv(MASTER_DATA_PATH)
    
    # 1. Locate the specific track
    # Note: Check if your ID column is named 'track_id' or 'id'
    track_row = df[df['track_id'] == "1afMigcYdKpRwDf8IyXnln"]

    if track_row.empty:
        print(f"ERROR: Track ID {TARGET_TRACK_ID} not found in {MASTER_DATA_PATH}")
        return

    track = track_row.iloc[0]

    # 2. Prepare Features
    raw_features = track[SCALABLE_COLS].values.reshape(1, -1)
    scaled_features = scaler.transform(raw_features)
    input_tensor = torch.tensor(scaled_features, dtype=torch.float32)

    # 3. Predict
    with torch.no_grad():
        preds = model(input_tensor).numpy()[0]

    # 4. Print Results
    print(f"\n" + "="*40)
    print(f"TARGETED CHECK: {track.get('track_name', 'Unknown')}")
    print(f"ARTISTS: {track.get('artists', 'Unknown')}")
    
    print("\n--- AUDIO DNA ---")
    for col in SCALABLE_COLS:
        print(f"  {col:18}: {track[col]:.4f}")

    print("\n--- MODEL'S MOOD PREDICTION ---")
    mood_scores = dict(zip(MOOD_COLS, preds))
    for mood, score in sorted(mood_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {mood:10}: {score:.4f}")
    print("="*40)

if __name__ == "__main__":
    run_targeted_check()