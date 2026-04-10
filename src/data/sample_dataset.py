import pandas as pd

# Load everything
all_data = pd.read_csv('src/data/cleaned_dataset.csv')
already_labeled = pd.read_csv('src/data/validation_5k_labeled.csv')

# Filter out the IDs you already finished
unlabeled_mask = ~all_data['track_id'].isin(already_labeled['track_id'])
unlabeled_pool = all_data[unlabeled_mask]

# Shuffle the remaining 108k songs
# Grab the next 5,000
next_batch = unlabeled_pool.sample(n=5000, random_state=42)

print(f"New batch selected. Unique genres: {next_batch['track_genre'].nunique()}")
next_batch.to_csv('src/data/next_batch_5k.csv', index=False)