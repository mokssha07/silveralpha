import json
from pathlib import Path

snap = Path("data/snapshots")

pressure_files = sorted(snap.glob("final_pressure_*.json"))
out_path = snap / "narrative_conflict.json"

if not pressure_files:
    neutral = {
        "conflict": False,
        "reason": "no_pressure_data"
    }
    json.dump(neutral, open(out_path, "w"), indent=2)
    print("No narrative conflict (no pressure data)")
    exit()

pressure = json.load(open(pressure_files[-1]))

bullish = sum(1 for c in pressure if c.get("direction") == "Bullish")
bearish = sum(1 for c in pressure if c.get("direction") == "Bearish")

conflict = bullish > 0 and bearish > 0

result = {
    "conflict": conflict,
    "bullish_count": bullish,
    "bearish_count": bearish
}

json.dump(result, open(out_path, "w"), indent=2)
print("Narrative conflict assessed")