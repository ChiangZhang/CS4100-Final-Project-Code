import pandas as pd

# Load the first batch
LABELS_PATH = "src/data/validation_5k_batch2.csv"
df = pd.read_csv(LABELS_PATH)

# Count duplicates
total_rows = len(df)
unique_tracks = df['track_id'].nunique()
duplicate_count = total_rows - unique_tracks

print("-" * 30)
print(f"Batch 1 Analysis:")
print(f"Total Rows: {total_rows}")
print(f"Unique Tracks: {unique_tracks}")
print(f"Duplicate Rows Found: {duplicate_count}")

if duplicate_count > 0:
    print("\nSample of duplicates:")
    print(df[df.duplicated(subset=['track_id'], keep=False)].sort_values(by='track_id').head(6))
print("-" * 30)