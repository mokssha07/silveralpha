import json
from pathlib import Path

snap = Path("data/snapshots")
market_files = sorted(
    [path for path in snap.glob("market_index_*.json") if not path.stem.endswith("_latest")] or list(snap.glob("market_index_*.json")),
    key=lambda path: path.stat().st_mtime
)
confidence_files = sorted(snap.glob("confidence_adj_*.json"), key=lambda path: path.stat().st_mtime)
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
pressures = [
    c.get("final_pressure", c.get("pressure", 0))
    for c in market.get("clusters", [])
]
total_abs_pressure = sum(abs(p) for p in pressures)

features = {
    "num_narratives": num_narratives,
    "mean_confidence": confidence.get("confidence", 0.5),
    "max_cluster_pressure": max([abs(p) for p in pressures], default=0.0),
    "mean_cluster_pressure": round(sum(pressures) / len(pressures), 3) if pressures else 0.0,
    "bullish_share": round(sum(1 for p in pressures if p > 0) / len(pressures), 3) if pressures else 0.0,
    "bearish_share": round(sum(1 for p in pressures if p < 0) / len(pressures), 3) if pressures else 0.0,
    "total_abs_pressure": round(total_abs_pressure, 3),
    "market_pressure_index": round(base_mpi, 3)
}

json.dump(features, open(out_path, "w"), indent=2)
print("Regime features extracted")
