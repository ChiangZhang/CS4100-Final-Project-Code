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
import matplotlib.pyplot as plt

from mood_model import MoodNet

# NOTE: LLM (ChatGPT) used to add graphs to this code that demonstrate the accuracy of the trained model
# code was given to LLM with context about what graphs and visuals I wanted to produce, and then I asked the LLM to make adjustments to my existing code to add those graphs in.

DATA_PATH = "src/data/full_training_dataset.csv"
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
    for batch, (X, y) in enumerate(dataloader):
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

    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    ALL_FEATURES = [c for c in df.columns if c not in MOOD_COLS + META_COLS]
    GENRE_COLS = [c for c in ALL_FEATURES if c not in SCALABLE_COLS]

    scaler = StandardScaler()
    scaled_audio = scaler.fit_transform(df[SCALABLE_COLS])

    X = scaled_audio.astype(np.float32)
    y = df[MOOD_COLS].values.astype(np.float32)

    os.makedirs("src/models", exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    best_all_time_loss = float('inf')
    fold_mses = []

    all_fold_preds = []
    all_fold_true = []

    for fold, (train_idx, val_idx) in enumerate(kf.split(X)):

        train_loader = DataLoader(
            TensorDataset(torch.from_numpy(X[train_idx]), torch.from_numpy(y[train_idx])),
            batch_size=32,
            shuffle=True
        )

        val_loader = DataLoader(
            TensorDataset(torch.from_numpy(X[val_idx]), torch.from_numpy(y[val_idx])),
            batch_size=32
        )

        model = MoodNet(input_dim=X.shape[1], hidden_dim=64, num_moods=len(MOOD_COLS))
        loss_fn = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        EPOCHS = 50
        train_losses = []

        for epoch in range(EPOCHS):
            model.train()
            running_loss = 0

            for X_batch, y_batch in train_loader:
                pred = model(X_batch)
                loss = loss_fn(pred, y_batch)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                running_loss += loss.item()

            avg_train_loss = running_loss / len(train_loader)
            train_losses.append(avg_train_loss)

        current_fold_mse = test_loop(val_loader, model, loss_fn)
        fold_mses.append(current_fold_mse)

        print(f"Fold {fold+1} MSE: {current_fold_mse:.4f}")

        # Save predictions for final visualization
        model.eval()
        preds = []
        trues = []

        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                p = model(X_batch)
                preds.append(p.numpy())
                trues.append(y_batch.numpy())

        preds = np.vstack(preds)
        trues = np.vstack(trues)

        all_fold_preds.append(preds)
        all_fold_true.append(trues)

        # Plot training loss per fold
        plt.figure()
        plt.plot(train_losses)
        plt.xlabel("Epoch")
        plt.ylabel("Training Loss")
        plt.title(f"Training Loss Curve (Fold {fold+1})")
        plt.show()

        if current_fold_mse < best_all_time_loss:
            best_all_time_loss = current_fold_mse
            torch.save(model.state_dict(), MODEL_PATH)
            print(f">>> New Best Model Found (MSE: {best_all_time_loss:.6f})")

    print(f"\nFinal Best MSE: {best_all_time_loss:.6f}")

    # fold mse plot
    plt.figure()
    plt.plot(range(1, len(fold_mses) + 1), fold_mses, marker='o')
    plt.xlabel("Fold")
    plt.ylabel("Validation MSE")
    plt.title("K-Fold Validation Error")
    plt.show()

    print(f"Mean MSE: {np.mean(fold_mses):.6f}")
    print(f"Std MSE: {np.std(fold_mses):.6f}")

    # pred vs ground truth
    all_preds = np.vstack(all_fold_preds)
    all_true = np.vstack(all_fold_true)

    plt.figure()
    plt.scatter(all_true[:, 0], all_preds[:, 0], alpha=0.4)
    plt.xlabel("True Mood Value")
    plt.ylabel("Predicted Mood Value")
    plt.title("Prediction vs Ground Truth (Mood: calm)")
    plt.show()


if __name__ == "__main__":
    main()