import json
from pathlib import Path

snap = Path("data/snapshots")

NEUTRAL_PROBA = 0.48

market = json.load(open(sorted(snap.glob("market_index_*.json"))[-1]))

proba = NEUTRAL_PROBA

mem_path = snap / "prediction_memory.json"
if mem_path.exists():
    memory = json.load(open(mem_path))
    if memory and "predicted_proba" in memory[-1]:
        proba = float(memory[-1]["predicted_proba"])

print("\n=== Narrative Summary ===")
print("Market Pressure Index:", market["market_pressure_index"])
print("Active Narratives:", len(market["clusters"]))

print("\n=== Prediction ===")
print(f"Probability of meaningful move: {round(proba, 3)}")
