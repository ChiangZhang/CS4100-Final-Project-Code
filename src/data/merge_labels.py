import pandas as pd
import os

FEATURES_PATH = "src/data/cleaned_dataset_unique.csv"
BATCH1_PATH = "src/data/labeled_batch1_unique.csv"
BATCH2_PATH = "src/data/validation_5k_batch2.csv"
OUTPUT_PATH = "src/data/v2_training_dataset.csv"

print("Loading features and labels...")
b1 = pd.read_csv(BATCH1_PATH)
b2 = pd.read_csv(BATCH2_PATH)
features = pd.read_csv(FEATURES_PATH)

all_labels = pd.concat([b1, b2]).drop_duplicates(subset=['track_id'])

MOOD_COLS = [
    "calm", "happy", "energetic", "sad",
    "dark", "romantic", "focus", "hype"
]

final_train = pd.merge(
    features,
    all_labels[['track_id'] + MOOD_COLS],
    on='track_id',
    how='inner'
)

final_train = final_train.sample(frac=1, random_state=42).reset_index(drop=True)

final_train.to_csv(OUTPUT_PATH, index=False)

print("-" * 30)
print(f"SUCCESS: Created {OUTPUT_PATH}")
print(f"Total Training Samples: {len(final_train)}")
print(f"Total Input Features: {final_train.shape[1]}")
print("-" * 30)