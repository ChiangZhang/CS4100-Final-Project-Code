import torch
import torch.nn as nn
import torch.optim as optim
from mood_model import MoodNet
from utils.mood_utils import load_data

# Hyperparameters
INPUT_DIM = 20   # number of audio features
HIDDEN_DIM = 64
NUM_MOODS = 8
LR = 0.001
EPOCHS = 20

# Load dataset
X_train, y_train = load_data()

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32)

# Model
model = MoodNet(INPUT_DIM, HIDDEN_DIM, NUM_MOODS)

criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# Training loop
for epoch in range(EPOCHS):
    model.train()
    
    optimizer.zero_grad()
    
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    
    loss.backward()
    optimizer.step()
    
    print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {loss.item():.4f}")

# Save model
torch.save(model.state_dict(), "models/mood_model.pt")