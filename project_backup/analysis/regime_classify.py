import json
from pathlib import Path

snap = Path("data/snapshots")
feature_files = (
    sorted(snap.glob("regime_features_*.json")) or
    sorted(snap.glob("regime_features.json"))
)
out_path = snap / "regime.json"

if not feature_files:
    neutral = {"regime": "neutral"}
    json.dump(neutral, open(out_path, "w"), indent=2)
    print("Neutral regime classified")
    exit()

features = json.load(open(feature_files[-1]))
mpi = features.get("market_pressure_index", 0.0)
n = features.get("num_narratives", 0)

if mpi > 0.3 and n >= 2:
    regime = "momentum"
elif mpi > 0.1:
    regime = "trending"
elif n == 0:
    regime = "quiet"
else:
    regime = "building"

json.dump({"regime": regime}, open(out_path, "w"), indent=2)
print(f"Regime classified: {regime}")