import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
import joblib
import os

from mood_model import MoodNet

DATA_PATH = "src/data/v2_training_dataset.csv"
MODEL_PATH = "src/models/mood_model.pt"
SCALER_PATH = "src/models/feature_scaler.pkl"

SCALABLE_COLS = [
    "danceability", "energy", "loudness", "speechiness", 
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
]
MOOD_COLS = ["calm", "happy", "energetic", "sad", "dark", "romantic", "focus", "hype"]
META_COLS = ["track_id", "artists", "album_name", "track_name"]

def train_loop(dataloader, model, loss_fn, optimizer):
    model.train()
    for batch,(X, y) in enumerate(dataloader):
        pred = model(X)
        loss = loss_fn(pred, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

def test_loop(dataloader, model, loss_fn):
    model.eval()
    num_batches = len(dataloader)
    test_loss = 0

    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
    
    avg_loss = test_loss / num_batches
    return avg_loss

def main():
    df = pd.read_csv(DATA_PATH)
    
    # shuffle all data to break alphabetical genre bias
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Everything that isn't Mood or Metadata is a Feature (includes all 114 Genres)
    ALL_FEATURES = [c for c in df.columns if c not in MOOD_COLS + META_COLS]
    GENRE_COLS = [c for c in ALL_FEATURES if c not in SCALABLE_COLS]

    # Scale features
    scaler = StandardScaler()
    scaled_audio_features = scaler.fit_transform(df[SCALABLE_COLS])
    X = np.hstack([scaled_audio_features, df[GENRE_COLS].values]).astype(np.float32)
    y = df[MOOD_COLS].values.astype(np.float32)

    os.makedirs("src/models", exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)

    # k-fold cross validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    best_all_time_loss = float('inf')
    fold_mses = []

    for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
        train_loader = DataLoader(TensorDataset(torch.from_numpy(X[train_idx]), torch.from_numpy(y[train_idx])), batch_size=32, shuffle=True)
        val_loader = DataLoader(TensorDataset(torch.from_numpy(X[val_idx]), torch.from_numpy(y[val_idx])), batch_size=32)

        model = MoodNet(input_dim=X.shape[1], hidden_dim=256, num_moods=len(MOOD_COLS))
        loss_fn =  nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        EPOCHS = 50
        for epoch in range(EPOCHS):
            train_loop(train_loader, model, loss_fn, optimizer)

        # Capture MSE after training is done for this fold
        current_fold_mse = test_loop(val_loader, model, loss_fn)
        fold_mses.append(current_fold_mse)
        print(f"Fold {fold+1} MSE: {current_fold_mse:.4f}")

        if current_fold_mse < best_all_time_loss:
            best_all_time_loss = current_fold_mse
            torch.save(model.state_dict(), MODEL_PATH)
            print(f">>> New Best Model Found (MSE: {best_all_time_loss:.6f})")

    print(f"\nFinal Best MSE: {best_all_time_loss:.6f}")

if __name__ == "__main__":
    main()