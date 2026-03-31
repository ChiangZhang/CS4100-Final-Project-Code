import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

from models.mood_model import MoodNet
from utils.mood_utils import MOODS

# -----------------------
# Dummy training feature builder
# -----------------------
def build_training_features(num_samples=100):
    INPUT_DIM = 9
    OUTPUT_DIM = len(MOODS)
    X = np.random.rand(num_samples, INPUT_DIM)
    y = np.random.rand(num_samples, OUTPUT_DIM)
    return X, y

# -----------------------
# Hyperparameters
# -----------------------
INPUT_DIM = 9
HIDDEN_DIM = 64
OUTPUT_DIM = len(MOODS)
EPOCHS = 5
LR = 0.001

# -----------------------
# Prepare data
# -----------------------
X, y = build_training_features()
X = torch.tensor(X, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.float32)

# -----------------------
# Initialize model
# -----------------------
model = MoodNet(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# -----------------------
# Training loop
# -----------------------
for epoch in range(EPOCHS):
    optimizer.zero_grad()
    outputs = model(X)
    loss = criterion(outputs, y)
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {loss.item():.4f}")

# -----------------------
# Save model
# -----------------------
MODEL_PATH = "src/models/mood_model.pt"
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
torch.save(model.state_dict(), MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")