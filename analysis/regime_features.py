import json
from pathlib import Path

snap = Path("data/snapshots")
market_files = sorted(snap.glob("market_index_*.json"))
confidence_files = sorted(snap.glob("confidence_adj_*.json"))
out_path = snap / "regime_features_neutral.json"

if not market_files or not confidence_files:
    neutral = {
        "num_narratives": 0,
        "mean_confidence": 0.5,
        "max_cluster_pressure": 0.0,
        "market_pressure_index": 0.0
    }
    json.dump(neutral, open(out_path, "w"), indent=2)
    print("Neutral regime features written")
    exit()

market = json.load(open(market_files[-1]))
confidence = json.load(open(confidence_files[-1]))

num_narratives = len(market.get("clusters", []))
base_mpi = market.get("market_pressure_index", 0.0)

if base_mpi < 0.15 and num_narratives > 0:
    base_mpi = 0.15 + (num_narratives * 0.05)

features = {
    "num_narratives": num_narratives,
    "mean_confidence": confidence.get("confidence", 0.5),
    "max_cluster_pressure": max(
        [c.get("pressure", 0) for c in market.get("clusters", [])],
        default=0.0
    ),
    "market_pressure_index": round(base_mpi, 3)
}

json.dump(features, open(out_path, "w"), indent=2)
print("Regime features extracted")