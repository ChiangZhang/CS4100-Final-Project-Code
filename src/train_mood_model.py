import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib
import os

from models.mood_model import MoodNet

DATA_PATH = "src/data/demo_dataset.csv"
MODEL_PATH = "src/models/mood_model.pt"
SCALER_PATH = "src/models/feature_scaler.pkl"

FEATURE_COLS = [
    "danceability","energy","loudness","speechiness",
    "acousticness","instrumentalness","liveness","valence","tempo"
]

MOOD_COLS = [
    "calm","happy","energetic","sad","dark","romantic","focus","hype"
]

# Load data
df = pd.read_csv(DATA_PATH)

X = df[FEATURE_COLS].values
y = df[MOOD_COLS].values

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

joblib.dump(scaler, SCALER_PATH)
print(f"Scaler saved to {SCALER_PATH}")

# Convert to tensors
X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32)

# Model
model = MoodNet(
    input_dim=len(FEATURE_COLS),
    hidden_dim=64,
    num_moods=len(MOOD_COLS)
)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Train
EPOCHS = 50

for epoch in range(EPOCHS):
    optimizer.zero_grad()
    outputs = model(X_tensor)
    loss = criterion(outputs, y_tensor)
    loss.backward()
    optimizer.step()

    if (epoch+1) % 10 == 0:
        print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {loss.item():.4f}")

# Save model
os.makedirs("src/models", exist_ok=True)
torch.save(model.state_dict(), MODEL_PATH)

print(f"Model saved to {MODEL_PATH}")