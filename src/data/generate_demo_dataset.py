import numpy as np
import pandas as pd

OUTPUT_PATH = "src/data/demo_dataset.csv"

np.random.seed(42)

NUM_SAMPLES = 2000

def generate_song():
    return {
        "danceability": np.random.uniform(0, 1),
        "energy": np.random.uniform(0, 1),
        "loudness": np.random.uniform(-60, 0),
        "speechiness": np.random.uniform(0, 1),
        "acousticness": np.random.uniform(0, 1),
        "instrumentalness": np.random.uniform(0, 1),
        "liveness": np.random.uniform(0, 1),
        "valence": np.random.uniform(0, 1),
        "tempo": np.random.uniform(60, 200),
    }

def assign_moods(song):
    # Heuristic-based "realistic" mood mapping
    energy = song["energy"]
    valence = song["valence"]
    acoustic = song["acousticness"]
    dance = song["danceability"]

    return {
        "calm": float(acoustic > 0.6 and energy < 0.4),
        "energetic": energy,
        "happy": valence,
        "sad": 1 - valence,
        "dark": float(valence < 0.3 and energy < 0.5),
        "romantic": float(valence > 0.6 and acoustic > 0.4),
        "focus": float(song["instrumentalness"] > 0.5),
        "hype": float(energy > 0.7 and dance > 0.6),
    }

data = []

for _ in range(NUM_SAMPLES):
    song = generate_song()
    moods = assign_moods(song)
    data.append({**song, **moods})

df = pd.DataFrame(data)
df.to_csv(OUTPUT_PATH, index=False)

print(f"Demo dataset saved to {OUTPUT_PATH}")