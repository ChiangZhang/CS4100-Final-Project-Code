import torch
import joblib
import pandas as pd
import numpy as np
from tqdm import tqdm
from torch.utils.data import DataLoader, TensorDataset
from src.models.mood_model import MoodNet

# Paths
MODEL_PATH = "src/models/mood_model.pt"
SCALER_PATH = "src/models/feature_scaler.pkl"
INPUT_DATA = "src/data/cleaned_dataset_unique.csv"
OUTPUT_DATA = "src/data/final_mood_mapped_library.csv"

# Columns
SCALABLE_COLS = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
MOOD_COLS = ["calm", "happy", "energetic", "sad", "dark", "romantic", "focus", "hype"]

def map_final_dataset():
    print("Loading model and scaler...")
    scaler = joblib.load(SCALER_PATH)
    model = MoodNet(input_dim=9, hidden_dim=64, num_moods=8)
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()

    print("Loading library data...")
    df = pd.read_csv(INPUT_DATA)
    
    # 1. Prepare Features
    X_raw = df[SCALABLE_COLS].values
    X_scaled = scaler.transform(X_raw)
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
    
    # 2. Setup DataLoader for Batch Inference
    # Batch size 512 is usually a 'sweet spot' for speed vs memory
    dataset = TensorDataset(X_tensor)
    loader = DataLoader(dataset, batch_size=512, shuffle=False)
    
    all_predictions = []
    
    print(f"Mapping {len(df)} tracks...")
    with torch.no_grad(): # Speeds up inference by not calculating gradients
        for batch in tqdm(loader, desc="Inference Progress"):
            X_batch = batch[0]
            preds = model(X_batch)
            all_predictions.append(preds.numpy())
    
    # 3. Concatenate and Merge
    y_pred = np.vstack(all_predictions)
    
    # Create a DataFrame for the new mood scores
    mood_df = pd.DataFrame(y_pred, columns=MOOD_COLS)
    
    # Combine original data with new mood predictions
    final_df = pd.concat([df.reset_index(drop=True), mood_df], axis=1)
    
    print(f"Saving mapped library to {OUTPUT_DATA}...")
    final_df.to_csv(OUTPUT_DATA, index=False)
    print("Library mapping complete!")

if __name__ == "__main__":
    map_final_dataset()