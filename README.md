# Mood-Based Playlist Generator

A machine learning + optimization system that generates emotionally gradient playlists by modeling songs as multi-dimensional mood vectors and optimizing transitions between them to reach a target mood.

## Project Overview

This project builds a system that generates playlists that transition smoothly between emotional states (moods) such as *happy, calm, energetic, sad,* and more.

It combines:
- A **neural network model (MoodNet)** for predicting song mood from audio features
- A **hybrid optimization hill climbing algorithm** for constructing smooth mood-progressing playlists

The project is designed to go beyond traditional recommendation systems that rely only on genre or listening history.


## Problem Statement

Most existing music recommendation systems:
- Focus on **genre similarity or user history**
- Assume a **static user mood**
- Do not support **emotional transitions over time**

This project addresses that gap by generating playlists that guide users through a **controlled mood progression**.


## System Architecture

### 1. Mood Prediction Model (Machine Learning)

A **double neural network (MoodNet)** is used to predict mood intensities for each song.

#### Key Features:
- Input: normalized audio features
  - tempo, energy, valence, acousticness, speechiness, etc.
- Output: multi-label mood vector
  - calm, happy, energetic, sad, dark, romantic, focus, hype

#### Training Strategy:
- 5-Fold Cross Validation for robustness
- Trained on ~10,000 labeled songs (Kaggle dataset)
- Used to predict moods for a larger dataset (~100,000+ songs)

#### Libraries:
- PyTorch
- NumPy
- Pandas
- scikit-learn


### 2. Playlist Optimization Engine

A hybrid search algorithm constructs playlists that smoothly transition moods.

#### Techniques Used:
- Hill Climbing (local optimization)
- Simulated Annealing (escape local minima)
- Random Restart (avoid stagnation)
- Random Initialization

#### Process:
1. Start with a random playlist
2. Iteratively replace songs with neighbors
3. Accept improvements or probabilistically accept worse solutions
4. Restart if stagnation occurs


## Scoring Function

Each playlist is evaluated using a weighted objective function:

### 1. Expected Mood Deviation (75%)
- Ensures target mood increases smoothly from start to end
- Encourages linear emotional progression

### 2. Smoothness Constraint (25%)
- Penalizes abrupt changes in non-target moods
- Ensures transitions between songs feel natural

**Goal:** Minimize total score (lower = better playlist)

## Evaluation & Visualization

The system includes multiple evaluation metrics:

- K-Fold Validation MSE (model performance stability)
- Training loss curves (neural network convergence)
- Prediction vs Ground Truth scatter plots
- Playlist mood progression visualization
- Optimization score convergence over iterations


## Technologies Used

### Machine Learning
- PyTorch (neural network training)
- scikit-learn (KFold, StandardScaler)

### Data Processing
- Pandas
- NumPy

### Visualization
- Matplotlib

### Optimization
- Custom implementation of:
  - Hill Climbing
  - Simulated Annealing
  - Random Restart strategy
