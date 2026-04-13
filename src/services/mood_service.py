import torch
import numpy as np
from src.models.mood_model import MoodNet
from src.utils.mood_utils import MOODS
import os
import subprocess

# NOTE: functions predict_mood_vector and score_song were produced using an LLM (chatGPT)
# the objective of the mood service with context was given to the LLM, and it was asked to produce these functions.

MODEL_PATH = "src/models/mood_model.pt"
SCALER_PATH = os.path.join(os.path.dirname(__file__), "../models/feature_scaler.pkl")

class MoodService:
    def __init__(self, input_dim, hidden_dim=64):
        self.ensure_model_exists()
        self.model = MoodNet(input_dim, hidden_dim, len(MOODS))
        self.model.load_state_dict(torch.load(MODEL_PATH))
        self.model.eval()
    
    def predict_mood_vector(self, features):
        with torch.no_grad():
            x = torch.tensor(features, dtype=torch.float32)
            output = self.model(x)
        return output.numpy()
    
    def score_song(self, features, start_idx, end_idx, alpha):
        pred = self.predict_mood_vector(features)
        
        start_score = pred[start_idx]
        end_score = pred[end_idx]
        
        return alpha * start_score + (1 - alpha) * end_score
    
    def ensure_model_exists(self):
        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            print("Model or scaler not found. Training model...")
            
            # Run training script automatically
            subprocess.run(["python3", "src/models/train_mood_model.py"], check=True)
            
            print("Model training complete.")
        print("model training files already exist!")