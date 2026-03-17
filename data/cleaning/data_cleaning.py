import pandas as pd
df = pd.read_csv("data/eda/dataset.csv")

# Give explicit a numeric type for modeling, and encode genres as numeric IDs
df['explicit'] = df['explicit'].astype(int)
unique_genres = sorted(df['track_genre'].unique())
genre_to_index = {genre: idx for idx, genre in enumerate(unique_genres)}
print(genre_to_index)
df['genre_id'] = df['track_genre'].map(genre_to_index)
print(df.head())
print(df.shape)

# Drop rows with invalid values (likely data errors) 
df = df[(df['duration_ms'] > 0) & (df['tempo'] > 0) & (df['time_signature'] > 0)]
df = df.drop(columns=['Unnamed: 0'])
df = df.dropna(subset=['artists', 'album_name', 'track_name'])

#drop duplicated rows
df = df.drop_duplicates()
print(df.shape)


#Examine features normalization needs 
print(df['valence'].describe())
print(df['energy'].describe())
print(df['tempo'].describe())
print(df['loudness'].describe())

#normalize tempo and loudness to min-max scale similar to valence and energy
for col in ['tempo', 'loudness']:
    min_val = df[col].min()
    max_val = df[col].max()
    df[f'{col}_normalized'] = (df[col] - min_val) / (max_val - min_val)
print(df[['tempo_normalized', 'loudness_normalized']].describe())
print(df[['tempo', 'tempo_normalized', 'loudness', 'loudness_normalized']].head())
print(df.shape)

#extra mood features derived from existing features
df['mood_score'] = (df['valence'] + df['energy']) / 2
print(df['mood_score'].describe())
df['transition_score'] = (df['danceability'] + df['tempo_normalized'] + df['loudness_normalized']) / 3
print(df['transition_score'].describe())

print(df.shape)
df.to_csv('data/cleaning/cleaned_dataset.csv', index=False)


