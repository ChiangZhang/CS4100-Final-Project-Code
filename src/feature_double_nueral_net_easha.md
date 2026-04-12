#### including this file to summarize the changes I've made in this branch, and how the double nueral network
#### can be used in the rest of the code
# NOTE: changes have been made to this implementation


## Files Added

### 1. src/data/generate_demo_dataset.py
- Generates a synthetic dataset of songs with audio features
- Assigns realistic mood labels using heuristic rules
- Outputs: demo_dataset.csv

### 2. src/train_mood_model.py
- Trains a 2-layer neural network (MoodNet)
- Uses dataset features as input and mood labels as targets
- Saves:
  - Trained model → src/models/mood_model.pt
  - Feature scaler → src/models/feature_scaler.pkl

### 3. src/features/feature_builder.py
- Converts a song into a normalized feature vector
- Applies saved scaler for consistency with training data

### 4. src/services/mood_service.py
- Loads trained model
- Runs inference to produce mood scores for a song

### 5. tests/demo_manual_test.py
- End-to-end test script
- Inputs sample songs
- Outputs mood predictions and gradient scores

## Model Architecture

- Input: 9 audio features
- Hidden Layer: Fully connected (ReLU)
- Output Layer: 8 mood scores (Sigmoid)

## How to Use the Mood Classifier

### Step 1: Build Features
features = build_single_feature(song_dict)

### Step 2: Get Mood Scores
scores = mood_service.predict(features)

### Step 3: Use in Playlist Algorithm
Each song receives:
score = alpha * start_mood_score + (1 - alpha) * end_mood_score
- alpha = position in playlist (1 → start, 0 → end)
- Songs are ranked based on closeness to this score

## Summary
This system:
1. Learns mood representations from audio features
2. Assigns multi-dimensional mood scores to songs
3. Enables smooth interpolation between moods for playlist generation