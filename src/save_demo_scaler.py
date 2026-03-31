import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from joblib import dump

# -----------------------
# Dummy training features
# -----------------------
INPUT_DIM = 9
num_samples = 100
X = np.random.rand(num_samples, INPUT_DIM)  # same shape as training features

# -----------------------
# Fit scaler
# -----------------------
scaler = MinMaxScaler()
scaler.fit(X)

# -----------------------
# Save scaler
# -----------------------
SCALER_PATH = "src/models/feature_scaler.pkl"
os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
dump(scaler, SCALER_PATH)
print(f"Scaler saved to {SCALER_PATH}")