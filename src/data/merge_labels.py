import pandas as pd
import os

FEATURES_PATH = "src/data/cleaned_dataset.csv"
LABELS_PATH = "src/data/validation_5k_labeled.csv"
OUTPUT_PATH = "src/data/v1_training_dataset.csv"

print("Loading features and labels...")
features = pd.read_csv(FEATURES_PATH)
labels = pd.read_csv(LABELS_PATH)

MOOD_COLS = [
    "calm", "happy", "energetic", "sad",
    "dark", "romantic", "focus", "hype"
]

v1_train = pd.merge(
    features,
    labels[['track_id'] + MOOD_COLS],
    on='track_id',
    how='inner'
)

v1_train = v1_train.sample(frac=1, random_state=42).reset_index(drop=True)

v1_train.to_csv(OUTPUT_PATH, index=False)

print("-" * 30)
print(f"SUCCESS: Created {OUTPUT_PATH}")
print(f"Total Training Samples: {len(v1_train)}")
print(f"Total Input Features: {v1_train.shape[1]}")
print("-" * 30)