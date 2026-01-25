import json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression

snap = Path("data/snapshots")
mem_path = snap / "prediction_memory.json"
trust_path = snap / "regime_trust.json"

NEUTRAL_PROBA = 0.48
MIN_SAMPLES = 8

if not mem_path.exists():
    json.dump([], open(mem_path, "w"))

memory = json.load(open(mem_path))

signal_trust = 0.5
if trust_path.exists():
    signal_trust = json.load(open(trust_path)).get("signal_trust", 0.5)

labels = [r.get("label") for r in memory if "label" in r]
use_model = (
    len(memory) >= MIN_SAMPLES and
    len(set(labels)) >= 2
)

if not use_model:
    run_count = len(memory)
    base_drift = np.random.uniform(-0.08, 0.08)
    cumulative_drift = base_drift * min(run_count / 10, 1.0)
    
    adjusted_proba = 0.5 + (NEUTRAL_PROBA - 0.5) * signal_trust + cumulative_drift
    adjusted_proba = max(0.2, min(0.8, adjusted_proba))
    adjusted_proba = round(float(adjusted_proba), 3)
    
    record = {
        "predicted_proba": adjusted_proba
    }
    memory.append(record)
    json.dump(memory, open(mem_path, "w"), indent=2)
    print(f"Predicted probability of meaningful move: {adjusted_proba}")
    exit()

X, y = [], []
for r in memory:
    if "label" not in r:
        continue
    X.append([
        r["market_pressure_index"],
        r["num_narratives"],
        r["max_cluster_pressure"],
        r["mean_confidence"],
    ])
    y.append(r["label"])

X = np.array(X)
y = np.array(y)

model = LogisticRegression()
model.fit(X, y)

latest = memory[-1]
latest_X = np.array([[
    latest["market_pressure_index"],
    latest["num_narratives"],
    latest["max_cluster_pressure"],
    latest["mean_confidence"],
]])

raw_proba = model.predict_proba(latest_X)[0][1]
adjusted_proba = 0.5 + (raw_proba - 0.5) * signal_trust
adjusted_proba = max(0.01, min(0.99, adjusted_proba))
adjusted_proba = round(float(adjusted_proba), 3)

latest["predicted_proba"] = adjusted_proba
json.dump(memory, open(mem_path, "w"), indent=2)
print(f"Predicted probability of meaningful move: {adjusted_proba}")