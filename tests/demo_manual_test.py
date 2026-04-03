"""
Demo Manual Test for MoodNet
Shows mood predictions and gradient scoring for a few sample songs.

Usage:
    # Activate your venv first
    source venv/bin/activate

    # Run the demo
    python3 tests/demo_manual_test.py
"""

import sys
import os
import numpy as np

# -----------------------
# Add src folder to Python path
# -----------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

# -----------------------
# Imports from your project
# -----------------------
from models.mood_model import MoodNet
from services.mood_service import MoodService
from features.feature_builder import build_single_feature
from utils.mood_utils import MOODS

# -----------------------
# Sample songs (fake data)
# -----------------------
sample_songs = [
    {
        "track_name": "Chill Vibes",
        "danceability": 0.5,
        "energy": 0.3,
        "loudness": -10,
        "speechiness": 0.04,
        "acousticness": 0.8,
        "instrumentalness": 0.2,
        "liveness": 0.1,
        "valence": 0.6,
        "tempo": 90
    },
    {
        "track_name": "Party Anthem",
        "danceability": 0.9,
        "energy": 0.95,
        "loudness": -3,
        "speechiness": 0.05,
        "acousticness": 0.0,
        "instrumentalness": 0.0,
        "liveness": 0.2,
        "valence": 0.95,
        "tempo": 128
    },
    {
        "track_name": "Focus Beats",
        "danceability": 0.6,
        "energy": 0.5,
        "loudness": -7,
        "speechiness": 0.03,
        "acousticness": 0.1,
        "instrumentalness": 0.5,
        "liveness": 0.05,
        "valence": 0.4,
        "tempo": 100
    }
]

# -----------------------
# Initialize Mood Service
# -----------------------
INPUT_DIM = 9  # must match feature vector length
mood_service = MoodService(input_dim=INPUT_DIM)

# -----------------------
# Set start and end moods for gradient test
# -----------------------
start_mood = "calm"
end_mood = "energetic"

start_idx = MOODS.index(start_mood)
end_idx = MOODS.index(end_mood)

# -----------------------
# Run demo
# -----------------------
print(f"\nDemo MoodNet: Start Mood = {start_mood}, End Mood = {end_mood}\n")

for song in sample_songs:
    features = build_single_feature(song)
    
    # Predict full mood vector
    mood_vector = mood_service.predict_mood_vector(features)
    
    # Print mood vector
    print(f"Song: {song['track_name']}")
    print("Mood Predictions:")
    for mood, score in zip(MOODS, mood_vector):
        print(f"  {mood:10s}: {score:.3f}")
    
    # Test gradient scoring at alpha = 1, 0.5, 0
    for alpha in [1.0, 0.5, 0.0]:
        blended_score = mood_service.score_song(features, start_idx, end_idx, alpha)
        print(f"  Gradient Score (alpha={alpha}): {blended_score:.3f}")
    
    print("-" * 40)

print("\nDemo complete! If all scores are in [0,1] and vary across moods, the network setup works.")