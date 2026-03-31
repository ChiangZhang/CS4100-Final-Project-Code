import torch
import numpy as np
from models.mood_model import MoodNet
from utils.mood_utils import MOODS

MODEL_PATH = "src/models/mood_model.pt"

class MoodService:
    def __init__(self, input_dim, hidden_dim=64):
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