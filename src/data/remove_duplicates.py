import pandas as pd


FEATURES_PATH = "src/data/validation_5k_labeled.csv"
features = pd.read_csv(FEATURES_PATH)

print(f"Original row count: {len(features)}")

# 2. SHUFFLE the dataset
# frac=1 means shuffle 100% of the data
# random_state=42 ensures you can reproduce this exact shuffle later if needed
features_shuffled = features.sample(frac=1, random_state=42).reset_index(drop=True)

# 3. Deduplicate by track_id
# Now 'keep=first' picks a random genre for each song because the list is shuffled
features_unique = features_shuffled.drop_duplicates(subset=['track_id'], keep='first')

# 4. Save the "Unbiased" unique file
UNIQUE_PATH = "src/data/labeled_batch1_unique.csv"
features_unique.to_csv(UNIQUE_PATH, index=False)

print("-" * 30)
print(f"Deduplicated count: {len(features_unique)}")
print(f"Alphabetical bias removed via shuffling.")
print(f"Successfully saved to: {UNIQUE_PATH}")
print("-" * 30)