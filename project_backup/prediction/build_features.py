# READ-ONLY PREDICTION LAYER
# Builds snapshot-level features from narrative outputs

import json
from pathlib import Path
import numpy as np

snap = Path("data/snapshots")

def latest(p):
    files = sorted(snap.glob(p))
    if not files:
        raise FileNotFoundError(p)
    return files[-1]

market = json.load(open(latest("market_index_*.json")))
conf = json.load(open(latest("confidence_*.json")))

features = {
    "market_pressure_index": market.get("market_pressure_index", 0.0),
    "num_narratives": len(market.get("clusters", [])),
    "max_cluster_pressure": max([c["pressure"] for c in market.get("clusters", [])], default=0.0),
    "mean_confidence": float(np.mean([c["confidence"] for c in conf])) if conf else 0.0
}

out = snap / "prediction_features.json"
json.dump(features, open(out, "w"), indent=2)
print("Saved prediction_features.json")
