import pandas as pd
labels = pd.read_csv('src/data/validation_5k_labeled.csv')
features = pd.read_csv('data/eda/dataset.csv') # Use the raw file to check genres

# Merge briefly to see the genre spread
check_df = pd.merge(labels[['track_id']], features[['track_id', 'track_genre']], on='track_id')
print(check_df['track_genre'].value_counts())
print(f"Unique genres in training set: {check_df['track_genre'].nunique()}")