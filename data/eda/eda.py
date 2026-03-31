import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import kagglehub
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Download latest version
path = kagglehub.dataset_download("maharshipandya/-spotify-tracks-dataset")

print("Path to dataset files:", path)

# EDA should address the following:
#   Which features correlate with mood (especially valence, energy, tempo)
#   Which features are redundant
#   Which features are most useful for similarity + transitions
#   Whether you can cluster songs into moods


# Load dataset
df = pd.read_csv("data/eda/dataset.csv")

# Basic data overview 
print("Shape:", df.shape)
print("\nColumns:\n", df.columns)
print("\nData Types:\n", df.dtypes)
print("\nMissing Values:\n", df.isnull().sum())

# Clean data a little
df['explicit'] = df['explicit'].astype(int)

# Drop non-numeric columns just for correlation analysis
non_numeric = ['track_id', 'artists', 'album_name', 'track_name', 'track_genre']
numeric_df = df.drop(columns=non_numeric)

# List just the numeric stats
print("\nSummary Statistics:\n", numeric_df.describe())

# make correlation matrix
corr = numeric_df.corr()

plt.figure(figsize=(12, 10))
plt.imshow(corr, interpolation='nearest')
plt.colorbar()
plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
plt.yticks(range(len(corr.columns)), corr.columns)
plt.title("Feature Correlation Matrix")
plt.show()

# Print top correlations with valence (mood proxy)
print("\nTop correlations with VALENCE (mood):")
print(corr['valence'].sort_values(ascending=False))

# feature distributions
features = ['danceability', 'energy', 'valence', 'tempo', 'acousticness']

for feature in features:
    plt.figure()
    plt.hist(df[feature], bins=50)
    plt.title(f"Distribution of {feature}")
    plt.xlabel(feature)
    plt.ylabel("Count")
    plt.show()

# finding scatter relationships for mood
plt.figure()
plt.scatter(df['energy'], df['valence'], alpha=0.3)
plt.xlabel("Energy")
plt.ylabel("Valence")
plt.title("Energy vs Valence (Mood Space)")
plt.show()

plt.figure()
plt.scatter(df['danceability'], df['valence'], alpha=0.3)
plt.xlabel("Danceability")
plt.ylabel("Valence")
plt.title("Danceability vs Valence")
plt.show()

# analyzing genres
genre_counts = df['track_genre'].value_counts().head(10)
print("\nTop Genres:\n", genre_counts)

plt.figure()
genre_counts.plot(kind='bar')
plt.title("Top 10 Genres")
plt.ylabel("Count")
plt.show()

# clustering:
#   select key features for mood clustering
features_for_clustering = [
    'danceability', 'energy', 'valence', 
    'tempo', 'acousticness', 'loudness'
]

X = df[features_for_clustering]

# normalize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# KMeans
kmeans = KMeans(n_clusters=4, random_state=42)
df['mood_cluster'] = kmeans.fit_predict(X_scaled)

# plot clusters
plt.figure()
plt.scatter(df['energy'], df['valence'], c=df['mood_cluster'], alpha=0.3)
plt.xlabel("Energy")
plt.ylabel("Valence")
plt.title("Mood Clusters (Energy vs Valence)")
plt.show()

# importance of features
# Correlation with valence + energy combined
df['mood_score'] = (df['valence'] + df['energy']) / 2

print("\nCorrelation with MOOD SCORE:")
numeric_df['mood_score'] = (df['valence'] + df['energy']) / 2
print(numeric_df.corr()['mood_score'].sort_values(ascending=False))