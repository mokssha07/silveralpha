# READ-ONLY PREDICTION LAYER
# Simple sanity checks for the predictor

import json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression

snap = Path("data/snapshots")
memory = json.load(open(snap / "prediction_memory.json"))

X, y = [], []
for r in memory:
    X.append([r["market_pressure_index"], r["num_narratives"], r["max_cluster_pressure"], r["mean_confidence"]])
    y.append(r["label"])

X, y = np.array(X), np.array(y)

print("Samples:", len(y))
print("Positive rate:", y.mean() if len(y) else 0)

if len(set(y)) > 1:
    m = LogisticRegression().fit(X, y)
    print("Coefficients:", dict(zip(
        ["market_pressure_index","num_narratives","max_cluster_pressure","mean_confidence"],
        m.coef_[0]
    )))
else:
    print("Not enough label diversity to evaluate yet.")
