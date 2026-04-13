## CAN PROBS DELETE THIS LATER

# for manual testing

import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from joblib import dump

INPUT_DIM = 9
num_samples = 100
X = np.random.rand(num_samples, INPUT_DIM)

scaler = MinMaxScaler()
scaler.fit(X)

SCALER_PATH = "src/models/feature_scaler.pkl"
os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
dump(scaler, SCALER_PATH)
print(f"Scaler saved to {SCALER_PATH}")