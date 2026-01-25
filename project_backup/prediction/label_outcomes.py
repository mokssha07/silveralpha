# READ-ONLY PREDICTION LAYER
# Attaches future outcome labels to snapshot features

import json
from pathlib import Path

snap = Path("data/snapshots")

features_path = snap / "prediction_features.json"
labels_path = snap / "prediction_labeled.json"

# Placeholder price input (hackathon-safe)
# Replace with real returns later without changing logic
FUTURE_RETURN = 0.012  # +1.2% example
THRESHOLD = 0.01       # 1% move

with open(features_path, "r") as f:
    features = json.load(f)

label = 1 if abs(FUTURE_RETURN) > THRESHOLD else 0

features["label"] = label

with open(labels_path, "w") as f:
    json.dump(features, f, indent=2)

print("Saved prediction_labeled.json")
